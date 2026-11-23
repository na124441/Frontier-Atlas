"""
Metadata Extractor.
Extracts structured metadata (JSON-LD, Open Graph, meta dates, canonical URLs).
Adheres to LLD Section 5.3.
"""

import json
import re
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup


class MetadataExtractor:
    """Extracts machine-readable metadata and microdata from HTML."""

    def extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extracts and parses all <script type="application/ld+json"> blocks."""
        results: List[Dict[str, Any]] = []
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string:
                try:
                    data = json.loads(script.string.strip())
                    if isinstance(data, list):
                        results.extend(data)
                    elif isinstance(data, dict):
                        results.append(data)
                except Exception:
                    continue
        return results

    def extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extracts Open Graph and Twitter card meta properties."""
        og_data: Dict[str, str] = {}
        for tag in soup.find_all("meta"):
            prop = tag.get("property") or tag.get("name")
            content = tag.get("content")
            if prop and content:
                prop_lower = prop.lower()
                if prop_lower.startswith(("og:", "twitter:", "article:", "parsely-", "sailthru.")):
                    og_data[prop_lower] = content.strip()
        return og_data

    def extract_meta_dates(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Collects date fields from meta tags, time tags, and microdata."""
        dates: Dict[str, str] = {}

        # Check standard meta tags
        date_meta_names = [
            "article:published_time", "og:article:published_time", "publication_date",
            "date", "dc.date", "dcterms.date", "parsely-pub-date", "sailthru.date",
            "release_date"
        ]
        for name in date_meta_names:
            meta = soup.find("meta", attrs={"name": re.compile(f"^{re.escape(name)}$", re.I)}) or \
                   soup.find("meta", attrs={"property": re.compile(f"^{re.escape(name)}$", re.I)})
            if meta and meta.get("content"):
                dates[name] = meta["content"].strip()

        # Check <time> tags with datetime attribute
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            dates["time_datetime"] = time_tag["datetime"].strip()
        elif time_tag and time_tag.get_text():
            dates["time_text"] = time_tag.get_text().strip()

        return dates

    def extract_canonical_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extracts <link rel="canonical" href="...">."""
        link = soup.find("link", rel=lambda val: val and "canonical" in val.lower())
        if link and link.get("href"):
            return link["href"].strip()
        return None

    def extract_all(self, html: str) -> Dict[str, Any]:
        """Runs all metadata extraction passes on the given HTML."""
        if not html:
            return {}

        soup = BeautifulSoup(html, "html.parser")
        json_ld = self.extract_json_ld(soup)
        og = self.extract_open_graph(soup)
        dates = self.extract_meta_dates(soup)
        canonical_url = self.extract_canonical_url(soup)

        return {
            "json_ld": json_ld,
            "open_graph": og,
            "meta_dates": dates,
            "canonical_url": canonical_url
        }
