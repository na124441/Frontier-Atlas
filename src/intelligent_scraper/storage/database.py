"""
Database Engine and Session Configuration.
Supports PostgreSQL (asyncpg) and SQLite (aiosqlite) with connection pooling.
Adheres to LLD Section 4.1, 4.2.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from intelligent_scraper.config.settings import Settings, get_settings

Base = declarative_base()


class DatabaseManager:
    """Manages Async SQLAlchemy engine and session lifecycle."""

    def __init__(self, db_url: str = None):
        settings = get_settings()
        self.db_url = db_url or settings.DATABASE_URL

        # Ensure sqlite directories exist if using sqlite
        if "sqlite" in self.db_url:
            import os
            self.db_url = self.db_url.replace("\\", "/")
            os.makedirs("./data", exist_ok=True)

        engine_kwargs = {"echo": False, "future": True}
        if "postgresql" in self.db_url:
            engine_kwargs.update({
                "pool_size": 20,
                "max_overflow": 10,
                "pool_pre_ping": True
            })

        self.engine = create_async_engine(self.db_url, **engine_kwargs)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def init_models(self) -> None:
        """Creates all registered database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependency for acquiring scoped database session."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Disposes engine pool."""
        await self.engine.dispose()


# Global default database instance
db_manager = DatabaseManager()
