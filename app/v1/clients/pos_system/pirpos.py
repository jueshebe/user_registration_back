"""PirPos client."""

from typing import List, Optional, Dict, Any
import os
import json
from logging import Logger
import logging
import requests
from app.v1.models import Client
from app.v1.clients.pos_system.base import SystemProvider
from app.v1.clients.pos_system.utils import (
    ClientsResponseValidator,
    ClientResponseValidator,
    define_client_from_pirpos_response,
    define_payload_from_client
)
from app.v1.utils.errors import CredentialsError, FetchDataError


class PirposConnector(SystemProvider):
    """Class to manage PIRPOS connection."""

    def __init__(
        self,
        pirpos_username: str,
        pirpos_password: str,
        logger: Logger,
    ):
        """Parameters used to make a connection."""
        self.__logger = logger
        self.__pirpos_username = pirpos_username
        self.__pirpos_password = pirpos_password
        self.__pirpos_access_token = self.__get_pirpos_access_token()
        self.__logger.info("Pirpos connector initialized.")

    def __get_pirpos_access_token(self) -> str:
        """Get pirpos access token to comunicate with the server.

        Raises
        ------
        ErrorPirposToken

        Returns
        -------
        str
            token
        """
        url = "https://api.pirpos.com/login"
        values = {
            "name": "",
            "email": self.__pirpos_username,
            "password": self.__pirpos_password,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(values), headers=headers)

        if not response.ok:
            raise CredentialsError(
                "Error getting Pirpos token, check email and password"
            )

        data = response.json()
        if "tokenCurrent" in data.keys():
            access_token = data["tokenCurrent"]
            assert isinstance(access_token, str)
        else:
            raise CredentialsError("tokenCurrent key is not present in the respose")

        return access_token

    def __get_headers(self) -> Dict[str, str]:
        """Get headers with credentials

        Returns:
            Dict[str, str]: Headers with credentials
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__pirpos_access_token}",
        }
        return headers

    def get_client(self, document: int) -> Optional[Client]:
        """Get client by document.

        Args:
            document (int): Document to search.

        Raises:
            FetchDataError: Raised when can't download PirPos clients.

        Returns:
            Optional[Client]: Client found.
        """
        headers = self.__get_headers()
        url = (
            "https://api.pirpos.com/clients?pagination=true"
            f"&limit=10&page=0&clientData={document}&"
        )

        try:
            response = requests.request("GET", url, headers=headers)
        except Exception as error:
            raise FetchDataError(f"Can't download PirPos clients\n {error}")
        if not response.ok:
            raise FetchDataError(f"Can't download PirPos clients\n {response.text}")

        data = response.json()
        raw_clients: List[ClientResponseValidator] = ClientsResponseValidator(
            **data
        ).data

        clients: List[Client] = define_client_from_pirpos_response(raw_clients)

        if len(clients) == 0:
            return None
        if len(clients) > 1:
            self.__logger.warning(
                "More than one client found for id %s. Using the first element",
                document,
            )
        return clients[0]

    def upload_client(self, client: Client) -> None:
        """Upload client to POS system.

        Args:
            client (Client): Client to upload.
        """
        headers = self.__get_headers()
        url = "https://api.pirpos.com/clients"
        payload: str = define_payload_from_client(client)

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except Exception as error:
            raise FetchDataError(f"Can't download PirPos clients\n {error}")
        if not response.ok:
            raise FetchDataError(f"Can't download PirPos clients\n {response.text}")


if __name__ == "__main__":
    user_name = os.getenv("PIRPOS_USER_NAME")
    user_password = os.getenv("PIRPOS_PASSWORD")

    if user_name is None or user_password is None:
        raise ValueError("PIRPOS_USER_NAME and PIRPOS_PASSWORD must be set")

    connector = PirposConnector(user_name, user_password, logging.getLogger())
    client = connector.get_client(1121923074)
    new_client = Client(
        name="julian2",
        last_name="herrera",
        document=11219230742,
        document_type=11,  # type: ignore
    )
    connector.upload_client(client)
