"""
Startup Entity Schema.
Adheres to SRS 4.1 and LLD 7.2.
"""

from typing import Optional
from pydantic import BaseModel, Field
from intelligent_scraper.schemas.base import BaseEntity, SourceMetadata


class StartupData(BaseModel):
    entityName: str = Field(..., description="Canonical startup name")
    employeeCount: Optional[int] = Field(None, description="Employee count if available")


class StartupEntity(BaseEntity):
    recordType: str = Field(default="STARTUP", description="Fixed value: STARTUP")
    source: SourceMetadata
    content: StartupData
