"""Integration tests for Database and Repositories."""
import pytest
from datetime import datetime, timezone
from intelligent_scraper.storage.database import DatabaseManager
from intelligent_scraper.storage.repositories.entity_repository import EntityRepository
from intelligent_scraper.storage.repositories.source_repository import SourceRepository


@pytest.mark.asyncio
async def test_database_persistence_sqlite(tmp_path):
    test_db_url = f"sqlite+aiosqlite:///{tmp_path.as_posix()}/test.db"
    db = DatabaseManager(db_url=test_db_url)
    await db.init_models()

    async for session in db.get_session():
        source_repo = SourceRepository(session)
        src = await source_repo.upsert(
            name="test_src",
            base_url="https://test.com",
            category="startup_directory",
            config={"rate_limit": 1.0}
        )
        assert src.name == "test_src"

        entity_repo = EntityRepository(session)
        startup = await entity_repo.save_startup(
            entity_name="OpenAI",
            employee_count=1200,
            source_name="test_src",
            source_url="https://openai.com",
            fingerprint="startup:openai"
        )
        assert startup.entity_name == "OpenAI"

        all_startups = await entity_repo.get_all_startups()
        assert len(all_startups) == 1
        assert all_startups[0].entity_name == "OpenAI"

    await db.close()
