"""
News Article Entity Schema.
Adheres to SRS 4.5 and LLD 7.6.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from intelligent_scraper.schemas.base import BaseEntity, SourceMetadata


class NewsData(BaseModel):
    title: str = Field(..., description="Article title")
    article_url: str = Field(..., description="Direct article URL")
    full_text: str = Field(..., description="Full text content of the news article")
    published_date: datetime = Field(..., description="Publication timestamp")
    summary: Optional[str] = Field(None, description="Optional brief summary")


class NewsEntity(BaseEntity):
    recordType: str = Field(default="NEWS", description="Fixed value: NEWS")
    source: SourceMetadata
    content: NewsData
