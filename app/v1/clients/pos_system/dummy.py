"""Dummy client."""

from typing import Optional
from app.v1.models import Client
from app.v1.clients.pos_system.base import SystemProvider


class DummyConnector(SystemProvider):
    """Class to manage PIRPOS connection."""

    def get_client(self, document: int) -> Optional[Client]:
        """Get client by document.

        Args:
            document (int): Document to search.

        Raises:
            FetchDataError: Raised when can't download PirPos clients.

        Returns:
            Optional[Client]: Client found.
        """
        return None

    def upload_client(self, client: Client) -> None:
        """Upload client data to the POS system.

        Args:
            client (Client): Client to upload.
        """
        return None

    def update_client(self, client: Client) -> None:
        """Update client to POS system.

        Args:
            client (Client): Client to update.
        """
        return None
