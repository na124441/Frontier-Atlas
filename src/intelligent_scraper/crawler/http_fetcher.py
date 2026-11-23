"""
Asynchronous HTTP Fetcher using aiohttp.
Provides high-concurrency fetching, connection pooling, and error mapping.
Adheres to LLD Section 4.2.
"""

import aiohttp
import logging
from typing import Any, Dict, Optional
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.core.constants import DEFAULT_HEADERS
from intelligent_scraper.core.exceptions import (
    NetworkFetchError, RateLimitError, ResourceNotFoundError, AccessRestrictedError
)
from intelligent_scraper.core.interfaces import IHTTPFetcher

logger = logging.getLogger(__name__)


class HTTPFetcher(IHTTPFetcher):
    """Async HTTP fetcher reusing an aiohttp ClientSession."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """Initializes a shared aiohttp ClientSession with TCP connection pooling."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.settings.HTTP_TIMEOUT)
            connector = aiohttp.TCPConnector(
                limit=self.settings.MAX_CONCURRENT_REQUESTS,
                ttl_dns_cache=300,
                ssl=False  # Avoid strict SSL dropouts during general web extraction
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=DEFAULT_HEADERS
            )

    async def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetches webpage content via HTTP GET.
        Returns:
            status_code (int)
            response_headers (dict)
            html_content (str)
            final_url (str)
        """
        if self.session is None or self.session.closed:
            await self.initialize()

        assert self.session is not None

        try:
            async with self.session.get(url, allow_redirects=True) as resp:
                status = resp.status
                headers = dict(resp.headers)
                final_url = str(resp.url)

                if status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else 5.0
                    raise RateLimitError(f"HTTP 429 Too Many Requests for {url}", retry_after=delay, source_url=url)

                if status == 404:
                    raise ResourceNotFoundError(f"HTTP 404 Not Found: {url}", source_url=url)

                if status == 403:
                    raise AccessRestrictedError(f"HTTP 403 Forbidden: {url}", source_url=url)

                # Attempt decoding text with utf-8 fallback to latin1 or errors ignore
                try:
                    html = await resp.text(errors="replace")
                except Exception:
                    raw_bytes = await resp.read()
                    html = raw_bytes.decode("utf-8", errors="replace")

                return {
                    "status_code": status,
                    "response_headers": headers,
                    "html_content": html,
                    "final_url": final_url
                }

        except (RateLimitError, ResourceNotFoundError, AccessRestrictedError):
            raise
        except Exception as e:
            logger.warning(f"HTTP fetch failed for {url}: {e}")
            raise NetworkFetchError(f"Fetch failure for {url}: {e}", source_url=url)

    async def close(self) -> None:
        """Closes aiohttp session and releases TCP connections."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
