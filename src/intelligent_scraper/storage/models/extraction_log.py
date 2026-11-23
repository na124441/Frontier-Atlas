"""
Extraction Log Model.
Tracks LLM execution history, provider choices, retry attempts, and errors.
Adheres to LLD Section 11.1.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from intelligent_scraper.storage.database import Base


class ExtractionLogModel(Base):
    __tablename__ = "extraction_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), nullable=True, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
