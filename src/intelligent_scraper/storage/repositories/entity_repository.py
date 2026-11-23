"""
Entity Repository.
Handles persistent storage and retrieval for all validated entities:
Startups, Products, Research Papers, Jobs, News, and Canonical Mappings.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from intelligent_scraper.storage.models.entity import (
    StartupModel, ProductModel, ResearchPaperModel, JobModel, NewsModel,
    CanonicalEntityModel, EntityMappingModel
)


class EntityRepository:
    """Repository handling entity persistence and tab export querying."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # 1. Startup Entity
    async def save_startup(
        self,
        entity_name: str,
        employee_count: Optional[int],
        source_name: str,
        source_url: str,
        fingerprint: str
    ) -> StartupModel:
        stmt = select(StartupModel).where(StartupModel.fingerprint == fingerprint)
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        startup = StartupModel(
            entity_name=entity_name,
            employee_count=employee_count,
            source_name=source_name,
            source_url=source_url,
            fingerprint=fingerprint
        )
        self.session.add(startup)
        await self.session.flush()
        return startup

    # 2. Product Entity
    async def save_product(
        self,
        startup_name: str,
        product_name: str,
        pricing_model: str,
        source_name: str,
        source_url: str,
        fingerprint: str
    ) -> ProductModel:
        stmt = select(ProductModel).where(ProductModel.fingerprint == fingerprint)
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        product = ProductModel(
            startup_name=startup_name,
            product_name=product_name,
            pricing_model=pricing_model,
            source_name=source_name,
            source_url=source_url,
            fingerprint=fingerprint
        )
        self.session.add(product)
        await self.session.flush()
        return product

    # 3. Research Paper Entity
    async def save_research_paper(
        self,
        title: str,
        authors: List[str],
        paper_url: str,
        github_url: Optional[str],
        github_stars: Optional[int],
        published_date: Any,
        fingerprint: str
    ) -> ResearchPaperModel:
        stmt = select(ResearchPaperModel).where(ResearchPaperModel.fingerprint == fingerprint)
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        paper = ResearchPaperModel(
            title=title,
            authors=authors,
            paper_url=paper_url,
            github_url=github_url,
            github_stars=github_stars,
            published_date=published_date,
            fingerprint=fingerprint
        )
        self.session.add(paper)
        await self.session.flush()
        return paper

    # 4. Job Entity
    async def save_job(
        self,
        company: str,
        title: Optional[str],
        job_url: Optional[str],
        is_remote: bool,
        role_family: str,
        published_date: Any,
        fingerprint: str
    ) -> JobModel:
        stmt = select(JobModel).where(JobModel.fingerprint == fingerprint)
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        job = JobModel(
            company=company,
            title=title,
            job_url=job_url,
            is_remote=is_remote,
            role_family=role_family,
            published_date=published_date,
            fingerprint=fingerprint
        )
        self.session.add(job)
        await self.session.flush()
        return job

    # 5. News Entity
    async def save_news(
        self,
        title: str,
        article_url: str,
        full_text: str,
        published_date: Any,
        source_name: str,
        source_url: str,
        fingerprint: str
    ) -> NewsModel:
        stmt = select(NewsModel).where(NewsModel.fingerprint == fingerprint)
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        news = NewsModel(
            title=title,
            article_url=article_url,
            full_text=full_text,
            published_date=published_date,
            source_name=source_name,
            source_url=source_url,
            fingerprint=fingerprint
        )
        self.session.add(news)
        await self.session.flush()
        return news

    # 6. Entity Mappings
    async def save_mapping(self, raw_name: str, canonical_name: str, method: str = "DETERMINISTIC") -> EntityMappingModel:
        stmt = select(EntityMappingModel).where(
            EntityMappingModel.raw_name == raw_name,
            EntityMappingModel.canonical_name == canonical_name
        )
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            return existing

        mapping = EntityMappingModel(
            raw_name=raw_name,
            canonical_name=canonical_name,
            matching_method=method
        )
        self.session.add(mapping)
        await self.session.flush()
        return mapping

    # Query methods for Google Sheets export
    async def get_all_startups(self) -> List[StartupModel]:
        res = await self.session.execute(select(StartupModel))
        return list(res.scalars().all())

    async def get_all_products(self) -> List[ProductModel]:
        res = await self.session.execute(select(ProductModel))
        return list(res.scalars().all())

    async def get_all_research_papers(self) -> List[ResearchPaperModel]:
        res = await self.session.execute(select(ResearchPaperModel))
        return list(res.scalars().all())

    async def get_all_jobs(self) -> List[JobModel]:
        res = await self.session.execute(select(JobModel))
        return list(res.scalars().all())

    async def get_all_news(self) -> List[NewsModel]:
        res = await self.session.execute(select(NewsModel))
        return list(res.scalars().all())

    async def get_all_mappings(self) -> List[EntityMappingModel]:
        res = await self.session.execute(select(EntityMappingModel))
        return list(res.scalars().all())
