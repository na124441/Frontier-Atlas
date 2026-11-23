"""
Task Repository.
Persists and queries crawl task statuses.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from intelligent_scraper.storage.models.crawl_task import CrawlTaskModel


class TaskRepository:
    """Repository handling crawl tasks."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: str) -> Optional[CrawlTaskModel]:
        stmt = select(CrawlTaskModel).where(CrawlTaskModel.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_task(self, source_id: str, url: str, priority: int = 10) -> CrawlTaskModel:
        task = CrawlTaskModel(source_id=source_id, url=url, priority=priority)
        self.session.add(task)
        await self.session.flush()
        return task

    async def update_status(self, task_id: str, status: str, retry_count: Optional[int] = None) -> Optional[CrawlTaskModel]:
        task = await self.get_by_id(task_id)
        if task:
            task.status = status
            if retry_count is not None:
                task.retry_count = retry_count
            await self.session.flush()
        return task

    async def get_pending(self, limit: int = 50) -> List[CrawlTaskModel]:
        stmt = select(CrawlTaskModel).where(CrawlTaskModel.status == "PENDING").order_by(CrawlTaskModel.priority).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
