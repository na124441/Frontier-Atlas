"""
Deduplication Engine.
Prevents duplicate ingestion using deterministic fingerprints and stable identifiers.
Adheres to SRS FR-13 and LLD Section 8.3.
"""

import hashlib
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse, urlunparse
from intelligent_scraper.core.interfaces import IDeduplicator
from intelligent_scraper.schemas.startup import StartupEntity
from intelligent_scraper.schemas.product import ProductEntity
from intelligent_scraper.schemas.research_paper import ResearchPaperEntity
from intelligent_scraper.schemas.job import JobEntity
from intelligent_scraper.schemas.news import NewsEntity


class Deduplicator(IDeduplicator):
    """Generates unique fingerprints and tracks duplicates in-memory and database."""

    def __init__(self):
        self.seen_fingerprints: Set[str] = set()

    def normalize_url(self, url: str) -> str:
        """
        Normalizes a URL by lowercasing hostname, stripping trailing slashes,
        and removing tracking query parameters (utm_*, ref, etc.).
        """
        if not url:
            return ""

        try:
            parsed = urlparse(url.strip())
            # Lowercase scheme and netloc
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            path = parsed.path.rstrip("/")

            # Filter query params
            filtered_query = []
            if parsed.query:
                params = parsed.query.split("&")
                for p in params:
                    k = p.split("=")[0].lower()
                    if not k.startswith("utm_") and k not in ("ref", "fbclid", "gclid"):
                        filtered_query.append(p)

            query = "&".join(filtered_query)
            clean = urlunparse((scheme, netloc, path, parsed.params, query, ""))
            return clean
        except Exception:
            return url.strip().lower().rstrip("/")

    def extract_arxiv_id(self, url: str) -> Optional[str]:
        """Extracts canonical Arxiv ID (e.g., 2312.12345 or 1706.03762)."""
        match = re.search(r'(?:arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5}(?:v\d+)?)', url, re.IGNORECASE)
        if match:
            # Strip version to ensure v1 and v2 match the same paper
            raw_id = match.group(1)
            return re.sub(r'v\d+$', '', raw_id)
        return None

    def generate_fingerprint(self, record: Any) -> str:
        """
        Computes deterministic SHA-256 fingerprint based on entity type:
        - Startup: 'startup:' + normalized canonical entity name
        - Product: 'product:' + startup_name + ':' + product_name
        - Research Paper: 'paper:' + arxiv_id OR canonical_paper_url
        - Job: 'job:' + company + ':' + canonical_job_url
        - News: 'news:' + canonical_article_url
        """
        composite_key = ""

        if isinstance(record, StartupEntity):
            canonical_name = record.content.entityName.strip().lower()
            composite_key = f"startup:{canonical_name}"

        elif isinstance(record, ProductEntity):
            startup = record.content.startupName.strip().lower()
            product = record.content.productName.strip().lower() or record.content.pricingModel.value
            composite_key = f"product:{startup}:{product}"

        elif isinstance(record, ResearchPaperEntity):
            arxiv_id = self.extract_arxiv_id(record.content.paper_url)
            if arxiv_id:
                composite_key = f"paper:arxiv:{arxiv_id}"
            else:
                norm_url = self.normalize_url(record.content.paper_url)
                norm_title = re.sub(r'\W+', '', record.content.title.lower())
                composite_key = f"paper:{norm_url}:{norm_title}"

        elif isinstance(record, JobEntity):
            company = record.content.company.strip().lower()
            url = self.normalize_url(record.content.job_url or "")
            role = record.content.role_family.strip().lower()
            composite_key = f"job:{company}:{role}:{url}"

        elif isinstance(record, NewsEntity):
            norm_url = self.normalize_url(record.content.article_url)
            composite_key = f"news:{norm_url}"

        elif isinstance(record, dict):
            # Fallback for raw dictionary records
            record_type = record.get("recordType", "").lower()
            url = self.normalize_url(record.get("source_url") or record.get("url") or "")
            composite_key = f"{record_type}:{url}"

        else:
            composite_key = str(record)

        return hashlib.sha256(composite_key.encode("utf-8")).hexdigest()

    async def is_duplicate(self, fingerprint: str) -> bool:
        """Check if fingerprint has already been recorded."""
        return fingerprint in self.seen_fingerprints

    def mark_seen(self, fingerprint: str) -> None:
        """Register fingerprint in memory."""
        self.seen_fingerprints.add(fingerprint)

    def deduplicate_batch(self, records: List[Any]) -> List[Any]:
        """Filters out duplicate items within a batch."""
        unique_records = []
        for record in records:
            fp = self.generate_fingerprint(record)
            if fp not in self.seen_fingerprints:
                self.seen_fingerprints.add(fp)
                unique_records.append(record)
        return unique_records
