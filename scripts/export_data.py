"""
Operational Script: Export Data.
Queries database and generates the 6 Google Sheets tabs / CSV files.
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligent_scraper.config.logging_config import setup_logging
from intelligent_scraper.storage.database import db_manager
from intelligent_scraper.storage.repositories.entity_repository import EntityRepository
from intelligent_scraper.exporters.sheets_exporter import SheetsExporter

logger = logging.getLogger("export_data")


async def main():
    setup_logging(level="INFO")
    logger.info("Exporting records from database to 6 Google Sheets tabs / CSV files...")

    exporter = SheetsExporter()

    async for session in db_manager.get_session():
        repo = EntityRepository(session)
        startups = await repo.get_all_startups()
        products = await repo.get_all_products()
        papers = await repo.get_all_research_papers()
        jobs = await repo.get_all_jobs()
        news = await repo.get_all_news()
        mappings = await repo.get_all_mappings()

        mapping_dicts = [
            {"raw_name": m.raw_name, "canonical_name": m.canonical_name, "matching_method": m.matching_method}
            for m in mappings
        ]

        result = exporter.export_all(
            startups=startups,
            products=products,
            research_papers=papers,
            jobs=jobs,
            news=news,
            mapping_logs=mapping_dicts
        )

        logger.info(f"Export summary:")
        for k, v in result.items():
            if isinstance(v, dict):
                logger.info(f" - {v.get('tab')}: {v.get('count')} records -> {v.get('csv_path')}")

    await db_manager.close()
    logger.info("Export script complete.")


if __name__ == "__main__":
    asyncio.run(main())
