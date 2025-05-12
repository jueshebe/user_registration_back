"""Model for products."""
from typing import List
from pydantic import BaseModel, field_validator
from app.v1.utils.utils import normalize


class TaxInfo(BaseModel):
    """Stock information."""

    tax_name: str
    value: float


class Product(BaseModel):
    """Product info."""

    product_id: str
    name: str
    price: float
    taxes: List[TaxInfo]

    @field_validator("name")
    @classmethod
    def clean_name(cls, name: str) -> str:
        """Remove upercase and accents."""
        return normalize(name)
