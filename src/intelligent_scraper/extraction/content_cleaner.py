"""
Content Cleaner.
Removes boilerplate elements (nav, header, footer, scripts, ads) while preserving
meaningful content (headings, article paragraphs, dates, code/links).
Adheres to SRS FR-09 and LLD Section 5.2.
"""

import re
from bs4 import BeautifulSoup, Comment


class ContentCleaner:
    """Cleans HTML to extract primary textual content."""

    # Tags to remove completely
    STRIP_TAGS = [
        "script", "style", "noscript", "svg", "canvas", "iframe",
        "header", "footer", "nav", "aside", "menu", "form"
    ]

    # Classes or IDs usually containing ads, comments, or boilerplate
    NOISE_PATTERNS = re.compile(
        r'(banner|cookie|gdpr|ad-|ads|advertisement|newsletter|social-share|share-bar|comment|sidebar)',
        re.IGNORECASE
    )

    def remove_scripts(self, soup: BeautifulSoup) -> None:
        """Removes script, noscript, style, and iframe tags."""
        for tag in soup.find_all(["script", "noscript", "style", "iframe", "svg"]):
            tag.decompose()

    def remove_navigation(self, soup: BeautifulSoup) -> None:
        """Removes nav, header, footer, and menu elements."""
        for tag in soup.find_all(["nav", "header", "footer", "menu", "aside"]):
            tag.decompose()

    def remove_irrelevant_sections(self, soup: BeautifulSoup) -> None:
        """Removes comments and noise elements (banners, social shares, cookie prompts)."""
        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove elements with noise classes/ids
        for el in soup.find_all(attrs={"class": self.NOISE_PATTERNS}):
            el.decompose()
        for el in soup.find_all(attrs={"id": self.NOISE_PATTERNS}):
            el.decompose()

    def normalize_whitespace(self, text: str) -> str:
        """Collapses consecutive whitespace and blank lines."""
        if not text:
            return ""
        # Collapse multiple spaces on the same line
        text = re.sub(r'[ \t]+', ' ', text)
        # Collapse more than two consecutive newlines into two
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()

    def clean_content(self, html: str) -> str:
        """Executes full cleaning pipeline and returns normalized text."""
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")
        self.remove_scripts(soup)
        self.remove_navigation(soup)
        self.remove_irrelevant_sections(soup)

        # Extract text from main container if available
        main_tag = soup.find("main") or soup.find("article") or soup.find("div", {"id": "content"}) or soup.body
        target = main_tag if main_tag else soup

        raw_text = target.get_text(separator="\n", strip=True)
        return self.normalize_whitespace(raw_text)
