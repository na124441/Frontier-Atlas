"""
Main Application Entrypoint.
Command-line interface to orchestrate the Intelligent Web Scraping & AI-Powered Data Intelligence Platform.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure src is in python path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligent_scraper.config.settings import settings
from intelligent_scraper.config.logging_config import setup_logging
from intelligent_scraper.orchestration.pipeline import IngestionPipeline

logger = logging.getLogger("intelligent_scraper")


async def async_main():
    parser = argparse.ArgumentParser(
        description="Intelligent Web Scraping & AI-Powered Data Intelligence Platform"
    )
    parser.add_argument(
        "--mode",
        choices=["run", "discover", "export", "init-db"],
        default="run",
        help="Pipeline execution mode (default: run)"
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=50,
        help="Maximum tasks to process in batch (default: 50)"
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Format logs as structured JSON"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    args = parser.parse_args()

    # Configure structured logging
    setup_logging(level=args.log_level, json_format=args.json_logs)
    logger.info(f"Starting Intelligent Web Scraper [Version {settings.VERSION}] in mode '{args.mode}'...")

    pipeline = IngestionPipeline()
    await pipeline.initialize()

    try:
        if args.mode == "init-db":
            logger.info("Database schemas initialized successfully.")
            return

        if args.mode in ("discover", "run"):
            logger.info("Phase 1: Discovering URLs from registered sources...")
            discovered_count = await pipeline.run_discovery_for_sources(max_per_source=10)
            logger.info(f"Discovered {discovered_count} candidate URLs.")

        if args.mode == "run":
            logger.info(f"Phase 2: Processing crawl & extraction pipeline (max {args.max_tasks})...")
            run_summary = await pipeline.run_pipeline(max_tasks=args.max_tasks)
            logger.info(f"Pipeline run summary: {run_summary}")

        if args.mode in ("export", "run"):
            logger.info("Phase 3: Exporting data across 6 Google Sheets tabs / CSV files...")
            export_summary = pipeline.export_all_tabs()
            logger.info("Export completed successfully.")
            for tab, res in export_summary.items():
                if isinstance(res, dict) and "csv_path" in res:
                    logger.info(f"  - Tab '{res['tab']}': {res['count']} rows -> {res['csv_path']}")

    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user.")
    except Exception as e:
        logger.critical(f"Fatal error in pipeline: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await pipeline.shutdown()


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
