"""
Document Repository.
Persists raw and cleaned document snapshots for data provenance.
"""

import hashlib
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from intelligent_scraper.storage.models.raw_document import RawDocumentModel


class DocumentRepository:
    """Repository handling document storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_content_hash(self, content_hash: str) -> Optional[RawDocumentModel]:
        stmt = select(RawDocumentModel).where(RawDocumentModel.content_hash == content_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def save_document(
        self,
        source_url: str,
        cleaned_content: str,
        crawl_task_id: Optional[str] = None,
        raw_location: Optional[str] = None
    ) -> RawDocumentModel:
        content_hash = hashlib.sha256((cleaned_content or source_url).encode("utf-8")).hexdigest()
        existing = await self.get_by_content_hash(content_hash)
        if existing:
            return existing

        doc = RawDocumentModel(
            crawl_task_id=crawl_task_id,
            source_url=source_url,
            content_hash=content_hash,
            raw_content_location=raw_location,
            cleaned_content=cleaned_content,
            extraction_status="EXTRACTED"
        )
        self.session.add(doc)
        await self.session.flush()
        return doc
