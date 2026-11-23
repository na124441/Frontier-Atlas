"""Discovery module: source registry, source discovery, sitemap parser, and URL frontier."""
from intelligent_scraper.discovery.source_registry import SourceRegistry, SourceConfig
from intelligent_scraper.discovery.sitemap_parser import SitemapParser
from intelligent_scraper.discovery.source_discovery import SourceDiscovery
from intelligent_scraper.discovery.url_frontier import URLFrontier, CrawlTask

__all__ = [
    "SourceRegistry",
    "SourceConfig",
    "SitemapParser",
    "SourceDiscovery",
    "URLFrontier",
    "CrawlTask",
]
