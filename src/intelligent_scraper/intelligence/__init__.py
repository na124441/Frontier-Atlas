"""Intelligence layer: date detector, freshness, entity resolution, deduplication and confidence validation."""
from intelligent_scraper.intelligence.date_detector import DateDetector
from intelligent_scraper.intelligence.freshness_validator import FreshnessValidator
from intelligent_scraper.intelligence.entity_resolver import EntityResolver
from intelligent_scraper.intelligence.deduplicator import Deduplicator
from intelligent_scraper.intelligence.confidence_validator import ConfidenceValidator

__all__ = [
    "DateDetector",
    "FreshnessValidator",
    "EntityResolver",
    "Deduplicator",
    "ConfidenceValidator",
]
