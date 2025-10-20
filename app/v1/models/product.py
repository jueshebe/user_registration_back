"""Model for products."""
from typing import List
from pydantic import BaseModel, field_validator
from app.v1.utils.utils import normalize


class ProductTaxInfo(BaseModel):
    """Stock information."""

    tax_name: str
    value: float


class Product(BaseModel):
    """Product info."""

    product_id: str
    name: str
    base_price: float
    total_price: float
    taxes: List[ProductTaxInfo]

    @field_validator("name")
    @classmethod
    def clean_name(cls, name: str) -> str:
        """Remove upercase and accents."""
        return normalize(name)
