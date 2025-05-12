"""POS systems utils."""

from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import requests
from pydantic import BaseModel, model_validator, Field
from app.v1.models import (
    Client,
    Responsibilities,
    DocumentType,
    CityDetail,
    Invoice,
    Business,
    Employee,
    Payment,
    InvoiceProduct,
    Product,
    TaxInfo
)
from app.v1.utils.errors import FetchDataError


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

    id: Optional[str] = Field(default=None, alias="_id")
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

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check model."""
        if values["idDocumentType"]:
            if isinstance(values["idDocumentType"], DocumentType):
                values["idDocumentType"] = values["idDocumentType"].value
            values["documentName"] = mapping_name_document_type[
                values["idDocumentType"]
            ].value

        if values["responsibilities"]:
            if isinstance(values["responsibilities"], Responsibilities):
                values["responsibilities"] = values["responsibilities"].value
            values["responsibilityName"] = mapping_responsibility_name[
                values["responsibilities"]
            ].value

        return values


class ClientsResponseValidator(BaseModel):
    """Validate clients response from PirPos."""

    data: List[ClientResponseValidator]


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


def define_payload_from_client(client: Client, pirpos_id: Optional[str] = None) -> str:
    """Create payload to upload client to PirPos.

    Args:
        client (Client): Client to upload.

    Returns:
        str: Payload to upload client to PirPos.
    """
    is_social_reason = client.document_type == DocumentType.NIT

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
        _id=pirpos_id,
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
    json_data = payload_object.json(exclude_none=True, by_alias=True)
    return json_data


def get_clients_by_filter(
    domain: str, search_filter: str, headers: Dict[str, Any]
) -> Tuple[List[Client], List[str]]:
    """Get pirpos clients using some filter.

    Args:
        filter(str): Filter to search.
        headers(Dict[str, Any]): Headers with credentials.

    Raises:
        FetchDataError: Raised when can't download PirPos clients.

    Returns:
        List[Client]: Clients found
    """
    url = (
        f"{domain}/clients?pagination=true"
        f"&limit=10&page=0&clientData={search_filter}&"
    )

    try:
        response = requests.request("GET", url, headers=headers, timeout=20)
    except Exception as error:
        raise FetchDataError(f"Can't download PirPos clients\n {error}") from error
    if not response.ok:
        raise FetchDataError(f"Can't download PirPos clients\n {response.text}")

    data = response.json()
    raw_clients: List[ClientResponseValidator] = ClientsResponseValidator(**data).data

    list_ids: List[str] = []
    for raw_client in raw_clients:
        if not raw_client.id:
            raise FetchDataError(
                f"Not found _id for client. document {raw_client.document}"
            )
        list_ids.append(raw_client.id)

    clients: List[Client] = define_client_from_pirpos_response(raw_clients)
    return clients, list_ids


def get_invoice_from_json(
    raw_data: List[Dict[str, Any]], prefix: str, number: int
) -> Optional[Invoice]:
    """Transform the Json data to get an Invoice object."""
    if not raw_data:
        return None
    first_invoice = raw_data[0]

    business = Business(**first_invoice["business"])

    employee_name = first_invoice["seller"]["name"]
    seller = Employee(name=employee_name, employee_id=employee_name)

    employee_name = first_invoice["cashier"]["name"]
    cachier = Employee(name=employee_name, employee_id=employee_name)

    sell_point = first_invoice["table"]["name"]

    raw_client_data = first_invoice["client"]
    client = Client(
        name=raw_client_data["name"],
        last_name=raw_client_data.get("last_name"),
        email=raw_client_data.get("email"),
        document=raw_client_data["document"],
        check_digit=raw_client_data.get("checkDigit"),
        document_type=int(raw_client_data["idDocumentType"]),  # type: ignore
        phone=raw_client_data.get("phone"),
        address=raw_client_data.get("address"),
        responsibilities=raw_client_data["responsibilities"],
    )

    created_on = first_invoice["createdOn"]
    anulated_date = first_invoice.get("canceled", {}).get("date")

    raw_payments = first_invoice["paid"]["paymentMethodValue"]
    payments: List[Payment] = []
    for raw_payment in raw_payments:
        payments.append(
            Payment(
                payment_name=raw_payment["paymentMethod"],
                payment_value=raw_payment["value"],
            )
        )

    raw_products = first_invoice["products"]
    products: List[InvoiceProduct] = []
    for raw_product in raw_products:
        product_taxes: List[TaxInfo] = []
        for raw_tax in raw_product.get("taxes", []):
            product_taxes.append(TaxInfo(
                tax_name=raw_tax["taxName"],
                value=raw_tax["taxValue"]
            ))

        product = Product(
            product_id=raw_product["code"],
            name=raw_product["name"],
            price=float(raw_product["totalBruto"]),
            taxes=product_taxes
        )
        products.append(InvoiceProduct(
            product=product,
            price=product.price,
            quantity=raw_product["quantity"],
            tax=product_taxes
        ))

    total = first_invoice["total"]
    status = first_invoice["status"]

    invoice = Invoice(
        business=business,
        cachier=cachier,
        sell_point=sell_point,
        seller=seller,
        client=client,
        created_on=created_on,
        anulated_date=anulated_date,
        invoice_prefix=prefix,
        invoice_number=number,
        payment_method=payments,
        products=products,
        total=total,
        status=status,
    )
    return invoice
