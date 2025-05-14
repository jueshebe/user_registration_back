"""Invoices Manager module."""
from typing import Optional
from app.v1.clients import SystemProvider
from app.v1.models import Invoice


class InvoicesManager():
    """Class to manage Invoices."""

    def __init__(self, connector: SystemProvider):
        """Initialize the users manager.

        Args:
            connector (SystemProvider): Connector to the system.
            logger (Logger): Logger to use.
        """
        self.__connector = connector

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get an invoice.

        Args:
            invoice_id (str): invoice identifier.

        Returns:
            Optional[Invoice]: required invoice.
        """
        invoice = self.__connector.get_invoice(invoice_id)
        return invoice
