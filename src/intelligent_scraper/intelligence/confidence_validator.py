"""
Confidence and Quality Validator.
Ensures every extracted record passes strict field presence, source traceability,
and semantic integrity checks before being accepted.
Adheres to SRS FR-15 and LLD Section 8.4.
"""

from typing import Any, Dict, List, Optional, Tuple
from intelligent_scraper.schemas.base import BaseEntity
from intelligent_scraper.schemas.startup import StartupEntity
from intelligent_scraper.schemas.product import ProductEntity
from intelligent_scraper.schemas.research_paper import ResearchPaperEntity
from intelligent_scraper.schemas.job import JobEntity
from intelligent_scraper.schemas.news import NewsEntity


class ConfidenceValidator:
    """Validates structural and semantic validity of extracted records."""

    def validate_source_reference(self, record: Any) -> Tuple[bool, Optional[str]]:
        """Verifies that record has a legitimate, non-empty source reference."""
        source_url = None
        if hasattr(record, "source") and record.source and hasattr(record.source, "url"):
            source_url = record.source.url
        elif isinstance(record, dict) and "source" in record:
            source_url = record["source"].get("url")

        if hasattr(record, "content"):
            content = record.content
            if hasattr(content, "paper_url") and not source_url:
                source_url = content.paper_url
            elif hasattr(content, "article_url") and not source_url:
                source_url = content.article_url
            elif hasattr(content, "job_url") and not source_url:
                source_url = content.job_url

        if not source_url or not source_url.startswith(("http://", "https://")):
            return False, f"Invalid or missing source URL: {source_url}"

        return True, None

    def validate_required_fields(self, record: Any) -> Tuple[bool, Optional[str]]:
        """Ensures non-empty essential attributes per entity type."""
        if isinstance(record, StartupEntity):
            if not record.content.entityName or len(record.content.entityName.strip()) < 2:
                return False, "Startup entity missing valid entityName"

        elif isinstance(record, ProductEntity):
            if not record.content.startupName:
                return False, "Product entity missing startupName"
            if not record.content.pricingModel:
                return False, "Product entity missing pricingModel"

        elif isinstance(record, ResearchPaperEntity):
            if not record.content.title or len(record.content.title.strip()) < 4:
                return False, "Research paper missing title"
            if not record.content.paper_url:
                return False, "Research paper missing paper_url"
            if record.content.published_date is None:
                return False, "Research paper missing published_date"

        elif isinstance(record, JobEntity):
            if not record.content.company:
                return False, "Job entity missing company"
            if not record.content.role_family:
                return False, "Job entity missing role_family"
            if record.content.date is None:
                return False, "Job entity missing date"

        elif isinstance(record, NewsEntity):
            if not record.content.title:
                return False, "News entity missing title"
            if not record.content.full_text or len(record.content.full_text.strip()) < 50:
                return False, "News entity missing sufficient full_text content"
            if record.content.published_date is None:
                return False, "News entity missing published_date"

        return True, None

    def validate_cross_field_consistency(self, record: Any) -> Tuple[bool, Optional[str]]:
        """Validates cross-field consistency (e.g. employee count >= 0, github stars >= 0)."""
        if isinstance(record, StartupEntity):
            if record.content.employeeCount is not None and record.content.employeeCount < 0:
                return False, "Employee count cannot be negative"

        elif isinstance(record, ResearchPaperEntity):
            if record.content.github_stars is not None and record.content.github_stars < 0:
                return False, "GitHub stars count cannot be negative"
            if record.content.github_url and not ("github.com" in record.content.github_url):
                return False, "Invalid GitHub repository URL"

        return True, None

    def validate_extraction_result(self, record: Any) -> Tuple[bool, List[str]]:
        """Runs complete battery of checks on an extracted entity."""
        errors: List[str] = []

        valid_source, source_err = self.validate_source_reference(record)
        if not valid_source:
            errors.append(source_err or "Source validation failed")

        valid_req, req_err = self.validate_required_fields(record)
        if not valid_req:
            errors.append(req_err or "Required fields check failed")

        valid_cross, cross_err = self.validate_cross_field_consistency(record)
        if not valid_cross:
            errors.append(cross_err or "Cross field consistency failed")

        return (len(errors) == 0, errors)
