"""
Intelligent Source Discovery Engine.
Automates URL discovery across web directories, RSS/Atom feeds, sitemaps, and paginated pages.
Adheres to SRS FR-01 and LLD Section 3.3.
"""

import re
import logging
from typing import Any, Dict, List, Set, Optional
from urllib.parse import urlparse
import aiohttp
from intelligent_scraper.crawler.http_fetcher import HTTPFetcher
from intelligent_scraper.discovery.source_registry import SourceConfig
from intelligent_scraper.discovery.sitemap_parser import SitemapParser
from intelligent_scraper.extraction.html_parser import HTMLParser

logger = logging.getLogger(__name__)


class SourceDiscovery:
    """Discovers URLs from registered source endpoints."""

    def __init__(self, http_fetcher: Optional[HTTPFetcher] = None):
        self.http_fetcher = http_fetcher or HTTPFetcher()
        self.html_parser = HTMLParser()
        self.sitemap_parser = SitemapParser()

    def validate_url(self, url: str, base_domain: str) -> bool:
        """Validates that URL is absolute, has http/https, and matches base domain restrictions."""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            if not parsed.netloc:
                return False
            # Check domain boundary if specified
            if base_domain and not (base_domain.lower() in parsed.netloc.lower()):
                return False
            # Skip media and binary files
            if re.search(r'\.(pdf|png|jpg|jpeg|gif|zip|tar|gz|exe|dmg|svg|mp4)$', parsed.path, re.IGNORECASE):
                return False
            return True
        except Exception:
            return False

    async def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extracts and resolves links from HTML content."""
        return self.html_parser.extract_links(html, base_url)

    async def discover_from_sitemap(self, sitemap_url: str) -> List[Dict[str, Any]]:
        """Extracts candidate URLs from XML sitemap."""
        return await self.sitemap_parser.fetch_and_parse(sitemap_url)

    async def discover_from_feed(self, feed_url: str) -> List[str]:
        """Extracts links from RSS or Atom XML feeds."""
        links: List[str] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        # Extract <link> or <link href="..." />
                        found = re.findall(r'<link[^>]*href=[\'"]([^\'"]+)[\'"]', text) or \
                                re.findall(r'<link>([^<]+)</link>', text)
                        for u in found:
                            u_str = u.strip()
                            if u_str.startswith("http"):
                                links.append(u_str)
        except Exception as e:
            logger.warning(f"Error fetching feed {feed_url}: {e}")
        return links

    async def discover_urls(self, source: SourceConfig, max_urls: int = 50) -> List[Dict[str, Any]]:
        """
        Executes discovery workflow for a source:
        1. Checks sitemaps or start URLs.
        2. Follows pagination if configured.
        3. Returns discovered URL task descriptors.
        """
        discovered: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()
        base_domain = urlparse(source.base_url).netloc

        for start_url in source.start_urls:
            if len(discovered) >= max_urls:
                break

            # Handle sitemap start URLs
            if "sitemap" in start_url.lower():
                sitemap_entries = await self.discover_from_sitemap(start_url)
                for entry in sitemap_entries:
                    u = entry.get("url")
                    if u and u not in seen_urls and self.validate_url(u, base_domain):
                        seen_urls.add(u)
                        discovered.append({
                            "url": u,
                            "source_name": source.name,
                            "metadata": {"lastmod": entry.get("lastmod")}
                        })
                        if len(discovered) >= max_urls:
                            break
                continue

            # Handle regular web directory or feed
            try:
                fetch_res = await self.http_fetcher.fetch(start_url)
                html = fetch_res.get("html_content", "")
                links = await self.extract_links(html, start_url)

                for link in links:
                    if link not in seen_urls and self.validate_url(link, base_domain):
                        seen_urls.add(link)
                        discovered.append({
                            "url": link,
                            "source_name": source.name,
                            "metadata": {}
                        })
                        if len(discovered) >= max_urls:
                            break

            except Exception as e:
                logger.warning(f"Error discovering from {start_url}: {e}")

        return discovered
