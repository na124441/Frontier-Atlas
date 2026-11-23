"""Storage module: engine, session management, models, and repositories."""
from intelligent_scraper.storage.database import DatabaseManager, Base, db_manager
from intelligent_scraper.storage.models import (
    SourceModel, CrawlTaskModel, RawDocumentModel, ExtractionLogModel,
    CanonicalEntityModel, EntityMappingModel,
    StartupModel, ProductModel, ResearchPaperModel, JobModel, NewsModel
)
from intelligent_scraper.storage.repositories import (
    SourceRepository, TaskRepository, DocumentRepository, EntityRepository
)

__all__ = [
    "DatabaseManager",
    "Base",
    "db_manager",
    "SourceModel",
    "CrawlTaskModel",
    "RawDocumentModel",
    "ExtractionLogModel",
    "CanonicalEntityModel",
    "EntityMappingModel",
    "StartupModel",
    "ProductModel",
    "ResearchPaperModel",
    "JobModel",
    "NewsModel",
    "SourceRepository",
    "TaskRepository",
    "DocumentRepository",
    "EntityRepository",
]
