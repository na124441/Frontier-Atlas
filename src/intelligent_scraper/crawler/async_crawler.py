"""
Asynchronous Crawler Worker.
Coordinates concurrent task execution with bounded concurrency, rate limits, and adaptive fetching.
Adheres to SRS FR-03 and LLD Section 4.5.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.crawler.adaptive_fetcher import AdaptiveFetcher
from intelligent_scraper.core.enums import TaskStatus

logger = logging.getLogger(__name__)


class AsyncCrawler:
    """Manages concurrent crawl execution using asyncio.Semaphore."""

    def __init__(
        self,
        adaptive_fetcher: Optional[AdaptiveFetcher] = None,
        settings: Optional[Settings] = None,
        max_concurrency: Optional[int] = None
    ):
        self.settings = settings or get_settings()
        self.concurrency = max_concurrency or self.settings.MAX_CONCURRENT_REQUESTS
        self.semaphore = asyncio.Semaphore(self.concurrency)
        self.adaptive_fetcher = adaptive_fetcher or AdaptiveFetcher()
        self._is_running = True

    async def process_task(
        self,
        task: Dict[str, Any],
        on_success: Optional[Callable[[Dict[str, Any], Dict[str, Any]], Any]] = None,
        on_error: Optional[Callable[[Dict[str, Any], Exception], Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Processes an individual crawl task under semaphore control."""
        url = task.get("url")
        source_config = task.get("source_config", {})

        async with self.semaphore:
            if not self._is_running:
                return None

            try:
                logger.info(f"Crawling URL: {url}")
                result = await self.adaptive_fetcher.fetch(url, source_config)

                task["status"] = TaskStatus.COMPLETED.value
                if on_success:
                    await on_success(task, result)
                return result

            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                task["status"] = TaskStatus.FAILED.value
                task["error_message"] = str(e)
                if on_error:
                    await on_error(task, e)
                return None

    async def process_batch(
        self,
        tasks: List[Dict[str, Any]],
        on_success: Optional[Callable[[Dict[str, Any], Dict[str, Any]], Any]] = None,
        on_error: Optional[Callable[[Dict[str, Any], Exception], Any]] = None
    ) -> List[Optional[Dict[str, Any]]]:
        """Runs a batch of tasks concurrently up to configured concurrency limit."""
        coroutines = [self.process_task(t, on_success, on_error) for t in tasks]
        return await asyncio.gather(*coroutines, return_exceptions=False)

    async def shutdown(self) -> None:
        """Gracefully halts crawler execution and frees network resources."""
        self._is_running = False
        await self.adaptive_fetcher.close()
        logger.info("Async crawler shut down cleanly.")
