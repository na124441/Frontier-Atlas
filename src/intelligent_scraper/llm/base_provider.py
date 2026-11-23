"""
Base LLM Provider Interface.
Adheres to LLD Section 6.2.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel


class BaseLLMProvider(ABC):
    """Abstract provider interface for all LLM backends."""

    def __init__(self, name: str, model_name: str, api_key: str):
        self.name = name
        self.model_name = model_name
        self.api_key = api_key
        self.failure_count = 0
        self.is_available = bool(api_key)

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        content: str,
        schema: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """
        Executes LLM completion and returns parsed structured JSON dictionary.
        Must handle schema adherence and clean JSON parsing.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if provider endpoint and credentials are operational."""
        pass

    def handle_rate_limit(self, retry_after: Optional[float] = None) -> float:
        """Calculates delay on rate limit encounter."""
        self.failure_count += 1
        return retry_after if retry_after and retry_after > 0 else 5.0

    def handle_payload_error(self) -> None:
        """Records payload too large (413) event."""
        self.failure_count += 1
