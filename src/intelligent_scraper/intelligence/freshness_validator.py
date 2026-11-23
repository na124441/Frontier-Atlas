"""
Freshness Validator.
Enforces the mandatory 24-hour freshness rule for news and job postings.
Adheres to SRS FR-08 and LLD Section 8.1.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
from intelligent_scraper.core.constants import FRESHNESS_WINDOW_SECONDS
from intelligent_scraper.core.exceptions import FreshnessError


class FreshnessValidator:
    """Validates publication timestamps against reference ingestion time."""

    def __init__(self, max_age_seconds: int = FRESHNESS_WINDOW_SECONDS):
        self.max_age_seconds = max_age_seconds

    def is_fresh(
        self,
        published_at: Optional[datetime],
        reference_time: Optional[datetime] = None
    ) -> bool:
        """
        Exact freshness algorithm from LLD 8.1:
        age = reference_time - published_at
        return (age.total_seconds() >= 0 and age.total_seconds() <= 86400)
        """
        if published_at is None:
            return False

        now = reference_time or datetime.now(timezone.utc)

        # Ensure both are UTC timezone-aware
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        age = now - published_at
        total_seconds = age.total_seconds()

        # Reject if in the future (>1 hour clock skew) or older than freshness window
        return 0 <= total_seconds <= self.max_age_seconds

    def validate_or_quarantine(
        self,
        published_at: Optional[datetime],
        reference_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_valid, rejection_reason).
        Records older than 24h, future without explanation, or unverifiable are rejected.
        """
        if published_at is None:
            return False, "Unverifiable freshness: missing publication timestamp"

        now = reference_time or datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        age = now - published_at
        total_seconds = age.total_seconds()

        if total_seconds < -300:  # More than 5 mins in future
            return False, f"Publication date in the future: {published_at.isoformat()}"

        if total_seconds > self.max_age_seconds:
            hours_old = total_seconds / 3600.0
            return False, f"Stale record: publication age {hours_old:.1f}h exceeds {self.max_age_seconds / 3600:.0f}h window"

        return True, None
