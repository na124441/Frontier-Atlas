"""
Abstract base classes and contracts for the scraper components.
Enforces separation of concerns as required by LLD Section 3.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class IHTTPFetcher(ABC):
    """Abstract interface for HTTP fetching."""
    @abstractmethod
    async def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch URL and return dict with status_code, headers, html_content, final_url."""
        pass


class IBrowserEngine(ABC):
    """Abstract interface for browser rendering."""
    @abstractmethod
    async def fetch_rendered_page(self, url: str) -> Dict[str, Any]:
        """Render page in browser and return HTML and metadata."""
        pass


class ILLMProvider(ABC):
    """Abstract interface for LLM extraction providers."""
    @abstractmethod
    async def generate(self, prompt: str, content: str, schema: Optional[type[BaseModel]] = None) -> Dict[str, Any]:
        """Generate structured extraction matching schema."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider availability."""
        pass


class IEntityResolver(ABC):
    """Abstract interface for entity resolution."""
    @abstractmethod
    def resolve_entity(self, name: str) -> str:
        """Resolve a raw company/startup name to canonical representation."""
        pass


class IDeduplicator(ABC):
    """Abstract interface for deduplication."""
    @abstractmethod
    def generate_fingerprint(self, record: Any) -> str:
        """Generate a deterministic deduplication hash/fingerprint."""
        pass

    @abstractmethod
    async def is_duplicate(self, fingerprint: str) -> bool:
        """Check if record fingerprint already exists."""
        pass
