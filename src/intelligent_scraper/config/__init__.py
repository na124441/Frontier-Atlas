"""Configuration module."""
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.config.logging_config import setup_logging

__all__ = ["Settings", "get_settings", "setup_logging"]
