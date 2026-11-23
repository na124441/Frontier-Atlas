"""Core interfaces, enums, exceptions and constants."""
from intelligent_scraper.core.enums import (
    RecordType, TaskStatus, SourceCategory, PricingModel, CrawlStrategy, LLMProviderName
)
from intelligent_scraper.core.exceptions import (
    ScraperException, NetworkFetchError, RateLimitError, PayloadTooLargeError,
    ResourceNotFoundError, AccessRestrictedError, BrowserRenderError,
    ExtractionError, LLMProviderError, ValidationError, FreshnessError,
    EntityResolutionError, DeduplicationError
)
from intelligent_scraper.core.constants import DEFAULT_HEADERS, FRESHNESS_WINDOW_SECONDS, SEED_STARTUPS
from intelligent_scraper.core.interfaces import (
    IHTTPFetcher, IBrowserEngine, ILLMProvider, IEntityResolver, IDeduplicator
)

__all__ = [
    "RecordType", "TaskStatus", "SourceCategory", "PricingModel", "CrawlStrategy", "LLMProviderName",
    "ScraperException", "NetworkFetchError", "RateLimitError", "PayloadTooLargeError",
    "ResourceNotFoundError", "AccessRestrictedError", "BrowserRenderError",
    "ExtractionError", "LLMProviderError", "ValidationError", "FreshnessError",
    "EntityResolutionError", "DeduplicationError",
    "DEFAULT_HEADERS", "FRESHNESS_WINDOW_SECONDS", "SEED_STARTUPS",
    "IHTTPFetcher", "IBrowserEngine", "ILLMProvider", "IEntityResolver", "IDeduplicator"
]
