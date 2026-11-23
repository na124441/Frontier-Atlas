"""
Date Detector and Normalizer.
Extracts and normalizes publication dates into ISO-8601 UTC timestamps.
Adheres to SRS FR-07 and LLD Section 8.1.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
from dateutil import parser as date_parser


class DateDetector:
    """Detects, parses, and normalizes publication dates."""

    # Relative time pattern: e.g. "2 hours ago", "3 mins ago", "1 day ago"
    RELATIVE_PATTERN = re.compile(
        r'(\d+)\s+(minute|min|hour|hr|day|week|month)s?\s+ago',
        re.IGNORECASE
    )

    def extract_date(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract publication date following priority:
        1. Structured publication metadata (JSON-LD, datePublished)
        2. Open Graph / meta tags (article:published_time, og:published_time)
        3. Visible publication timestamps
        4. Relative timestamps
        5. Fallback heuristics
        """
        if not metadata:
            return None

        # Priority 1: Structured JSON-LD / schema.org
        for key in ("datePublished", "dateCreated", "publication_date", "published_time"):
            if key in metadata and metadata[key]:
                parsed = self.normalize_timestamp(metadata[key])
                if parsed:
                    return parsed

        # Priority 2: Open Graph / Dublin Core / Meta
        for key in (
            "article:published_time", "og:article:published_time", "dc.date",
            "dcterms.date", "parsely-pub-date", "sailthru.date"
        ):
            if key in metadata and metadata[key]:
                parsed = self.normalize_timestamp(metadata[key])
                if parsed:
                    return parsed

        # Priority 3: Visible / Relative dates
        if "raw_date_string" in metadata and metadata["raw_date_string"]:
            return self.normalize_timestamp(metadata["raw_date_string"])

        return None

    def parse_relative_date(self, value: str, reference_time: Optional[datetime] = None) -> Optional[datetime]:
        """Convert relative strings like '2 hours ago', 'yesterday' to absolute UTC datetime."""
        if not value:
            return None

        val = value.strip().lower()
        now = reference_time or datetime.now(timezone.utc)

        if val in ("just now", "moments ago", "a moment ago"):
            return now

        if val in ("yesterday", "1 day ago"):
            return now - timedelta(days=1)

        match = self.RELATIVE_PATTERN.search(val)
        if match:
            amount = int(match.group(1))
            unit = match.group(2).lower()

            if "min" in unit:
                return now - timedelta(minutes=amount)
            elif "hour" in unit or "hr" in unit:
                return now - timedelta(hours=amount)
            elif "day" in unit:
                return now - timedelta(days=amount)
            elif "week" in unit:
                return now - timedelta(weeks=amount)
            elif "month" in unit:
                return now - timedelta(days=amount * 30)

        return None

    def normalize_timestamp(self, value: Any, reference_time: Optional[datetime] = None) -> Optional[datetime]:
        """Normalizes any date string or unix timestamp to timezone-aware UTC datetime."""
        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        if isinstance(value, (int, float)):
            try:
                # Handle millisecond vs second timestamps
                ts = value / 1000.0 if value > 1e11 else float(value)
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            except (ValueError, OSError):
                return None

        if isinstance(value, str):
            clean_val = value.strip()
            # Try relative date parsing first
            rel_dt = self.parse_relative_date(clean_val, reference_time)
            if rel_dt:
                return rel_dt

            # Try strict dateutil parsing
            try:
                dt = date_parser.parse(clean_val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                return dt
            except (ValueError, OverflowError):
                pass

        return None

    def get_publication_date(self, document: Dict[str, Any]) -> Optional[datetime]:
        """Inspects document metadata and text snippets to extract publication date."""
        meta = document.get("metadata", {})
        dt = self.extract_date(meta)
        if dt:
            return dt

        # Check raw document fields
        for field in ("published_at", "date", "pub_date", "timestamp"):
            if field in document:
                dt = self.normalize_timestamp(document[field])
                if dt:
                    return dt

        return None
