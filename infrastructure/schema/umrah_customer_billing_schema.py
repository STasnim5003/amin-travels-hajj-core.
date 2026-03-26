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
