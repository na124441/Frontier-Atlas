"""
Source Registry.
Manages metadata and crawling configurations for all registered sources.
Adheres to SRS FR-01 and LLD Section 3.2.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from intelligent_scraper.core.enums import SourceCategory, CrawlStrategy


class SourceConfig:
    """Configuration container for an individual crawling source."""

    def __init__(
        self,
        name: str,
        base_url: str,
        category: SourceCategory | str,
        strategy: CrawlStrategy | str = CrawlStrategy.HTTP,
        start_urls: Optional[List[str]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        rate_limit_delay: float = 0.5,
        headers: Optional[Dict[str, str]] = None,
        extraction_rules: Optional[Dict[str, Any]] = None,
        is_active: bool = True
    ):
        self.name = name
        self.base_url = base_url
        self.category = SourceCategory(category) if isinstance(category, str) else category
        self.strategy = CrawlStrategy(strategy) if isinstance(strategy, str) else strategy
        self.start_urls = start_urls or [base_url]
        self.pagination = pagination or {}
        self.rate_limit_delay = rate_limit_delay
        self.headers = headers or {}
        self.extraction_rules = extraction_rules or {}
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.base_url,
            "category": self.category.value,
            "strategy": self.strategy.value,
            "start_urls": self.start_urls,
            "pagination": self.pagination,
            "rate_limit_delay": self.rate_limit_delay,
            "headers": self.headers,
            "extraction_rules": self.extraction_rules,
            "is_active": self.is_active
        }


class SourceRegistry:
    """Central registry of crawling targets."""

    def __init__(self, config_path: Optional[str] = None):
        self._sources: Dict[str, SourceConfig] = {}
        if config_path and Path(config_path).exists():
            self.load_from_yaml(config_path)

    def register_source(self, config: SourceConfig) -> None:
        """Registers or replaces a source configuration."""
        self._sources[config.name] = config

    def get_source(self, name: str) -> Optional[SourceConfig]:
        """Retrieves a source by unique name."""
        return self._sources.get(name)

    def list_sources(self, category: Optional[SourceCategory] = None) -> List[SourceConfig]:
        """Returns all active sources, optionally filtered by category."""
        results = [s for s in self._sources.values() if s.is_active]
        if category:
            results = [s for s in results if s.category == category]
        return results

    def update_source_config(self, name: str, **kwargs) -> Optional[SourceConfig]:
        """Updates attributes on an existing source."""
        source = self._sources.get(name)
        if not source:
            return None
        for k, v in kwargs.items():
            if hasattr(source, k):
                setattr(source, k, v)
        return source

    def load_from_yaml(self, file_path: str) -> None:
        """Loads and parses source configurations from a YAML file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        sources_data = data.get("sources", [])
        for item in sources_data:
            cfg = SourceConfig(
                name=item["name"],
                base_url=item["base_url"],
                category=item.get("category", SourceCategory.STARTUP_DIRECTORY.value),
                strategy=item.get("strategy", CrawlStrategy.HTTP.value),
                start_urls=item.get("start_urls"),
                pagination=item.get("pagination"),
                rate_limit_delay=item.get("rate_limit_delay", 0.5),
                headers=item.get("headers"),
                extraction_rules=item.get("extraction_rules"),
                is_active=item.get("is_active", True)
            )
            self.register_source(cfg)
