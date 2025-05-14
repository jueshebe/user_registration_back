"""PirPos client."""

from typing import Optional, Dict
import os
import json
from logging import Logger
import logging
import requests
from app.v1.models import Client, Invoice
from app.v1.clients.pos_system.base import SystemProvider
from app.v1.clients.pos_system.utils import (
    define_payload_from_client,
    get_clients_by_filter,
    get_invoice_from_json
)
from app.v1.utils.errors import CredentialsError, SendDataError, FetchDataError


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
        self.__pirpos_domain = "https://api.pirpos.com"
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
        url = f"{self.__pirpos_domain}/login"
        values = {
            "name": "",
            "email": self.__pirpos_username,
            "password": self.__pirpos_password,
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url, data=json.dumps(values), headers=headers, timeout=20
        )

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
        """Get headers with credentials.

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
        clients, _ = get_clients_by_filter(self.__pirpos_domain, str(document), headers)

        if len(clients) == 0:
            return None

        if len(clients) == 1:
            return clients[0]

        if len(clients) > 1:
            for client in clients:
                if client.document == document:
                    return client

        self.__logger.warning(
            "More than one client found for id %s. Using the first element",
            document,
        )
        return clients[0]

    def upload_client(self, client: Client) -> None:
        """Upload client data to the POS system.

        Args:
            client (Client): Client to upload.
        """
        current_client = self.get_client(client.document)
        if current_client and current_client.document == client.document:
            raise SendDataError("Client already exists in PirPos")

        headers = self.__get_headers()
        url = f"{self.__pirpos_domain}/clients"
        payload: str = define_payload_from_client(client)

        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload, timeout=20
            )
        except Exception as error:
            raise SendDataError(
                f"Can't create a customer in PirPos\n {error}"
            ) from error
        if not response.ok:
            raise SendDataError(f"Can't create a customer in PirPos\n {response.text}")

    def update_client(self, client: Client) -> None:
        """Update client to POS system.

        Args:
            client (Client): Client to update.
        """
        headers = self.__get_headers()
        clients, ids = get_clients_by_filter(self.__pirpos_domain, str(client.document), headers)

        if len(clients) == 0:
            raise SendDataError(
                f"Can't update a client. No client found for document: {client.document}"
            )

        clients_with_same_document = [
            (found_client, id)
            for found_client, id in zip(clients, ids)
            if found_client.document == client.document
        ]

        if len(clients_with_same_document) > 1:
            raise SendDataError(
                f"Can't update a client. More than one client found for document: {client.document}"
            )
        url = f"{self.__pirpos_domain}/clients"
        payload: str = define_payload_from_client(
            client, clients_with_same_document[0][1]
        )

        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload, timeout=20
            )
        except Exception as error:
            raise SendDataError(f"Can't update customer in PirPos\n {error}") from error
        if not response.ok:
            raise SendDataError(f"Can't update customer in PirPos\n {response.text}")

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get a specific invoice."""
        headers = self.__get_headers()
        url = f"{self.__pirpos_domain}/invoices"
        params = {"number": invoice_id}
        try:
            response = requests.request(
                "GET", url, headers=headers, params=params, timeout=20
            )
        except Exception as error:
            raise FetchDataError(
                f"Can't get an invoice from PirPos\n {error}"
            ) from error
        if not response.ok:
            raise FetchDataError(f"Non 200 response getting an invoice from PirPos\n {response.text}")
        return get_invoice_from_json(response.json(), invoice_id)


if __name__ == "__main__":
    user_name = os.getenv("PIRPOS_USER_NAME")
    user_password = os.getenv("PIRPOS_PASSWORD")

    if user_name is None or user_password is None:
        raise ValueError("PIRPOS_USER_NAME and PIRPOS_PASSWORD must be set")

    connector = PirposConnector(user_name, user_password, logging.getLogger())
    # test_client = connector.get_client(90038794)
    # new_client = Client(
    #     name="julian2",
    #     last_name="herrera",
    #     document=123456789,
    #     document_type=11,  # type: ignore
    # )
    # connector.upload_client(new_client)
    # new_client.name = "julian3"
    # connector.update_client(new_client)

    invoice = connector.get_invoice("FVE", 29984)
    print(invoice)
