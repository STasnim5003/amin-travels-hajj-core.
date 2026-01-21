from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class PaymentRequestB2BBase(BaseModel):
    payment_way: Optional[str] = None
    money_receipt_payment_slip_file: Optional[Any] = None
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    money_receipt_number: Optional[str] = None
    status: Optional[str] = None
    purpose: Optional[str] = None
    details : Optional[str] = None
    payment_date : Optional[str] = None
    amount : Optional[float] = None
    exchange_rate : Optional[float] = None
    sector : Optional[str] = None
    remarks : Optional[str] = None
    nusuk_request_id : Optional[str] = None
    exchanged_amount : Optional[float] = None

class PaymentRequestCreateSchema(BaseModel):
    payment_way: str
    money_receipt_payment_slip_file: Optional[Any] = None
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    money_receipt_number: Optional[str] = None
    payment_date: str
    purpose: str
    amount : float

class PaymentRequestResponse(PaymentRequestB2BBase):
    id: int
    agency_name : Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class PaymentRequestListResponseSchema(BaseModel):
    payment_requests : list[PaymentRequestResponse]

class PaymentRequestUpdateSchema(BaseModel):
    id:int
    payment_way: Optional[str] = None
    money_receipt_payment_slip_file: Optional[Any] = None
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    money_receipt_number: Optional[str] = None
    status: Optional[str] = None
    payment_date: Optional[str] = None
    purpose: Optional[str] = None
    amount : Optional[float] = None
    exchange_rate: Optional[float] = None
    exchanged_amount : Optional[float] = None