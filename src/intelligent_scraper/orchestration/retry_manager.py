"""
Retry Manager and Dead-Letter Handling.
Implements bounded exponential backoff with randomized jitter and dead-letter quarantine.
Adheres to SRS FR-11 and LLD Section 10.3.
"""

import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.core.exceptions import (
    RateLimitError, NetworkFetchError, LLMProviderError, ResourceNotFoundError, AccessRestrictedError
)

logger = logging.getLogger(__name__)


class RetryManager:
    """Calculates backoff delays and directs failed tasks to retry or dead-letter queue."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.max_retries = self.settings.MAX_RETRIES
        self.base_delay = self.settings.BACKOFF_BASE_SECONDS
        self.maximum_delay = self.settings.BACKOFF_MAX_SECONDS
        self.dead_letter_queue: List[Dict[str, Any]] = []

    def calculate_backoff(self, retry_count: int, retry_after: Optional[float] = None) -> float:
        """
        Exact backoff formula from LLD Section 10.3:
        delay = min(maximum_delay, base_delay * (2 ^ retry_count)) + random_jitter
        """
        if retry_after is not None and retry_after > 0:
            return retry_after + random.uniform(0.1, 1.0)

        exponential = self.base_delay * (2 ** retry_count)
        capped = min(self.maximum_delay, exponential)
        jitter = random.uniform(0.1, 1.0)
        return capped + jitter

    def should_retry(self, error: Exception, current_retry_count: int) -> bool:
        """
        Decides if an error qualifies for retry:
        - 404 (ResourceNotFoundError): False (permanent)
        - 403 (AccessRestrictedError): False (access restricted)
        - 429 (RateLimitError): True (transient)
        - 5xx or NetworkFetchError: True (transient network failure)
        - Non-retryable LLM provider error: False
        """
        if current_retry_count >= self.max_retries:
            return False

        if isinstance(error, ResourceNotFoundError):
            return False

        if isinstance(error, AccessRestrictedError):
            return False

        if isinstance(error, RateLimitError):
            return True

        if isinstance(error, NetworkFetchError):
            return True

        if isinstance(error, LLMProviderError):
            return error.is_retryable

        # General transient network exceptions
        return True

    def schedule_retry(self, task: Dict[str, Any], error: Exception) -> Optional[datetime]:
        """Calculates next retry timestamp."""
        retry_count = task.get("retry_count", 0)
        retry_after = getattr(error, "retry_after", None)
        delay_sec = self.calculate_backoff(retry_count, retry_after)
        return datetime.now(timezone.utc) + timedelta(seconds=delay_sec)

    def move_to_dead_letter(self, task: Dict[str, Any], error: Exception, stage: str = "unknown") -> None:
        """
        Moves exhausted or fatal tasks into the dead-letter queue.
        Preserves original URL, source info, error details, retry history, stage, and failure timestamp.
        """
        entry = {
            "task_id": task.get("task_id"),
            "url": task.get("url"),
            "source_id": task.get("source_id"),
            "source_name": task.get("source_name"),
            "error_type": error.__class__.__name__,
            "error_details": str(error),
            "retry_count": task.get("retry_count", 0),
            "processing_stage": stage,
            "failure_timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.dead_letter_queue.append(entry)
        logger.error(f"Task {task.get('task_id')} moved to dead-letter queue at stage '{stage}': {error}")
