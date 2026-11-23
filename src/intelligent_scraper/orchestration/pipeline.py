"""
End-to-End Ingestion Pipeline Orchestrator.
Glues together discovery, adaptive crawling, extraction, LLM fallback, entity resolution,
freshness validation, deduplication, persistence, and Google Sheets export.
Adheres to SRS Section 2.2, 3.1 and LLD Section 10.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from intelligent_scraper.config.settings import Settings, get_settings
from intelligent_scraper.core.enums import RecordType, SourceCategory
from intelligent_scraper.crawler.adaptive_fetcher import AdaptiveFetcher
from intelligent_scraper.crawler.async_crawler import AsyncCrawler
from intelligent_scraper.discovery.source_registry import SourceRegistry, SourceConfig
from intelligent_scraper.discovery.source_discovery import SourceDiscovery
from intelligent_scraper.discovery.url_frontier import URLFrontier, CrawlTask
from intelligent_scraper.extraction.html_parser import HTMLParser
from intelligent_scraper.extraction.content_cleaner import ContentCleaner
from intelligent_scraper.intelligence.date_detector import DateDetector
from intelligent_scraper.intelligence.freshness_validator import FreshnessValidator
from intelligent_scraper.intelligence.entity_resolver import EntityResolver
from intelligent_scraper.intelligence.deduplicator import Deduplicator
from intelligent_scraper.intelligence.confidence_validator import ConfidenceValidator
from intelligent_scraper.integrations.github_client import GitHubClient
from intelligent_scraper.llm.extraction_service import ExtractionService
from intelligent_scraper.llm.model_router import ModelRouter
from intelligent_scraper.orchestration.retry_manager import RetryManager
from intelligent_scraper.orchestration.task_manager import TaskManager
from intelligent_scraper.storage.database import db_manager, DatabaseManager
from intelligent_scraper.storage.repositories.entity_repository import EntityRepository
from intelligent_scraper.storage.repositories.document_repository import DocumentRepository
from intelligent_scraper.schemas.startup import StartupEntity, StartupData
from intelligent_scraper.schemas.product import ProductEntity, ProductData
from intelligent_scraper.schemas.research_paper import ResearchPaperEntity, ResearchPaperData
from intelligent_scraper.schemas.job import JobEntity, JobData
from intelligent_scraper.schemas.news import NewsEntity, NewsData
from intelligent_scraper.schemas.base import SourceMetadata
from intelligent_scraper.exporters.sheets_exporter import SheetsExporter

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Central pipeline coordinator implementing the 11-step ingestion workflow."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        db: Optional[DatabaseManager] = None
    ):
        self.settings = settings or get_settings()
        self.db = db or db_manager

        # Initialize core components
        self.registry = SourceRegistry(self.settings.SOURCES_CONFIG_PATH)
        self.frontier = URLFrontier()
        self.task_manager = TaskManager(self.frontier)
        self.retry_manager = RetryManager(self.settings)

        self.adaptive_fetcher = AdaptiveFetcher()
        self.crawler = AsyncCrawler(self.adaptive_fetcher, self.settings)
        self.discovery = SourceDiscovery(self.adaptive_fetcher.http_fetcher)

        self.html_parser = HTMLParser()
        self.content_cleaner = ContentCleaner()

        self.model_router = ModelRouter(self.settings)
        self.extraction_service = ExtractionService(self.model_router)

        self.date_detector = DateDetector()
        self.freshness_validator = FreshnessValidator(self.settings.FRESHNESS_HOURS * 3600)
        self.entity_resolver = EntityResolver(self.settings.SEED_DATABASE_PATH)
        self.deduplicator = Deduplicator()
        self.confidence_validator = ConfidenceValidator()

        self.github_client = GitHubClient(settings=self.settings)
        self.exporter = SheetsExporter(settings=self.settings)

        # In-memory collections for quick retrieval and exporting
        self.collected_startups: List[StartupEntity] = []
        self.collected_products: List[ProductEntity] = []
        self.collected_papers: List[ResearchPaperEntity] = []
        self.collected_jobs: List[JobEntity] = []
        self.collected_news: List[NewsEntity] = []

    async def initialize(self) -> None:
        """Initializes database tables and connections."""
        await self.db.init_models()
        logger.info("Ingestion pipeline initialized.")

    def map_category_to_record_type(self, category: SourceCategory) -> RecordType:
        """Maps source category to primary expected entity type."""
        mapping = {
            SourceCategory.STARTUP_DIRECTORY: RecordType.STARTUP,
            SourceCategory.PRODUCT_DIRECTORY: RecordType.PRODUCT,
            SourceCategory.RESEARCH_REPOSITORY: RecordType.RESEARCH_PAPER,
            SourceCategory.JOB_BOARD: RecordType.JOB,
            SourceCategory.NEWS_WEBSITE: RecordType.NEWS,
            SourceCategory.GITHUB_REPOSITORY: RecordType.RESEARCH_PAPER
        }
        return mapping.get(category, RecordType.STARTUP)

    async def process_crawl_task(self, task: CrawlTask, source: SourceConfig) -> Optional[Any]:
        """
        Executes pipeline for an individual crawl task:
        Fetch -> Clean -> LLM Extract -> Date/Freshness -> Entity Resolution -> Deduplicate -> Persist
        """
        url = task.url
        record_type = self.map_category_to_record_type(source.category)

        # 1. Fetch content adaptively
        try:
            fetch_result = await self.adaptive_fetcher.fetch(url, source.to_dict())
        except Exception as e:
            if self.retry_manager.should_retry(e, task.retry_count):
                retry_at = self.retry_manager.schedule_retry(task.to_dict(), e)
                await self.frontier.schedule_retry(task.task_id, retry_at)
            else:
                self.retry_manager.move_to_dead_letter(task.to_dict(), e, stage="fetching")
                await self.task_manager.mark_task_done(task.task_id, success=False, reason=str(e))
            return None

        html = fetch_result.get("html_content", "")
        cleaned_text = self.content_cleaner.clean_content(html)
        metadata = self.html_parser.extract_metadata(html)

        # 2. Date & Freshness Check (Required for News and Jobs)
        pub_date = self.date_detector.extract_date(metadata.get("meta_dates", {}))
        if not pub_date:
            pub_date = self.date_detector.parse_relative_date(cleaned_text[:500])
        if not pub_date:
            pub_date = datetime.now(timezone.utc)  # Default fallback if unknown

        if record_type in (RecordType.NEWS, RecordType.JOB):
            is_fresh, reason = self.freshness_validator.validate_or_quarantine(pub_date)
            if not is_fresh:
                logger.warning(f"Record quarantined: {reason} for URL {url}")
                await self.task_manager.mark_task_done(task.task_id, success=False, reason=reason)
                return None

        # 3. LLM-based structured extraction
        try:
            extracted_dict = await self.extraction_service.extract_entity(
                content=cleaned_text,
                record_type=record_type,
                source_url=url
            )
        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            self.retry_manager.move_to_dead_letter(task.to_dict(), e, stage="extraction")
            await self.task_manager.mark_task_done(task.task_id, success=False, reason=str(e))
            return None

        # 4. Construct typed Entity and resolve names
        source_meta = SourceMetadata(name=source.name, url=url)
        entity = None

        if record_type == RecordType.STARTUP:
            raw_name = extracted_dict.get("entityName") or "Unknown"
            canonical_name = self.entity_resolver.resolve_entity(raw_name)
            startup_data = StartupData(
                entityName=canonical_name,
                employeeCount=extracted_dict.get("employeeCount")
            )
            entity = StartupEntity(source=source_meta, content=startup_data)

        elif record_type == RecordType.PRODUCT:
            raw_startup = extracted_dict.get("startupName") or "Unknown"
            canonical_startup = self.entity_resolver.resolve_entity(raw_startup)
            pricing = extracted_dict.get("pricingModel", "FREEMIUM")
            product_data = ProductData(
                startupName=canonical_startup,
                productName=extracted_dict.get("productName", f"{canonical_startup} Product"),
                pricingModel=pricing
            )
            entity = ProductEntity(source=source_meta, content=product_data)

        elif record_type == RecordType.RESEARCH_PAPER:
            # Check GitHub repository and star count
            gh_url = extracted_dict.get("github_url")
            stars = extracted_dict.get("github_stars")
            if gh_url:
                norm_gh = self.github_client.normalize_repository_url(gh_url)
                if norm_gh:
                    gh_url = norm_gh
                    is_valid, fetched_stars = await self.github_client.validate_repository(norm_gh)
                    if is_valid and fetched_stars is not None:
                        stars = fetched_stars

            paper_data = ResearchPaperData(
                title=extracted_dict.get("title", "Untitled Research"),
                authors=extracted_dict.get("authors", []),
                paper_url=extracted_dict.get("paper_url", url),
                github_url=gh_url,
                github_stars=stars,
                published_date=pub_date
            )
            entity = ResearchPaperEntity(content=paper_data)

        elif record_type == RecordType.JOB:
            raw_company = extracted_dict.get("company") or "Unknown"
            canonical_company = self.entity_resolver.resolve_entity(raw_company)
            job_data = JobData(
                company=canonical_company,
                date=pub_date,
                is_remote=extracted_dict.get("is_remote", False),
                role_family=extracted_dict.get("role_family", "Engineering"),
                title=extracted_dict.get("title", "AI Specialist"),
                job_url=url
            )
            entity = JobEntity(content=job_data)

        elif record_type == RecordType.NEWS:
            news_data = NewsData(
                title=extracted_dict.get("title", "AI Ecosystem Update"),
                article_url=extracted_dict.get("article_url", url),
                full_text=extracted_dict.get("full_text", cleaned_text[:1500]),
                published_date=pub_date,
                summary=extracted_dict.get("summary")
            )
            entity = NewsEntity(source=source_meta, content=news_data)

        # 5. Confidence and Required-Field Validation
        is_valid, validation_errors = self.confidence_validator.validate_extraction_result(entity)
        if not is_valid:
            logger.warning(f"Record validation failed for {url}: {validation_errors}")
            await self.task_manager.mark_task_done(task.task_id, success=False, reason="; ".join(validation_errors))
            return None

        # 6. Deduplication Check
        fingerprint = self.deduplicator.generate_fingerprint(entity)
        if await self.deduplicator.is_duplicate(fingerprint):
            logger.info(f"Duplicate record ignored (fp={fingerprint})")
            await self.task_manager.mark_task_done(task.task_id, success=True)
            return None
        self.deduplicator.mark_seen(fingerprint)

        # 7. Persistence into Database
        await self.persist_record(entity, fingerprint, cleaned_text, url)

        # 8. Store in memory for export
        if record_type == RecordType.STARTUP:
            self.collected_startups.append(entity)
        elif record_type == RecordType.PRODUCT:
            self.collected_products.append(entity)
        elif record_type == RecordType.RESEARCH_PAPER:
            self.collected_papers.append(entity)
        elif record_type == RecordType.JOB:
            self.collected_jobs.append(entity)
        elif record_type == RecordType.NEWS:
            self.collected_news.append(entity)

        await self.task_manager.mark_task_done(task.task_id, success=True)
        return entity

    async def persist_record(self, entity: Any, fingerprint: str, cleaned_text: str, source_url: str) -> None:
        """Saves record and provenance document into database."""
        async for session in self.db.get_session():
            entity_repo = EntityRepository(session)
            doc_repo = DocumentRepository(session)

            await doc_repo.save_document(source_url=source_url, cleaned_content=cleaned_text)

            if isinstance(entity, StartupEntity):
                await entity_repo.save_startup(
                    entity_name=entity.content.entityName,
                    employee_count=entity.content.employeeCount,
                    source_name=entity.source.name,
                    source_url=entity.source.url,
                    fingerprint=fingerprint
                )
            elif isinstance(entity, ProductEntity):
                await entity_repo.save_product(
                    startup_name=entity.content.startupName,
                    product_name=entity.content.productName,
                    pricing_model=entity.content.pricingModel.value,
                    source_name=entity.source.name,
                    source_url=entity.source.url,
                    fingerprint=fingerprint
                )
            elif isinstance(entity, ResearchPaperEntity):
                await entity_repo.save_research_paper(
                    title=entity.content.title,
                    authors=entity.content.authors,
                    paper_url=entity.content.paper_url,
                    github_url=entity.content.github_url,
                    github_stars=entity.content.github_stars,
                    published_date=entity.content.published_date,
                    fingerprint=fingerprint
                )
            elif isinstance(entity, JobEntity):
                await entity_repo.save_job(
                    company=entity.content.company,
                    title=entity.content.title,
                    job_url=entity.content.job_url,
                    is_remote=entity.content.is_remote,
                    role_family=entity.content.role_family,
                    published_date=entity.content.date,
                    fingerprint=fingerprint
                )
            elif isinstance(entity, NewsEntity):
                await entity_repo.save_news(
                    title=entity.content.title,
                    article_url=entity.content.article_url,
                    full_text=entity.content.full_text,
                    published_date=entity.content.published_date,
                    source_name=entity.source.name,
                    source_url=entity.source.url,
                    fingerprint=fingerprint
                )

    async def run_discovery_for_sources(self, max_per_source: int = 15) -> int:
        """Runs source discovery across all registered sources and registers discovered URLs."""
        sources = self.registry.list_sources()
        total_discovered = 0

        for src in sources:
            logger.info(f"Discovering candidate URLs for source: {src.name}")
            try:
                candidates = await self.discovery.discover_urls(src, max_urls=max_per_source)
                tasks = await self.task_manager.create_processing_tasks(candidates)
                total_discovered += len(tasks)
            except Exception as e:
                logger.warning(f"Discovery error on source {src.name}: {e}")

        return total_discovered

    async def run_pipeline(self, max_tasks: int = 50) -> Dict[str, Any]:
        """Runs batch crawl and ingestion tasks."""
        tasks = await self.task_manager.dispatch_tasks_to_workers(batch_size=max_tasks)
        logger.info(f"Processing batch of {len(tasks)} tasks.")

        results = []
        for task in tasks:
            source = self.registry.get_source(task.source_id)
            if not source:
                # Fallback generic source
                source = SourceConfig(name=task.source_id, base_url=task.url, category=SourceCategory.STARTUP_DIRECTORY)
            res = await self.process_crawl_task(task, source)
            if res:
                results.append(res)

        return {
            "processed": len(tasks),
            "successful_extractions": len(results),
            "stats": self.task_manager.get_stats()
        }

    def export_all_tabs(self) -> Dict[str, Any]:
        """Exports datasets across all six Google Sheets tabs / CSV files."""
        mapping_logs = self.entity_resolver.get_mapping_logs()
        return self.exporter.export_all(
            startups=self.collected_startups,
            products=self.collected_products,
            research_papers=self.collected_papers,
            jobs=self.collected_jobs,
            news=self.collected_news,
            mapping_logs=mapping_logs
        )

    async def shutdown(self) -> None:
        """Closes all network sessions and database connections."""
        await self.crawler.shutdown()
        await self.db.close()
