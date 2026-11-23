"""
Product Entity Schema.
Adheres to SRS 4.2 and LLD 7.3.
"""

from pydantic import BaseModel, Field
from intelligent_scraper.core.enums import PricingModel
from intelligent_scraper.schemas.base import BaseEntity, SourceMetadata


class ProductData(BaseModel):
    startupName: str = Field(..., description="Canonical startup name")
    pricingModel: PricingModel = Field(..., description="Pricing model: FREE, FREEMIUM, PAID, ENTERPRISE")
    productName: str = Field(default="", description="Name of the product")


class ProductEntity(BaseEntity):
    recordType: str = Field(default="PRODUCT", description="Fixed value: PRODUCT")
    source: SourceMetadata
    content: ProductData
