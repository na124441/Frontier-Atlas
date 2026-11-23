"""
Raw Document Database Model.
Preserves raw HTML/content for provenance and reproducible audits.
Adheres to LLD Section 11.1.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from intelligent_scraper.storage.database import Base


class RawDocumentModel(Base):
    __tablename__ = "raw_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crawl_task_id = Column(String(36), nullable=True, index=True)
    source_url = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    raw_content_location = Column(Text, nullable=True)
    cleaned_content = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    extraction_status = Column(String(30), default="PENDING")
