"""
Adaptive Web Fetcher.
Dynamically decides whether to use fast HTTP fetching or headless browser rendering.
Adheres to SRS FR-03 and LLD Section 4.4.
"""

import re
import logging
from typing import Any, Dict, Optional
from intelligent_scraper.crawler.http_fetcher import HTTPFetcher
from intelligent_scraper.crawler.browser_engine import BrowserEngine
from intelligent_scraper.crawler.rate_limiter import RateLimiter
from intelligent_scraper.core.exceptions import (
    NetworkFetchError, RateLimitError, ResourceNotFoundError,
    AccessRestrictedError, BrowserRenderError
)

logger = logging.getLogger(__name__)


class AdaptiveFetcher:
    """Intelligently routes requests to HTTP fetcher or headless browser based on page characteristics."""

    # Heuristic patterns indicating JavaScript client-side rendering is required
    JS_REQUIRED_PATTERNS = [
        re.compile(r'<noscript>.*?enable javascript.*?</noscript>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<div\s+id=[\'"](?:app|root|__next|__nuxt)[\'"]>\s*</div>', re.IGNORECASE),
        re.compile(r'You need to enable JavaScript to run this app', re.IGNORECASE),
        re.compile(r'loading\.\.\.', re.IGNORECASE),
    ]

    def __init__(
        self,
        http_fetcher: Optional[HTTPFetcher] = None,
        browser_engine: Optional[BrowserEngine] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.http_fetcher = http_fetcher or HTTPFetcher()
        self.browser_engine = browser_engine or BrowserEngine()
        self.rate_limiter = rate_limiter or RateLimiter()

    def requires_browser_rendering(self, html: str, source_config: Optional[Dict[str, Any]] = None) -> bool:
        """Determines if HTML is an unrendered JavaScript shell."""
        if source_config and source_config.get("strategy") == "browser":
            return True

        if not html:
            return True

        # Check for explicit JS requirement banners
        for pat in self.JS_REQUIRED_PATTERNS:
            if pat.search(html):
                return True

        # Check text density: very short HTML (< 800 bytes) with scripts is likely a shell
        if len(html.strip()) < 800 and ("<script" in html.lower()):
            return True

        return False

    async def fetch(self, url: str, source_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes adaptive fetching strategy:
        1. Rate limit throttle.
        2. Attempt fast HTTP retrieval.
        3. Check if JavaScript rendering is needed.
        4. Fallback to Browser Engine only when required.
        """
        # Respect rate limits
        await self.rate_limiter.acquire(url)

        # Force browser if explicitly configured
        force_browser = source_config.get("strategy") == "browser" if source_config else False
        if force_browser:
            logger.info(f"Source configured for browser rendering: {url}")
            try:
                return await self.browser_engine.fetch_rendered_page(url)
            except BrowserRenderError:
                logger.warning(f"Browser rendering failed, falling back to HTTP for {url}")

        # Attempt HTTP retrieval
        try:
            http_result = await self.http_fetcher.fetch(url)

            # Check if required content is missing due to client-side JS
            if self.requires_browser_rendering(http_result.get("html_content", ""), source_config):
                logger.info(f"Detected client-rendered JavaScript shell; escalating to Playwright for: {url}")
                try:
                    browser_result = await self.browser_engine.fetch_rendered_page(url)
                    return browser_result
                except Exception as b_err:
                    logger.warning(f"Browser escalation failed ({b_err}); using initial HTTP content.")
                    return http_result

            return http_result

        except (RateLimitError, ResourceNotFoundError, AccessRestrictedError):
            # Known terminal/retry errors must not trigger blind browser rendering
            raise
        except NetworkFetchError as e:
            # If HTTP connection itself failed, try browser once if appropriate
            logger.warning(f"HTTP fetch error ({e}); attempting browser fallback.")
            try:
                return await self.browser_engine.fetch_rendered_page(url)
            except Exception:
                raise e

    async def close(self) -> None:
        """Cleans up HTTP session and browser instance."""
        await self.http_fetcher.close()
        await self.browser_engine.close()
