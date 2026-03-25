from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

class UmrahCustomerBillingBaseSchema(BaseModel):
    invoice_no: str
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