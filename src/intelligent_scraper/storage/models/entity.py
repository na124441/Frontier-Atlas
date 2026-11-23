"""
Entity Models for Structured Intelligence.
Covers Startups, Products, Research Papers, Jobs, News, Canonical Entities, and Mappings.
Adheres to SRS Section 4 and LLD Section 11.1.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, UniqueConstraint
from intelligent_scraper.storage.database import Base


class CanonicalEntityModel(Base):
    __tablename__ = "canonical_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = Column(String(200), unique=True, nullable=False, index=True)
    entity_type = Column(String(50), default="STARTUP")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class EntityMappingModel(Base):
    __tablename__ = "entity_mappings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_name = Column(String(255), nullable=False, index=True)
    canonical_name = Column(String(200), nullable=False)
    canonical_entity_id = Column(String(36), nullable=True)
    matching_method = Column(String(50), default="DETERMINISTIC")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class StartupModel(Base):
    __tablename__ = "startups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_name = Column(String(200), nullable=False, index=True)
    employee_count = Column(Integer, nullable=True)
    source_name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    startup_name = Column(String(200), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    pricing_model = Column(String(50), nullable=False)
    source_name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)


class ResearchPaperModel(Base):
    __tablename__ = "research_papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(Text, nullable=False)
    authors = Column(JSON, default=list)
    paper_url = Column(Text, nullable=False)
    github_url = Column(Text, nullable=True)
    github_stars = Column(Integer, nullable=True)
    published_date = Column(DateTime, nullable=False, index=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company = Column(String(200), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    job_url = Column(Text, nullable=True)
    is_remote = Column(Boolean, default=False)
    role_family = Column(String(100), nullable=False)
    published_date = Column(DateTime, nullable=False, index=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)


class NewsModel(Base):
    __tablename__ = "news"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(Text, nullable=False)
    article_url = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)
    published_date = Column(DateTime, nullable=False, index=True)
    source_name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)
