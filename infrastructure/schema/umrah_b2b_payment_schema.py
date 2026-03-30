from datetime import datetime, date

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class UmrahB2BPaymentCreate(BaseModel):
    b2b_agent_name: str
    guest_name: str
    description: Optional[Dict[str, Any]] = None
    way_of_payment: Optional[str] = None
    bill: int
    credit: int
    payment_date: Optional[date] = None
    remarks: Optional[str] = None


class UmrahB2BPaymentUpdate(BaseModel):
    id: int
    b2b_agent_name: Optional[str] = None
    guest_name: Optional[str] = None
    description: Optional[Dict[str, Any]] = None
    way_of_payment: Optional[str] = None
    bill: Optional[int] = None
    credit: Optional[int] = None
    payment_date: Optional[date] = None
    remarks: Optional[str] = None
    is_active: Optional[bool] = None


class UmrahB2BPaymentResponse(UmrahB2BPaymentCreate):
    id: int
    agency_name: Optional[str]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class UmrahB2BPaymentListResponse(BaseModel):
    payment_list: List[UmrahB2BPaymentResponse]