"""POS systems utils."""

from pydantic import BaseModel
from typing import List, Optional
from app.v1.models import Client, Responsibilities, DocumentType, CityDetail


class CittyDetailValidator(BaseModel):
    """Validate city details."""

    cityCode: str
    countryCode: str
    stateCode: str
    stateName: str
    cityName: str


class ClientResponseValidator(BaseModel):
    """Validate clients response from PirPos."""

    name: str
    document: int
    idDocumentType: DocumentType
    cityDetail: Optional[CittyDetailValidator] = None
    isSocialReason: Optional[bool] = None
    responsibilities: Optional[Responsibilities] = None
    lastName: Optional[str] = None
    checkDigit: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientsResponseValidator(BaseModel):
    """Validate clients response from PirPos."""

    data: list[ClientResponseValidator]


def define_client_from_pirpos_response(
    raw_clients: List[ClientResponseValidator],
) -> List[Client]:
    """Create client object."""
    clients: List[Client] = []
    for raw_client in raw_clients:
        responsabilites = (
            raw_client.responsibilities
            if raw_client.responsibilities
            else Responsibilities.R_99_PN
        )
        email = raw_client.email if raw_client.email else ""
        if raw_client.cityDetail:
            raw_city_detail = raw_client.cityDetail
            city_detail = CityDetail(
                city_name=raw_city_detail.cityName,
                city_state=raw_city_detail.stateName,
                city_code=raw_city_detail.cityCode,
                country_code=raw_city_detail.countryCode,
                state_code=raw_city_detail.stateCode,
            )
        else:
            city_detail = None

        client = Client(
            name=raw_client.name,
            email=email,
            document=raw_client.document,
            check_digit=raw_client.checkDigit,
            document_type=raw_client.idDocumentType,
            phone=raw_client.phone,
            address=raw_client.address,
            responsibilities=responsabilites,
            city_detail=city_detail,
        )
        clients.append(client)
    return clients
