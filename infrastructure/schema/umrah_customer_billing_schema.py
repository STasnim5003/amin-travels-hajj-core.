from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel

class UmrahCustomerBillingBaseSchema(BaseModel):
    invoice_no: str
    umrah_requisition_code: str
    description: Optional[str] = None
    way_of_payment: Optional[str] = None
    amount: float
    date: Optional[str] = None
    remarks: Optional[str] = None
    receipt: Optional[Any] = None

class UmrahCustomerBillingResponseSchema(UmrahCustomerBillingBaseSchema):
    id : int
    agency_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class UmrahCustomerBillingItem(BaseModel):
    amount: Optional[float]
    description: Optional[str]
    way_of_payment: Optional[str]
    date: Optional[str]
    remarks: Optional[str]
    id: Optional[int]


class UmrahCustomerBillingListResponse(BaseModel):
    umrah_requisition_code: str
    invoice_no: Optional[str]
    name: Optional[str]
    total_price: Optional[float]
    total_payment: Optional[float]
    total_due: Optional[float]
    billing_list: List[UmrahCustomerBillingItem]

class UmrahCustomerBillingUpdateSchema(UmrahCustomerBillingBaseSchema):
    id: int

class UmrahCustomerBillingInvoiceBuildSchema(BaseModel):
    umrah_requisition_code: str
    invoice_no: str
    name: Optional[str]
    mobile_no: Optional[str]
    total_price: Optional[float]
    total_due: Optional[float]
    total_payment: Optional[float]
    no_of_adults: Optional[int]
    no_of_children: Optional[int]
    no_of_infants: Optional[int]
    per_head_price_adult: Optional[float]
    per_head_price_children: Optional[float]
    per_head_price_infants: Optional[float]
    total_price_in_words: Optional[str]
    total_due_in_words: Optional[str]
    total_payment_in_words: Optional[str]

