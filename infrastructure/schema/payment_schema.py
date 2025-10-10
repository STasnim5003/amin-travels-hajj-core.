from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class PaymentSchema(BaseModel):
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: str
    pilgrims_id: Optional[List[str]] = None
    group_leader: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentResponseSchema(PaymentSchema):
    id: int
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    transaction_id: Optional[str] = None
    no_of_hajji: Optional[int] = None
    payable_id: Optional[int] = None
    payments: Optional[List["PaymentResponseSchema"]] = []  # nested payments
    total_payable: Optional[int] = 0
    total_paid: Optional[int] = 0
    total_due: Optional[int] = 0
    receipt: Optional[List[Dict[str, Any]]] = None



class AgencyPaymentSchemaForGroupLeader(BaseModel):
    group_leader: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: Optional[str]
    payable_id : int
    pilgrims_id: Optional[List[str]] = None


class PaginatedPaymentResponseForGroupLeader(BaseModel):
    payments: List[PaymentResponseSchema]
    page: int
    size: int
    total: int
    total_payable: Optional[int] = None
    total_payment: Optional[int] = None
    total_due: Optional[int] = None
    total_available_amount: Optional[int] = None

    class Config:
        from_attributes = True


class PaginatedPaymentResponseForAgency(BaseModel):
    payments: List[PaymentResponseSchema]
    page: int
    size: int
    total: int

    class Config:
        from_attributes = True
