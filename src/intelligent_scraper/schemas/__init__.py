"""Pydantic data contracts for all extracted entities."""
from intelligent_scraper.schemas.base import BaseEntity, SourceMetadata
from intelligent_scraper.schemas.startup import StartupEntity, StartupData
from intelligent_scraper.schemas.product import ProductEntity, ProductData
from intelligent_scraper.schemas.research_paper import ResearchPaperEntity, ResearchPaperData
from intelligent_scraper.schemas.job import JobEntity, JobData
from intelligent_scraper.schemas.news import NewsEntity, NewsData

__all__ = [
    "BaseEntity",
    "SourceMetadata",
    "StartupEntity",
    "StartupData",
    "ProductEntity",
    "ProductData",
    "ResearchPaperEntity",
    "ResearchPaperData",
    "JobEntity",
    "JobData",
    "NewsEntity",
    "NewsData",
]
