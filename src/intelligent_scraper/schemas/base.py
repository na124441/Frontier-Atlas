"""
Base entity schemas and metadata models.
Adheres to LLD Section 7.1.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class SourceMetadata(BaseModel):
    name: str = Field(..., description="Source website name")
    url: str = Field(..., description="Original source URL")


class BaseEntity(BaseModel):
    schemaVersion: str = Field(default="1.0", description="Schema version")
    recordType: str = Field(..., description="Discriminator record type")
    collectedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 collection timestamp"
    )
