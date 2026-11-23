"""
Google Gemini LLM Provider (Primary Provider).
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


class GeminiProvider(BaseLLMProvider):
    """Integrates with Google Gemini Flash models."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__(name="gemini", model_name=model_name, api_key=api_key)
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    async def health_check(self) -> bool:
        """Verifies API key and endpoint readiness."""
        if not self.api_key:
            return False
        try:
            url = f"{self.endpoint}?key={self.api_key}"
            payload = {"contents": [{"parts": [{"text": "ping"}]}]}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        content: str,
        schema: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """Sends extraction request to Gemini API."""
        if not self.api_key:
            raise LLMProviderError("Missing Gemini API Key", provider=self.name, is_retryable=False)

        schema_instruction = ""
        if schema:
            schema_json = json.dumps(schema.model_json_schema(), indent=2)
            schema_instruction = f"\nReturn strictly valid JSON conforming to this JSON schema:\n{schema_json}\nOutput ONLY raw JSON."

        full_prompt = f"{prompt}\n{schema_instruction}\n\nSource Content:\n{content}"

        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 429:
                        self.handle_rate_limit()
                        raise RateLimitError("Gemini rate limit exceeded (HTTP 429)")
                    elif resp.status == 413:
                        self.handle_payload_error()
                        raise PayloadTooLargeError("Gemini payload too large (HTTP 413)")
                    elif resp.status != 200:
                        err_text = await resp.text()
                        raise LLMProviderError(f"Gemini API error ({resp.status}): {err_text}", provider=self.name)

                    data = await resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise LLMProviderError("No response candidates returned by Gemini", provider=self.name)

                    part_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    clean_text = part_text.strip()
                    # Strip markdown code fences if present
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.startswith("```"):
                        clean_text = clean_text[3:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]

                    return json.loads(clean_text.strip())

        except (RateLimitError, PayloadTooLargeError):
            raise
        except json.JSONDecodeError as e:
            raise LLMProviderError(f"Gemini returned invalid JSON: {e}", provider=self.name)
        except Exception as e:
            self.failure_count += 1
            raise LLMProviderError(f"Gemini request failed: {e}", provider=self.name)
