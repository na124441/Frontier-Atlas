"""
Crawl Task Database Model.
Adheres to LLD Section 11.1.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, UniqueConstraint
from intelligent_scraper.storage.database import Base


class CrawlTaskModel(Base):
    __tablename__ = "crawl_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), nullable=False, index=True)
    url = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING", index=True)
    priority = Column(Integer, default=10)
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("source_id", "url", name="uq_source_url"),
    )
