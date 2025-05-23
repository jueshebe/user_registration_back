"""System provider Base Object."""
from abc import ABC, abstractmethod
from typing import Optional
from app.v1.models import Client, Invoice


class SystemProvider(ABC):
    """Base class to define all POS technology providers."""

    @abstractmethod
    def get_client(self, document: int) -> Optional[Client]:
        """Get client by document."""

    @abstractmethod
    def upload_client(self, client: Client) -> None:
        """Upload client in the POS system."""

    @abstractmethod
    def update_client(self, client: Client) -> None:
        """Update client in the POS system."""

    @abstractmethod
    def get_invoice(self, prefix: str, number: int) -> Optional[Invoice]:
        """Get a specific invoice."""
