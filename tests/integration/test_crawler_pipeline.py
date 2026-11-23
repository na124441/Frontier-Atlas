"""Integration tests for Crawler Pipeline and Rate Limiting."""
import pytest
from intelligent_scraper.crawler.rate_limiter import RateLimiter
from intelligent_scraper.crawler.async_crawler import AsyncCrawler
from intelligent_scraper.crawler.adaptive_fetcher import AdaptiveFetcher


@pytest.mark.asyncio
async def test_rate_limiter_throttling():
    limiter = RateLimiter(default_delay=0.1)
    import time
    start = time.monotonic()
    await limiter.acquire("https://api.github.com/repos/openai/evals")
    await limiter.acquire("https://api.github.com/repos/openai/whisper")
    elapsed = time.monotonic() - start
    assert elapsed >= 0.09


@pytest.mark.asyncio
async def test_crawler_concurrency_control():
    crawler = AsyncCrawler(max_concurrency=2)
    assert crawler.semaphore._value == 2
    await crawler.shutdown()
