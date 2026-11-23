"""Repositories for storage models."""
from intelligent_scraper.storage.repositories.source_repository import SourceRepository
from intelligent_scraper.storage.repositories.task_repository import TaskRepository
from intelligent_scraper.storage.repositories.document_repository import DocumentRepository
from intelligent_scraper.storage.repositories.entity_repository import EntityRepository

__all__ = [
    "SourceRepository",
    "TaskRepository",
    "DocumentRepository",
    "EntityRepository",
]
