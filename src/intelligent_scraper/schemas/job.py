"""
Job Posting Entity Schema.
Adheres to SRS 4.4 and LLD 7.5.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from intelligent_scraper.schemas.base import BaseEntity, SourceMetadata


class JobData(BaseModel):
    company: str = Field(..., description="Canonical company name")
    date: datetime = Field(..., description="Publication timestamp")
    is_remote: bool = Field(default=False, description="Remote eligibility")
    role_family: str = Field(..., description="Functional job category (e.g. Engineering, Research)")
    title: Optional[str] = Field(None, description="Job title")
    job_url: Optional[str] = Field(None, description="Direct URL to posting")


class JobEntity(BaseEntity):
    recordType: str = Field(default="JOB", description="Fixed value: JOB")
    source: Optional[SourceMetadata] = None
    content: JobData
