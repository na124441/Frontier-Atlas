"""
Comprehensive Test Runner for Intelligent Web Scraper.
Directly executes unit, integration, and E2E test suites with detailed reporting.
"""

import asyncio
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

passed = 0
failed = 0
errors = []


def report(name: str, success: bool, err_msg: str = ""):
    global passed, failed, errors
    if success:
        passed += 1
        print(f"  [PASS] {name}", flush=True)
    else:
        failed += 1
        errors.append((name, err_msg))
        print(f"  [FAIL] {name}: {err_msg}", flush=True)


async def run_all_tests():
    print("==================================================", flush=True)
    print("Running Intelligent Web Scraper Test Suite", flush=True)
    print("==================================================", flush=True)

    # 1. Date Detector & Freshness Tests
    print("\n--- 1. Date Detector & Freshness Validator ---")
    try:
        from intelligent_scraper.intelligence.date_detector import DateDetector
        from intelligent_scraper.intelligence.freshness_validator import FreshnessValidator

        detector = DateDetector()
        ref = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        dt = detector.parse_relative_date("2 hours ago", reference_time=ref)
        report("DateDetector relative 2 hours ago", dt == datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc))

        dt_min = detector.parse_relative_date("15 mins ago", reference_time=ref)
        report("DateDetector relative 15 mins ago", dt_min == datetime(2024, 6, 1, 11, 45, 0, tzinfo=timezone.utc))

        validator = FreshnessValidator(max_age_seconds=86400)
        now = datetime.now(timezone.utc)
        report("FreshnessValidator 2h age is fresh", validator.is_fresh(now - timedelta(hours=2), reference_time=now))
        report("FreshnessValidator 25h age is stale", not validator.is_fresh(now - timedelta(hours=25), reference_time=now))
    except Exception as e:
        report("Date Detector Tests", False, str(e))

    # 2. Entity Resolver Tests
    print("\n--- 2. Deterministic Entity Resolution ---")
    try:
        from intelligent_scraper.intelligence.entity_resolver import EntityResolver

        resolver = EntityResolver("./data/seed/ai_startups_seed.json")
        report("EntityResolver exact match OpenAI", resolver.resolve_entity("OpenAI") == "OpenAI")
        report("EntityResolver variation Open AI", resolver.resolve_entity("Open AI") == "OpenAI")
        report("EntityResolver corporate suffix OpenAI Inc.", resolver.resolve_entity("OpenAI Inc.") == "OpenAI")
        report("EntityResolver corporate suffix OpenAI, Inc.", resolver.resolve_entity("OpenAI, Inc.") == "OpenAI")
        report("EntityResolver corporate suffix OpenAI LLC", resolver.resolve_entity("OpenAI LLC") == "OpenAI")
        report("EntityResolver Anthropic PBC", resolver.resolve_entity("Anthropic PBC") == "Anthropic")
        report("EntityResolver Perplexity AI Inc", resolver.resolve_entity("Perplexity AI Inc") == "Perplexity AI")

        logs = resolver.get_mapping_logs()
        report("EntityResolver generates mapping logs", len(logs) >= 3)
    except Exception as e:
        report("Entity Resolver Tests", False, str(e))

    # 3. HTML Parser & Content Cleaner Tests
    print("\n--- 3. HTML Parser & Content Cleaner ---")
    try:
        from intelligent_scraper.extraction.html_parser import HTMLParser
        from intelligent_scraper.extraction.content_cleaner import ContentCleaner

        sample_html = """
        <html>
            <head><title>Anthropic Frontier Research</title></head>
            <body>
                <nav><a href='/home'>Home</a></nav>
                <script>console.log('ad tracker');</script>
                <article>
                    <h1>Frontier Alignment</h1>
                    <p>New methods for scalable oversight and steering.</p>
                    <a href='https://github.com/anthropics/evals'>GitHub Code</a>
                </article>
                <footer>Legal footer notice</footer>
            </body>
        </html>
        """
        parser = HTMLParser()
        cleaner = ContentCleaner()

        title = parser.extract_title(sample_html)
        report("HTMLParser extract title", title == "Anthropic Frontier Research")

        links = parser.extract_links(sample_html, "https://anthropic.com")
        report("HTMLParser extract links", "https://github.com/anthropics/evals" in links)

        cleaned = cleaner.clean_content(sample_html)
        report("ContentCleaner removes nav and script", "Home" not in cleaned and "ad tracker" not in cleaned and "Frontier Alignment" in cleaned)
    except Exception as e:
        report("HTML Parser Tests", False, str(e))

    # 4. URL Frontier & Priority Queue Tests
    print("\n--- 4. URL Frontier & Deduplication ---")
    try:
        from intelligent_scraper.discovery.url_frontier import URLFrontier

        frontier = URLFrontier()
        t1 = await frontier.enqueue("https://example.com/ai", "src1", priority=10)
        report("URLFrontier enqueue task", t1 is not None and t1.priority == 10)

        t_dup = await frontier.enqueue("https://example.com/ai", "src1")
        report("URLFrontier prevent duplicate URL", t_dup is None)

        t2 = await frontier.enqueue("https://example.com/urgent", "src1", priority=2)
        batch = await frontier.dequeue(batch_size=2)
        report("URLFrontier priority dequeuing", len(batch) == 2 and batch[0].priority == 2)
    except Exception as e:
        report("URL Frontier Tests", False, str(e))

    # 5. Content Chunker & Payload Management (HTTP 413)
    print("\n--- 5. Content Chunker & Payload Reducer ---")
    try:
        from intelligent_scraper.extraction.content_chunker import ContentChunker

        chunker = ContentChunker(max_tokens=20)
        long_text = "Paragraph 1 with text content.\n\nParagraph 2 with different text content.\n\nParagraph 3 extra content."
        chunks = chunker.create_chunks(long_text)
        report("ContentChunker creates semantic chunks", len(chunks) >= 2)

        merged = chunker.merge_chunk_results([
            {"entityName": "OpenAI", "employeeCount": None},
            {"entityName": "OpenAI", "employeeCount": 1500}
        ])
        report("ContentChunker merges chunk results", merged.get("employeeCount") == 1500)
    except Exception as e:
        report("Content Chunker Tests", False, str(e))

    # 6. Database Repositories & Deduplication Fingerprints
    print("\n--- 6. Storage & Database Repositories ---")
    try:
        from intelligent_scraper.storage.database import DatabaseManager
        from intelligent_scraper.storage.repositories.entity_repository import EntityRepository
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = (Path(tmpdir) / "test.db").as_posix()
            db = DatabaseManager(db_url=f"sqlite+aiosqlite:///{db_path}")
            await db.init_models()

            async for session in db.get_session():
                repo = EntityRepository(session)
                s = await repo.save_startup("OpenAI", 1500, "test_dir", "https://openai.com", "fp_openai_1")
                report("EntityRepository save startup", s.entity_name == "OpenAI")

                all_s = await repo.get_all_startups()
                report("EntityRepository query startups", len(all_s) == 1)

            await db.close()
    except Exception as e:
        report("Database Storage Tests", False, str(e))

    # 7. End-to-End Pipeline & 6-Tab Export Test
    print("\n--- 7. End-to-End Pipeline & Google Sheets / CSV Export ---")
    try:
        from intelligent_scraper.orchestration.pipeline import IngestionPipeline
        from intelligent_scraper.discovery.source_registry import SourceConfig
        from intelligent_scraper.discovery.url_frontier import CrawlTask
        from intelligent_scraper.core.enums import SourceCategory
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = (Path(tmpdir) / "e2e_test.db").as_posix()
            db = DatabaseManager(db_url=f"sqlite+aiosqlite:///{db_path}")
            pipeline = IngestionPipeline(db=db)
            await pipeline.initialize()

            # Mock adaptive fetcher so no real external network call blocks test
            test_html = """
            <html><head><title>Anthropic Raises New Funding Round</title></head>
            <body><article>
            <h1>Anthropic Raises New Funding Round</h1>
            <p>Anthropic announced today a major strategic investment to accelerate safe AI systems.</p>
            </article></body></html>
            """
            pipeline.adaptive_fetcher.fetch = AsyncMock(return_value={
                "status_code": 200,
                "response_headers": {},
                "html_content": test_html,
                "final_url": "https://techcrunch.com/anthropic-announcement"
            })

            src = SourceConfig(name="techcrunch_test", base_url="https://techcrunch.com", category=SourceCategory.NEWS_WEBSITE)
            task = CrawlTask(priority=1, task_id="t-1", url="https://techcrunch.com/anthropic-announcement", source_id="techcrunch_test")

            entity = await pipeline.process_crawl_task(task, src)
            report("IngestionPipeline process task successfully", entity is not None)
            report("IngestionPipeline collected news item", len(pipeline.collected_news) == 1)

            # Export across all 6 tabs
            exports = pipeline.export_all_tabs()
            report("SheetsExporter generates Tab 1 (Startups)", "startups" in exports)
            report("SheetsExporter generates Tab 2 (Products)", "products" in exports)
            report("SheetsExporter generates Tab 3 (Research Papers)", "research_papers" in exports)
            report("SheetsExporter generates Tab 4 (Jobs)", "jobs" in exports)
            report("SheetsExporter generates Tab 5 (News)", "news" in exports and exports["news"]["count"] == 1)
            report("SheetsExporter generates Tab 6 (Entity Mapping Log)", "mapping_logs" in exports)

            await pipeline.shutdown()
    except Exception as e:
        report("E2E Pipeline Tests", False, f"{e}\n{traceback.format_exc()}")

    print("\n==================================================")
    print(f"Results: {passed} PASSED, {failed} FAILED")
    print("==================================================")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
