"""
HTML Parser.
Extracts title, hyperlinks, structured metadata, and main content.
Adheres to LLD Section 5.1.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from intelligent_scraper.extraction.content_cleaner import ContentCleaner
from intelligent_scraper.extraction.metadata_extractor import MetadataExtractor


class HTMLParser:
    """Robust HTML parsing engine using BeautifulSoup with fallback helpers."""

    def __init__(self):
        self.cleaner = ContentCleaner()
        self.metadata_extractor = MetadataExtractor()

    def parse(self, html: str) -> BeautifulSoup:
        """Parses HTML into BeautifulSoup object."""
        return BeautifulSoup(html, "html.parser")

    def extract_title(self, html: str) -> str:
        """Extracts document title, falling back to h1 or og:title."""
        if not html:
            return ""

        soup = self.parse(html)
        # Check <title>
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text():
            return title_tag.get_text().strip()

        # Check og:title
        og_title = soup.find("meta", attrs={"property": "og:title"}) or soup.find("meta", attrs={"name": "og:title"})
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Check first <h1>
        h1 = soup.find("h1")
        if h1 and h1.get_text():
            return h1.get_text().strip()

        return ""

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extracts and resolves all valid absolute HTTP(S) links."""
        if not html:
            return []

        soup = self.parse(html)
        links = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            # Ignore fragments, javascript, mailto
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            try:
                abs_url = urljoin(base_url, href)
                parsed = urlparse(abs_url)
                if parsed.scheme in ("http", "https") and parsed.netloc:
                    links.add(abs_url)
            except Exception:
                continue

        return list(links)

    def extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extracts metadata via MetadataExtractor."""
        return self.metadata_extractor.extract_all(html)

    def extract_main_content(self, html: str) -> str:
        """Extracts cleaned textual representation."""
        return self.cleaner.clean_content(html)
