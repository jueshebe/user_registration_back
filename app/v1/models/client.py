"""Model of a client."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class CityDetail(BaseModel):
    """City info."""

    city_name: str
    city_state: str
    city_code: str
    country_code: str  # TODO: Must be Enum
    state_code: str


class Responsibilities(Enum):
    """Dian responsibilities."""

    O_13 = "O-13"
    O_15 = "O-15"
    O_23 = "O-23"
    O_47 = "O-47"
    R_99_PN = "R-99-PN"


class DocumentType(Enum):
    """DIAN document types."""

    REGISTRO_CIVIL = 11
    TARJETA_IDENTIDAD = 12
    CEDULA_CIUDADANIA = 13
    TARJETA_EXTRANJERIA = 21
    CEDULA_EXTRANJERIA = 22
    NIT = 31
    PASAPORTE = 41
    TIPO_DOCUMENTO_EXTRANJERO = 42
    SIN_IDENTIFICAR = 43
    PEP = 47
    PPT = 48
    NIT_OTRO_PAIS = 50
    NUIP = 91


class Client(BaseModel):
    """Client info."""

    name: str
    email: str
    document: int
    check_digit: Optional[int] = None
    document_type: DocumentType
    phone: Optional[str] = None
    address: Optional[str] = None
    responsibilities: Responsibilities = Responsibilities.R_99_PN
    city_detail: Optional[CityDetail] = None
