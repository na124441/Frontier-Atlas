"""
Playwright Browser Automation Engine.
Executes client-side JavaScript for dynamic SPA pages.
Adheres to LLD Section 4.3.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.core.exceptions import BrowserRenderError
from intelligent_scraper.core.interfaces import IBrowserEngine

logger = logging.getLogger(__name__)


class BrowserEngine(IBrowserEngine):
    """Manages headless browser instances via Playwright Async API."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.playwright = None
        self.browser = None
        self._lock = asyncio.Lock()
        self.is_available = True

    async def initialize(self) -> None:
        """Launches headless Chromium instance if available."""
        async with self._lock:
            if self.browser is not None:
                return

            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )
                logger.info("Playwright browser initialized successfully.")
            except Exception as e:
                logger.warning(f"Playwright browser initialization not available: {e}")
                self.is_available = False

    async def fetch_rendered_page(self, url: str) -> Dict[str, Any]:
        """
        Renders page in a browser context, waits for network idle / DOM content,
        and returns rendered HTML.
        """
        if not self.is_available:
            raise BrowserRenderError("Playwright browser is unavailable in this environment")

        if self.browser is None:
            await self.initialize()

        if self.browser is None:
            raise BrowserRenderError("Failed to initialize headless browser")

        context = None
        page = None
        try:
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()

            # Set timeout
            timeout_ms = self.settings.BROWSER_TIMEOUT * 1000
            page.set_default_timeout(timeout_ms)

            response = await page.goto(url, wait_until="domcontentloaded")
            # Wait for content to populate
            await asyncio.sleep(1.5)

            html = await page.content()
            status = response.status if response else 200
            final_url = page.url

            return {
                "status_code": status,
                "response_headers": response.headers if response else {},
                "html_content": html,
                "final_url": final_url,
                "rendered_via_browser": True
            }

        except Exception as e:
            logger.error(f"Browser rendering failed for {url}: {e}")
            raise BrowserRenderError(f"Browser render error for {url}: {e}")
        finally:
            if page:
                await page.close()
            if context:
                await context.close()

    async def close(self) -> None:
        """Closes browser and stops Playwright."""
        async with self._lock:
            if self.browser:
                try:
                    await self.browser.close()
                except Exception:
                    pass
                self.browser = None
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception:
                    pass
                self.playwright = None
