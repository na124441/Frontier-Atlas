"""End-to-End Test for the Full Ingestion and Export Pipeline."""
import pytest
from unittest.mock import AsyncMock
from intelligent_scraper.orchestration.pipeline import IngestionPipeline
from intelligent_scraper.discovery.url_frontier import CrawlTask
from intelligent_scraper.discovery.source_registry import SourceConfig
from intelligent_scraper.core.enums import SourceCategory
from intelligent_scraper.storage.database import DatabaseManager


@pytest.mark.asyncio
async def test_full_pipeline_e2e(tmp_path):
    test_db_url = f"sqlite+aiosqlite:///{tmp_path.as_posix()}/e2e.db"
    db = DatabaseManager(db_url=test_db_url)
    pipeline = IngestionPipeline(db=db)
    await pipeline.initialize()

    # Mock adaptive fetcher so no real network requests are made during unit/e2e test
    sample_html = (
        "<html><head><title>OpenAI Releases New Frontier Model</title></head>"
        "<body><article><h1>OpenAI Releases New Frontier Model</h1>"
        "<p>OpenAI has announced a major upgrade to their frontier architecture with significant reasoning improvements.</p>"
        "</article></body></html>"
    )
    pipeline.adaptive_fetcher.fetch = AsyncMock(return_value={
        "status_code": 200,
        "response_headers": {},
        "html_content": sample_html,
        "final_url": "https://example.com/news/openai-announcement"
    })

    # Create dummy source config
    source = SourceConfig(
        name="test_news_source",
        base_url="https://example.com/news",
        category=SourceCategory.NEWS_WEBSITE
    )

    # Mock task
    task = CrawlTask(
        priority=1,
        task_id="test-task-1",
        url="https://example.com/news/openai-announcement",
        source_id="test_news_source"
    )

    entity = await pipeline.process_crawl_task(task, source)
    assert entity is not None

    # Check results in memory
    assert len(pipeline.collected_news) == 1
    assert pipeline.collected_news[0].recordType == "NEWS"

    # Test 6-tab export
    exports = pipeline.export_all_tabs()
    assert "news" in exports
    assert exports["news"]["count"] == 1
    assert "mapping_logs" in exports

    await pipeline.shutdown()
