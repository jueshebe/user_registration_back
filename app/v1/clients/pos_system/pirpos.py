"""PirPos client."""
from typing import List, Tuple, Optional
import os
import json
from logging import Logger
import logging
import time
from datetime import datetime, timedelta
import requests
from pirpos2siigo.models import Client, Product, Invoice, InvoiceStatus
from pirpos2siigo.clients.utils import (
    load_pirpos2siigo_config,
    create_client,
    create_pirpos_product,
    create_invoice,
    ErrorPirposToken,
    ErrorLoadingPirposClients,
    ErrorLoadingPirposProducts,
    ErrorLoadingPirposInvoices,
)


class PirposConnector:
    """Class to manage pirpos invoices, products and clients."""

    def __init__(
        self,
        pirpos_username: str,
        pirpos_password: str,
        configuration_path: str,
        logger: Logger = logging.getLogger(),
    ):
        """Parameters used to make a connection."""
        self.__logger = logger
        self.__pirpos_username = pirpos_username
        self.__pirpos_password = pirpos_password
        self.__configuration = load_pirpos2siigo_config(configuration_path)
        self.__pirpos_access_token = self.__get_pirpos_access_token()
        self.__products: List[Product]
        self.__clients: List[Client]
        # self.get_pirpos_clients()
        # self.get_pirpos_products()

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
            raise ErrorPirposToken(
                "Error getting Pirpos token, check email and password"
            )

        data = response.json()
        if "tokenCurrent" in data.keys():
            access_token = data["tokenCurrent"]
            assert isinstance(access_token, str)
        else:
            raise ErrorPirposToken(
                "tokenCurrent key is not present in the respose"
            )

        return access_token

    def get_pirpos_clients(self, batch_clients: int = 200) -> None:
        """Get pirpos clients.

        Parameters
        ----------
        batch_clients : int, optional
            batch used to download clients, by default 200
        """
        page = 0
        clients: List[Client] = []
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__pirpos_access_token}",
        }

        while True:
            url = (
                "https://api.pirpos.com/clients?pagination=true"
                f"&limit={batch_clients}&page={page}&clientData=&"
            )

            response = requests.request("GET", url, headers=headers)
            if not response.ok:
                raise ErrorLoadingPirposClients(
                    f"Can't download PirPos clients\n {response.text}"
                )

            data = response.json()[
                "data"
            ]  # TODO: check incoming data with BaseModel class
            if len(data) == 0:
                break

            for client_data in data:
                name = client_data["name"]
                client = create_client(
                    configuration_file=self.__configuration,
                    name=name,
                    siigo_id=None,
                    pirpos_id=client_data.get("_id"),
                    email=client_data.get("email"),
                    phone=client_data.get("phone"),
                    address=client_data.get("address"),
                    document=client_data.get("document"),
                    check_digit=client_data.get("checkDigit"),
                    document_type=client_data.get("idDocumentType"),
                    responsibilities=client_data.get("responsibilities"),
                    city_name=client_data.get("cityDetail", {}).get("cityName"),
                    city_state=client_data.get("cityDetail", {}).get(
                        "stateName"
                    ),
                    city_code=client_data.get("cityDetail", {}).get("cityCode"),
                    country_code=client_data.get("cityDetail", {}).get(
                        "countryCode"
                    ),
                    state_code=client_data.get("cityDetail", {}).get(
                        "stateCode"
                    ),
                )
                clients.append(client)
            page += 1

        self.__clients = clients

    @property
    def clients(self) -> List[Client]:
        """Getter for clients."""
        return self.__clients


if __name__ == "__main__":
    user_name = os.getenv("PIRPOS_USER_NAME")
    user_password = os.getenv("PIRPOS_PASSWORD")
    PATH = (
        "/Users/julianestehe/Programs/asadero/pirpos2siigo/configuration.JSON"
    )
    PATH = "/home/julian/projects/pirpos2siigo/configuration.JSON"
    assert isinstance(user_name, str)
    assert isinstance(user_password, str)
    connector = PirposConnector(
        user_name, user_password, PATH, logging.getLogger()
    )
    # connector.get_pirpos_products()
    date_1 = datetime(2023, 1, 2)
    date_2 = datetime(2023, 1, 2)
    time_1 = time.time()
    loaded_invoices = connector.get_pirpos_invoices_per_client(date_1, date_2)
    print(time.time() - time_1)
