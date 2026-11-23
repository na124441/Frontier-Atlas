"""
Source Repository.
CRUD operations for sources.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from intelligent_scraper.storage.models.source import SourceModel


class SourceRepository:
    """Repository handling persistence of crawling sources."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[SourceModel]:
        stmt = select(SourceModel).where(SourceModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_all(self) -> List[SourceModel]:
        stmt = select(SourceModel)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(self, name: str, base_url: str, category: str, config: dict) -> SourceModel:
        existing = await self.get_by_name(name)
        if existing:
            existing.base_url = base_url
            existing.category = category
            existing.config = config
            return existing
        new_source = SourceModel(name=name, base_url=base_url, category=category, config=config)
        self.session.add(new_source)
        await self.session.flush()
        return new_source
