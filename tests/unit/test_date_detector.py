"""Unit tests for Date Detector and Freshness Validator."""
import pytest
from datetime import datetime, timezone, timedelta
from intelligent_scraper.intelligence.date_detector import DateDetector
from intelligent_scraper.intelligence.freshness_validator import FreshnessValidator


def test_date_detector_relative_parsing():
    detector = DateDetector()
    ref_time = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 2 hours ago
    dt = detector.parse_relative_date("2 hours ago", reference_time=ref_time)
    assert dt is not None
    assert dt == datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)

    # 15 mins ago
    dt_min = detector.parse_relative_date("15 mins ago", reference_time=ref_time)
    assert dt_min == datetime(2024, 6, 1, 11, 45, 0, tzinfo=timezone.utc)

    # yesterday
    dt_yest = detector.parse_relative_date("yesterday", reference_time=ref_time)
    assert dt_yest == datetime(2024, 5, 31, 12, 0, 0, tzinfo=timezone.utc)


def test_freshness_validator_window():
    validator = FreshnessValidator(max_age_seconds=86400)
    now = datetime.now(timezone.utc)

    # Fresh within 2 hours
    assert validator.is_fresh(now - timedelta(hours=2), reference_time=now)

    # Exactly 24 hours
    assert validator.is_fresh(now - timedelta(hours=24), reference_time=now)

    # Stale: 25 hours old
    assert not validator.is_fresh(now - timedelta(hours=25), reference_time=now)

    # In future (>5 mins ahead)
    valid, err = validator.validate_or_quarantine(now + timedelta(hours=2), reference_time=now)
    assert not valid
    assert "future" in err.lower()
