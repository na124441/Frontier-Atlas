"""
Groq LLM Provider (First Fallback).
Adheres to LLD Section 6.3.
"""

import json
import logging
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
import aiohttp
from intelligent_scraper.core.exceptions import LLMProviderError, RateLimitError, PayloadTooLargeError
from intelligent_scraper.llm.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Integrates with Groq API (Llama 3 models)."""

    def __init__(self, api_key: str, model_name: str = "llama3-70b-8192"):
        super().__init__(name="groq", model_name=model_name, api_key=api_key)
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    async def health_check(self) -> bool:
        """Verifies API connectivity."""
        if not self.api_key:
            return False
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        content: str,
        schema: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """Sends extraction request to Groq OpenAI-compatible endpoint."""
        if not self.api_key:
            raise LLMProviderError("Missing Groq API Key", provider=self.name, is_retryable=False)

        schema_instruction = ""
        if schema:
            schema_json = json.dumps(schema.model_json_schema(), indent=2)
            schema_instruction = f"\nReturn strictly valid JSON conforming to this JSON schema:\n{schema_json}\nOutput ONLY raw JSON."

        messages = [
            {"role": "system", "content": "You are a structured data extraction engine. Return only JSON matching the schema."},
            {"role": "user", "content": f"{prompt}\n{schema_instruction}\n\nSource Content:\n{content}"}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 429:
                        self.handle_rate_limit()
                        raise RateLimitError("Groq rate limit exceeded (HTTP 429)")
                    elif resp.status == 413:
                        self.handle_payload_error()
                        raise PayloadTooLargeError("Groq payload too large (HTTP 413)")
                    elif resp.status != 200:
                        err_text = await resp.text()
                        raise LLMProviderError(f"Groq API error ({resp.status}): {err_text}", provider=self.name)

                    data = await resp.json()
                    content_str = data["choices"][0]["message"]["content"]
                    clean_str = content_str.strip()
                    if clean_str.startswith("```json"):
                        clean_str = clean_str[7:]
                    if clean_str.startswith("```"):
                        clean_str = clean_str[3:]
                    if clean_str.endswith("```"):
                        clean_str = clean_str[:-3]
                    return json.loads(clean_str.strip())

        except (RateLimitError, PayloadTooLargeError):
            raise
        except json.JSONDecodeError as e:
            raise LLMProviderError(f"Groq returned invalid JSON: {e}", provider=self.name)
        except Exception as e:
            self.failure_count += 1
            raise LLMProviderError(f"Groq request failed: {e}", provider=self.name)
