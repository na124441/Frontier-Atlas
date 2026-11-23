"""
XML Sitemap Parser.
Extracts candidate URLs and publication timestamps from standard sitemaps and sitemap indexes.
"""

import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)


class SitemapParser:
    """Fetches and parses sitemap.xml to discover candidate URLs."""

    NAMESPACES = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "news": "http://www.google.com/schemas/sitemap-news/0.9"
    }

    async def fetch_and_parse(self, sitemap_url: str) -> List[Dict[str, Optional[str]]]:
        """Fetches sitemap and extracts loc and lastmod pairs."""
        results: List[Dict[str, Optional[str]]] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sitemap_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status != 200:
                        return results
                    xml_content = await resp.text()

            root = ET.fromstring(xml_content)

            # Check if this is a sitemapindex
            sub_sitemaps = root.findall(".//sm:sitemap/sm:loc", self.NAMESPACES) or root.findall(".//sitemap/loc")
            if sub_sitemaps:
                for sub in sub_sitemaps[:5]:  # Bounded to top 5 sub-sitemaps
                    if sub.text:
                        sub_results = await self.fetch_and_parse(sub.text.strip())
                        results.extend(sub_results)
                return results

            # Regular sitemap
            url_nodes = root.findall(".//sm:url", self.NAMESPACES) or root.findall(".//url")
            for node in url_nodes:
                loc_el = node.find("sm:loc", self.NAMESPACES) or node.find("loc")
                lastmod_el = node.find("sm:lastmod", self.NAMESPACES) or node.find("lastmod")

                if loc_el is not None and loc_el.text:
                    loc = loc_el.text.strip()
                    lastmod = lastmod_el.text.strip() if lastmod_el is not None and lastmod_el.text else None
                    results.append({"url": loc, "lastmod": lastmod})

        except Exception as e:
            logger.warning(f"Error parsing sitemap {sitemap_url}: {e}")

        return results
