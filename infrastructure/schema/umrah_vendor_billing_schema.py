from datetime import datetime

from pydantic import BaseModel
from typing import Optional, Any

class UmrahVendorBillingCreateSchema(BaseModel):
    amin_office_code: str
    guest_name: str
    vendor_name: str
    description: Optional[Any]
    bill: float
    credit: float
    payment_date: str
    remarks: Optional[str]


class UmrahVendorBillingResponseSchema(UmrahVendorBillingCreateSchema):
    id: int
    agency_name: Optional[str]
    invoice_no: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True

class UmrahVendorBillingDetailsResponseSchema(BaseModel):
    amin_office_code: str
    name: Optional[str]
    number_of_traveller: Optional[int]

    hotels: Optional[Any]
    transports: Optional[Any]

    visa: Optional[Any]
    air_ticket: Optional[Any]
    train: Optional[Any]
    guide: Optional[Any]
    ziara: Optional[Any]
    food: Optional[Any]
    others: Optional[Any]

    child_vendors: Optional[Any]
    infant_vendors: Optional[Any]

    payments: Optional[Any]

class UmrahVendorBillingSummaryQueryParams(BaseModel):
    vendor_name: str

class UmrahAllVendorBillingSchema(BaseModel):
    vendor_name: Optional[str]
    service: Optional[str]
    total_vendor_price: Optional[float]
    total_vendor_payment: Optional[float]
    requisitions: Optional[Any]
    payments: Optional[Any]