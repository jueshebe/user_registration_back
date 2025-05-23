"""Model for invoices."""

from typing import List, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from app.v1.models.client import Client
from app.v1.models.product import Product, TaxInfo


class Employee(BaseModel):
    """Cachier model."""

    name: str
    employee_id: str


class InvoiceProduct(BaseModel):
    """Invoice product model.

    Product object contains current information of a product
    some invoice can have another state of a product.
    """

    product: Product
    price: float
    quantity: int
    tax: Optional[List[TaxInfo]]


class Payment(BaseModel):
    """Payment model."""

    payment_name: str
    payment_value: float


class InvoiceStatus(str, Enum):
    """Invoice status model."""

    PAID = "Pagada"
    CANCELED = "Anulada"


class Business(BaseModel):
    """Company data."""

    name: str
    nit: str
    address: Optional[str] = None
    phone: Optional[str] = None


class Invoice(BaseModel):
    """Invoice model."""

    business: Business
    cachier: Employee
    sell_point: str
    seller: Employee
    client: Client
    created_on: datetime
    anulated_date: Optional[datetime] = None
    invoice_prefix: str
    invoice_number: int
    payment_method: List[Payment]
    products: List[InvoiceProduct]
    total: float
    status: InvoiceStatus = InvoiceStatus.PAID
