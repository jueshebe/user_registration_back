"""POS systems utils."""

from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict, Any
from enum import Enum
from app.v1.models import Client, Responsibilities, DocumentType, CityDetail


class CityDetailValidator(BaseModel):
    """Validate city details."""

    cityCode: str
    countryCode: str
    stateCode: str
    stateName: str
    cityName: str


class DocumentName(str, Enum):
    """Document name."""

    REGISTRO_CIVIL = "Registro civil"
    TARJETA_IDENTIDAD = "Tarjeta de identidad"
    CEDULA_CIUDADANIA = "Cédula de ciudadanía"
    TARJETA_EXTRANJERIA = "Tarjeta de extranjería"
    CEDULA_EXTRANJERIA = "Cédula de extranjería"
    NIT = "NIT"
    PASAPORTE = "Pasaporte"
    TIPO_DOCUMENTO_EXTRANJERO = "Tipo de documento de extranjero"
    SIN_IDENTIFICAR = "Sin identificar"
    PEP = "Permiso Especial de Permanencia"
    PPT = "Permiso Protección Temporal"
    NIT_OTRO_PAIS = "NIT de otro país"
    NUIP = "NUIP"


class ResponsibilityName(str, Enum):
    """Document name."""

    O_13 = "Gran contribuyente"
    O_15 = "Autorretenedor"
    O_23 = "Agente de retención IVA"
    O_47 = "Régimen simple de tributación"
    R_99_PN = "No responsable"


mapping_name_document_type = {
    11: DocumentName.REGISTRO_CIVIL,
    12: DocumentName.TARJETA_IDENTIDAD,
    13: DocumentName.CEDULA_CIUDADANIA,
    21: DocumentName.TARJETA_EXTRANJERIA,
    22: DocumentName.CEDULA_EXTRANJERIA,
    31: DocumentName.NIT,
    41: DocumentName.PASAPORTE,
    42: DocumentName.TIPO_DOCUMENTO_EXTRANJERO,
    43: DocumentName.SIN_IDENTIFICAR,
    47: DocumentName.PEP,
    48: DocumentName.PPT,
    50: DocumentName.NIT_OTRO_PAIS,
    91: DocumentName.NUIP,
}


mapping_responsibility_name = {
    "O_13": ResponsibilityName.O_13,
    "O_15": ResponsibilityName.O_15,
    "O_23": ResponsibilityName.O_23,
    "O_47": ResponsibilityName.O_47,
    "R-99-PN": ResponsibilityName.R_99_PN,
}


class ClientResponseValidator(BaseModel):
    """Validate clients response from PirPos."""

    name: str
    document: int
    idDocumentType: DocumentType
    documentName: Optional[str] = None
    cityDetail: Optional[CityDetailValidator] = None
    isSocialReason: Optional[bool] = None
    responsibilities: Optional[Responsibilities] = None
    responsibilityName: Optional[str] = None
    lastName: Optional[str] = None
    checkDigit: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @model_validator(mode='before')
    def check_model(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check model."""
        if values["idDocumentType"]:
            if isinstance(values["idDocumentType"], DocumentType):
                values["idDocumentType"] = values["idDocumentType"].value
            values["documentName"] = mapping_name_document_type[values["idDocumentType"]].value

        if values["responsibilities"]:
            if isinstance(values["responsibilities"], Responsibilities):
                values["responsibilities"] = values["responsibilities"].value
            values["responsibilityName"] = mapping_responsibility_name[values["responsibilities"]].value

        return values


class ClientsResponseValidator(BaseModel):
    """Validate clients response from PirPos."""

    data: list[ClientResponseValidator]


def define_client_from_pirpos_response(
    raw_clients: List[ClientResponseValidator],
) -> List[Client]:
    """Create client object."""
    clients: List[Client] = []
    for raw_client in raw_clients:
        responsibilites = (
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
            last_name=raw_client.lastName,
            email=email,
            document=raw_client.document,
            check_digit=raw_client.checkDigit,
            document_type=raw_client.idDocumentType,
            phone=raw_client.phone,
            address=raw_client.address,
            responsibilities=responsibilites,
            city_detail=city_detail,
        )
        clients.append(client)
    return clients


def define_payload_from_client(client: Client) -> str:
    """Create payload to upload client to PirPos.

    Args:
        client (Client): Client to upload.

    Returns:
        str: Payload to upload client to PirPos.
    """
    is_social_reason = True if client.document_type == DocumentType.NIT else False

    if client.city_detail:
        city_detail = CityDetailValidator(
            cityCode=client.city_detail.city_code,
            countryCode=client.city_detail.country_code,
            stateCode=client.city_detail.state_code,
            stateName=client.city_detail.city_state,
            cityName=client.city_detail.city_name,
        )
    else:
        city_detail = None

    payload_object = ClientResponseValidator(
        name=client.name,
        document=client.document,
        idDocumentType=client.document_type,
        cityDetail=city_detail,
        isSocialReason=is_social_reason,
        responsibilities=client.responsibilities,
        lastName=client.last_name,
        checkDigit=client.check_digit,
        email=client.email,
        phone=client.phone,
        address=client.address,
    )
    json_data = payload_object.json(exclude_none=True)
    return json_data
