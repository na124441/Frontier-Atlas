"""
Model Router and Fallback Chain.
Routes requests across primary (Gemini Flash), secondary (Groq Llama),
and tertiary (DeepSeek) providers with rate limit backoff and error recovery.
Adheres to SRS FR-09, FR-11 and LLD Section 6.4.
"""

import asyncio
import logging
import random
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.core.exceptions import LLMProviderError, RateLimitError, PayloadTooLargeError
from intelligent_scraper.llm.base_provider import BaseLLMProvider
from intelligent_scraper.llm.gemini_provider import GeminiProvider
from intelligent_scraper.llm.groq_provider import GroqProvider
from intelligent_scraper.llm.deepseek_provider import DeepSeekProvider
from intelligent_scraper.llm.mock_provider import MockProvider

logger = logging.getLogger(__name__)


class ModelRouter:
    """Orchestrates LLM calls across multiple providers with fallback and retry logic."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._init_providers()
        self.priority_order: List[str] = list(self.settings.LLM_PROVIDER_PRIORITY)
        self.provider_failure_counts: Dict[str, int] = {k: 0 for k in self.priority_order}

    def _init_providers(self) -> None:
        """Initializes configured providers."""
        self.providers["gemini"] = GeminiProvider(
            api_key=self.settings.GEMINI_API_KEY,
            model_name=self.settings.GEMINI_MODEL
        )
        self.providers["groq"] = GroqProvider(
            api_key=self.settings.GROQ_API_KEY,
            model_name=self.settings.GROQ_MODEL
        )
        self.providers["deepseek"] = DeepSeekProvider(
            api_key=self.settings.DEEPSEEK_API_KEY,
            model_name=self.settings.DEEPSEEK_MODEL
        )
        self.providers["mock"] = MockProvider()

    def select_provider(self, exclude: Optional[List[str]] = None) -> Optional[BaseLLMProvider]:
        """Selects highest-priority active provider that is not excluded."""
        excluded = set(exclude or [])
        for name in self.priority_order:
            if name not in excluded and name in self.providers:
                prov = self.providers[name]
                if prov.is_available:
                    return prov

        # If all configured external providers fail or lack keys, fallback to mock in dev/test
        if "mock" not in excluded:
            return self.providers["mock"]

        return None

    def record_provider_failure(self, provider_name: str) -> None:
        """Increments failure count and temporarily deprioritizes failing provider."""
        self.provider_failure_counts[provider_name] = self.provider_failure_counts.get(provider_name, 0) + 1
        logger.warning(
            f"Provider {provider_name} recorded failure #{self.provider_failure_counts[provider_name]}"
        )

    async def execute_request(
        self,
        prompt: str,
        content: str,
        schema: Optional[Type[BaseModel]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Executes request through provider fallback chain:
        Gemini -> Groq -> DeepSeek -> Mock
        Handles rate limits with exponential backoff and jitter.
        """
        attempted_providers: List[str] = []

        while len(attempted_providers) < len(self.providers):
            provider = self.select_provider(exclude=attempted_providers)
            if not provider:
                break

            provider_name = provider.name
            attempted_providers.append(provider_name)

            for retry in range(max_retries):
                try:
                    logger.info(f"Attempting extraction using {provider_name} (retry={retry})")
                    result = await provider.generate(prompt=prompt, content=content, schema=schema)
                    return result

                except RateLimitError as e:
                    # Exponential backoff with randomized jitter
                    delay = min(self.settings.BACKOFF_MAX_SECONDS, (2 ** retry) * self.settings.BACKOFF_BASE_SECONDS)
                    jitter = random.uniform(0.1, 1.0)
                    total_delay = delay + jitter
                    logger.warning(f"Rate limit on {provider_name}: backing off for {total_delay:.2f}s")
                    await asyncio.sleep(total_delay)
                    # If last retry, break out to fallback provider
                    if retry == max_retries - 1:
                        self.record_provider_failure(provider_name)

                except PayloadTooLargeError:
                    # Reraise so chunker can handle payload reduction
                    logger.warning(f"Payload too large (413) on {provider_name}")
                    raise

                except LLMProviderError as e:
                    logger.error(f"Error on {provider_name}: {e.message}")
                    self.record_provider_failure(provider_name)
                    if not e.is_retryable:
                        break  # Fallback to next provider immediately

                except Exception as e:
                    logger.error(f"Unexpected error with {provider_name}: {e}")
                    self.record_provider_failure(provider_name)
                    break

        raise LLMProviderError("All LLM providers in fallback chain exhausted", provider="chain", is_retryable=False)
