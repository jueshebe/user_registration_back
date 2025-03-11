"""Users Manager module."""
from typing import Optional
from logging import Logger
from app.v1.clients import SystemProvider
from app.v1.models import Client


class UsersManager():
    """Class to manage users."""

    def __init__(self, connector: SystemProvider, logger: Logger):
        """Initialize the users manager.

        Args:
            connector (SystemProvider): Connector to the system.
            logger (Logger): Logger to use.
        """
        self.__connector = connector
        self.__logger = logger

    def get_user(self, document: int) -> Optional[Client]:
        """Get user by document.

        Args:
            document (int): Document to search.

        Returns:
            dict: User data.
        """
        user = self.__connector.get_client(document)
        return user

    def upload_user(self, user: Client) -> None:
        """Upload user in the system.

        Args:
            user (dict): User data.
        """
        self.__connector.upload_client(user)

    def update_user(self, user: Client) -> None:
        """Update user in the system.

        Args:
            user (dict): User data.
        """
        self.__connector.update_client(user)
