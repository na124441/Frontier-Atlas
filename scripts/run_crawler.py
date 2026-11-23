"""
Operational Script: Run Crawler Pipeline.
Executes source discovery, adaptive crawling, LLM extraction, and persistence.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligent_scraper.config.logging_config import setup_logging
from intelligent_scraper.orchestration.pipeline import IngestionPipeline

logger = logging.getLogger("run_crawler")


async def main():
    parser = argparse.ArgumentParser(description="Run Intelligent Web Scraper pipeline")
    parser.add_argument("--limit", type=int, default=20, help="Max tasks to crawl")
    parser.add_argument("--json-logs", action="store_true", help="Log in JSON format")
    args = parser.parse_args()

    setup_logging(level="INFO", json_format=args.json_logs)
    logger.info(f"Starting crawler pipeline (task limit: {args.limit})...")

    pipeline = IngestionPipeline()
    await pipeline.initialize()

    try:
        discovered = await pipeline.run_discovery_for_sources(max_per_source=5)
        logger.info(f"Discovered {discovered} tasks.")
        summary = await pipeline.run_pipeline(max_tasks=args.limit)
        logger.info(f"Execution complete: {summary}")

        # Automatically export data
        exports = pipeline.export_all_tabs()
        logger.info("Export generated for all 6 tabs.")
    finally:
        await pipeline.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
