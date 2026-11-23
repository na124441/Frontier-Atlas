"""
Per-Domain Rate Limiter and Request Throttler.
Enforces politeness policies, backoff intervals, and host-level concurrency limits.
Adheres to SRS FR-03 and LLD Section 4.1.
"""

import asyncio
import time
from typing import Dict
from urllib.parse import urlparse


class RateLimiter:
    """Domain-level rate limiter to prevent aggressive hitting of targets."""

    def __init__(self, default_delay: float = 0.5):
        self.default_delay = default_delay
        # domain -> last request timestamp
        self._last_request_times: Dict[str, float] = {}
        # domain -> lock to synchronize requests per domain
        self._domain_locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def _get_lock(self, domain: str) -> asyncio.Lock:
        """Retrieves or creates asyncio.Lock for the domain."""
        async with self._global_lock:
            if domain not in self._domain_locks:
                self._domain_locks[domain] = asyncio.Lock()
            return self._domain_locks[domain]

    def _extract_domain(self, url: str) -> str:
        """Extracts netloc domain from URL."""
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return "default"

    async def acquire(self, url: str, custom_delay: float = None) -> None:
        """Throttles execution to honor inter-request delays for the target domain."""
        domain = self._extract_domain(url)
        lock = await self._get_lock(domain)
        delay = custom_delay if custom_delay is not None else self.default_delay

        async with lock:
            now = time.monotonic()
            last_time = self._last_request_times.get(domain, 0.0)
            elapsed = now - last_time

            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)

            self._last_request_times[domain] = time.monotonic()
