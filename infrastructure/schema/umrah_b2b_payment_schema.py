from datetime import datetime, date

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class UmrahB2BPaymentCreate(BaseModel):
    description: Optional[str] = None
    way_of_payment: Optional[str] = None
    amount: float
    payment_date: Optional[date] = None
    remarks: Optional[str] = None
    b2b_agent_name : str
    invoice_no_and_paid_amount: Optional[Any] = None

class UmrahB2BPaymentUpdate(BaseModel):
    id: int
    description: Optional[str] = None
    way_of_payment: Optional[str] = None
    amount: float
    payment_date: Optional[date] = None
    remarks: Optional[str] = None
    b2b_agent_name: str
    invoice_no_and_paid_amount: Optional[Any] = None



class UmrahB2BPaymentResponse(UmrahB2BPaymentCreate):
    id: int
    invoice_no: Optional[str]
    agency_name: Optional[str]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class B2BAgentPaymentListQueryParameters(BaseModel):
    b2b_agent_name: str
    # payment_start_date: Optional[date]
    # payment_end_date: Optional[date]

class UmrahB2BBillingInvoiceBuildSchema(BaseModel):
    amin_office_code: str
    b2b_agent_name: Optional[str]
    sales_person: Optional[str]
    name: Optional[str]
    mobile_no: Optional[str]
    total_price: Optional[float]
    total_payment: Optional[float]
    discount: Optional[float]
    total_due: Optional[float]
    no_of_adults: Optional[int]
    no_of_children: Optional[int]
    no_of_infants: Optional[int]
    per_head_price_adult: Optional[float]
    per_head_price_children: Optional[float]
    per_head_price_infants: Optional[float]
    total_price_in_words: Optional[str]
    total_due_in_words: Optional[str]
    total_payment_in_words: Optional[str]
    child_service: Optional[dict] = None
    infant_service: Optional[dict] = None
    visa_total_price: Optional[float] = None
    air_ticket_total_price: Optional[float] = None
    ziara_total_price: Optional[float] = None
    train_total_price: Optional[float] = None

    hotel_info: Optional[List[dict]] = []
    transport_info: Optional[List[dict]] = []
    guide_info: Optional[List[dict]] = []


class B2BTransactionItem(BaseModel):
    type: Optional[str] = None
    amin_office_code: Optional[str] = None
    name: Optional[str] = None
    sales_person: Optional[str] = None
    total_price: Optional[float] = None
    discount: Optional[float] = None
    invoice_no: Optional[str] = None
    payment_date: Optional[str] = None
    amount: Optional[float] = None
    payment_way: Optional[str] = None
    created_at: Optional[str] = None
    id: Optional[int] = None

class UmrahB2BTransactionList(BaseModel):
    b2b_agent_name: str
    agency_name: str
    total_bill: float
    total_credit: float
    total_due: float
    transactions: Optional[List[B2BTransactionItem]] = None