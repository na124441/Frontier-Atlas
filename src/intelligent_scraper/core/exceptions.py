"""
Custom Exception Hierarchy for Intelligent Web Scraper.
Supports structured error handling as mandated by NFR-03 and SRS Section 8.
"""

from typing import Optional


class ScraperException(Exception):
    """Base exception for all scraper errors."""
    def __init__(self, message: str, task_id: Optional[str] = None, source_url: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.task_id = task_id
        self.source_url = source_url


class NetworkFetchError(ScraperException):
    """Raised when an HTTP or network fetch fails."""
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class RateLimitError(NetworkFetchError):
    """Raised on HTTP 429 rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded (HTTP 429)", retry_after: Optional[float] = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class PayloadTooLargeError(NetworkFetchError):
    """Raised on HTTP 413 payload too large."""
    def __init__(self, message: str = "Payload too large (HTTP 413)", **kwargs):
        super().__init__(message, status_code=413, **kwargs)


class ResourceNotFoundError(NetworkFetchError):
    """Raised on HTTP 404."""
    def __init__(self, message: str = "Resource not found (HTTP 404)", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class AccessRestrictedError(NetworkFetchError):
    """Raised on HTTP 403 or access restriction."""
    def __init__(self, message: str = "Access restricted (HTTP 403)", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class BrowserRenderError(ScraperException):
    """Raised when Playwright browser rendering fails."""
    pass


class ExtractionError(ScraperException):
    """Raised when content parsing or LLM extraction fails."""
    pass


class LLMProviderError(ExtractionError):
    """Raised when an LLM provider fails."""
    def __init__(self, message: str, provider: str, is_retryable: bool = True, **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.is_retryable = is_retryable


class ValidationError(ScraperException):
    """Raised when schema or semantic validation fails."""
    pass


class FreshnessError(ValidationError):
    """Raised when content violates the 24-hour freshness rule."""
    def __init__(self, message: str, published_date: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.published_date = published_date


class EntityResolutionError(ScraperException):
    """Raised when entity canonicalization encounters an unresolvable conflict."""
    pass


class DeduplicationError(ScraperException):
    """Raised when duplicate record is detected."""
    def __init__(self, message: str, fingerprint: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.fingerprint = fingerprint
