"""
Research Paper Entity Schema.
Adheres to SRS 4.3 and LLD 7.4.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from intelligent_scraper.schemas.base import BaseEntity, SourceMetadata


class ResearchPaperData(BaseModel):
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="Author names")
    paper_url: str = Field(..., description="Arxiv or PDF URL")
    github_url: Optional[str] = Field(None, description="Associated GitHub URL if available")
    github_stars: Optional[int] = Field(None, description="Current GitHub stars")
    published_date: datetime = Field(..., description="Publication timestamp")


class ResearchPaperEntity(BaseEntity):
    recordType: str = Field(default="RESEARCH_PAPER", description="Fixed value: RESEARCH_PAPER")
    source: Optional[SourceMetadata] = None
    content: ResearchPaperData
