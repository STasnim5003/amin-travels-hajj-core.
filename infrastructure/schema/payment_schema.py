from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from infrastructure.schema.bank_info_schema import BankInfoBaseSchema, BankInfoResponseSchema


class PaymentSchema(BaseModel):
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: Optional[str]
    pilgrims_tracking_id: Optional[List[str]] = None
    group_leader: Optional[str] = None
    tracking_id : Optional[str] = None

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
    pilgrims_tracking_id: Optional[List[str]] = None
    way_of_payment : Optional[str] = None
    transfer_no : Optional[str] = None




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


class BankSummarySchema(BaseModel):
    bank_info_id: Optional[int] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_account: Optional[str] = None
    total_payment: Optional[float] = None

    class Config:
        from_attributes = True


class OverallSummarySchema(BaseModel):
    total_payment: Optional[float] = None
    last_7_days_payment: Optional[float] = None
    today_payment: Optional[float] = None
    yesterday_payment: Optional[float] = None

    class Config:
        from_attributes = True


class PaginatedPaymentResponseForAgency(BaseModel):
    grouped_payments: Optional[Dict[str, List[PaymentResponseSchema]]] = None
    payments: Optional[List[PaymentResponseSchema]] = None
    page: int
    size: int
    total: int
    bank_summary: Optional[List[BankSummarySchema]] = None
    overall_summary: Optional[OverallSummarySchema] = None

    class Config:
        from_attributes = True

class PaymentUpdateSchema(BaseModel):
    description: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[int] = None
    pilgrims_id: Optional[List[str]] = None

    class Config:
        from_attributes = True

class PayableInfoUpdateSchema(BaseModel):
    tracking_id: Optional[str] = None
    group_leader_code : Optional[str] = None
    total_due: Optional[int] = None
    total_payable: Optional[int] = None
    total_available_amount: Optional[int] = None
    total_payment: Optional[int] = None
    actual_payable: Optional[int] = None
    package_price_discount: Optional[int] = None

class PaymentPayableBaseSchema(BaseModel):
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: str
    payment_category: Optional[str] = None

class GroupLeaderPayableBaseSchema(PaymentPayableBaseSchema):
    group_leader: str
    pilgrims_tracking_id: Optional[List[str]] = None


class PilgrimPayableBaseSchema(PaymentPayableBaseSchema):
    tracking_id : str

class PilgrimPaymentBaseSchema(PaymentPayableBaseSchema):
    tracking_id: str
    bank_info_id : Optional[int] = None
    way_of_payment: Optional[str] = None
    transfer_no : Optional[str] = None

class GroupLeaderPaymentBaseSchema(PaymentPayableBaseSchema):
    group_leader: str
    pilgrims_tracking_id: Optional[List[str]] = None
    bank_info_id: Optional[int] = None
    way_of_payment: Optional[str] = None
    transfer_no: Optional[str] = None

class ReceiptPrintSchema(BaseModel):
    id : int
    description : Optional[str] = None
    date :Optional[str] = None
    amount : int
    group_leader: Optional[str] = None
    payer_name: Optional[str] = None
    payee_name: Optional[str] = None
    category : Optional[str] = None
    transaction_id : Optional[str] = None
    tracking_id : Optional[str] = None
    payment_category : Optional[str] = None
    way_of_payment : Optional[str] = None
    bank_info_id : Optional[int] = None
    transfer_no : Optional[str] = None
    bank_name : Optional[str] = None
    bank_branch: Optional[str] = None
    amount_in_words: Optional[str] = None

