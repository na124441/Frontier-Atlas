"""
Source Database Model.
Adheres to LLD Section 11.1.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON
from intelligent_scraper.storage.database import Base


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    base_url = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
