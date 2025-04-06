"""Utils users view."""

from typing import Union
from pydantic import BaseModel, field_validator
from email_validator import validate_email
from app.v1.models import DocumentType, Client


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
            except ValueError as error:
                raise ValueError(f"Invalid document type: {value}") from error
        if isinstance(value, int):
            return value
        raise ValueError(f"Invalid document type: {value}")


def validate_user(user: Client) -> None:
    """Validate user data."""
    validate_email(str(user.email))

    if not user.name or user.name == "":
        raise ValueError("Name is required")

    if user.document_type == DocumentType.NIT:
        if not user.check_digit:
            raise ValueError("Check digit is required")
