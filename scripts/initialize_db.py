"""
Operational Script: Database Initialization.
Creates tables and loads seed entities.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligent_scraper.config.logging_config import setup_logging
from intelligent_scraper.storage.database import db_manager
from intelligent_scraper.intelligence.entity_resolver import EntityResolver
from intelligent_scraper.storage.repositories.entity_repository import EntityRepository

logger = logging.getLogger("initialize_db")


async def main():
    setup_logging(level="INFO")
    logger.info("Initializing database tables...")
    await db_manager.init_models()

    logger.info("Loading seed entities into database...")
    resolver = EntityResolver("./data/seed/ai_startups_seed.json")

    async for session in db_manager.get_session():
        repo = EntityRepository(session)
        for canonical in resolver.canonical_entities:
            await repo.save_mapping(raw_name=canonical, canonical_name=canonical, method="SEED")

    logger.info(f"Successfully seeded {len(resolver.canonical_entities)} AI startups.")
    await db_manager.close()
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    asyncio.run(main())
