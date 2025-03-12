"""Utils users view."""

from typing import Union
from pydantic import BaseModel, field_validator
from app.v1.models import DocumentType


class GetClientValidator(BaseModel):
    """Get client validator."""

    document_type: DocumentType
    email: str

    @field_validator("document_type", mode="before")
    @classmethod
    def convert_document_type(cls, value: Union[str, int]) -> int:
        """Convert document type to DocumentType."""
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"Invalid document type: {value}")
        if isinstance(value, int):
            return value
        raise ValueError(f"Invalid document type: {value}")
