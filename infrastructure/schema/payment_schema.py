from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class PaymentSchema(BaseModel):
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: Optional[str]
    pilgrims_tracking_id: Optional[List[str]] = None
    group_leader: Optional[str] = None
    tracking_id: Optional[str] = None

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
    way_of_payment: Optional[str] = None
    transfer_no: Optional[str] = None
    cheque_no: Optional[str] = None
    cheque_bank: Optional[str] = None
    voucher_no : Optional[str] = None
    bank_info: Optional[Dict[str, Any]] = None


class AgencyPaymentSchemaForGroupLeader(BaseModel):
    group_leader: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: Optional[str]
    payable_id: int
    pilgrims_id: Optional[List[str]] = None


class PaginatedPaymentResponseForGroupLeader(BaseModel):
    grouped_payments: List[PaymentResponseSchema]
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


class GroupedPayment(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    mobile_no: Optional[str] = None
    actual_payable : Optional[int] = None
    total_payment : Optional[int] = None
    total_due: Optional[int] = None
    id: Optional[int] = None
    tracking_id: Optional[str] = None
    group_leader: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    created_at: Optional[str] = None
    bank_info: Optional[Dict[str, Any]] = None
    way_of_payment: Optional[str] = None
    transfer_no: Optional[str] = None
    pilgrims_tracking_id: Optional[List[str]] = None
    transaction_id: Optional[str] = None

    children: Optional[List[PaymentResponseSchema]] = None


class PaginatedPaymentResponseForAgency(BaseModel):
    grouped_payments: Optional[List[GroupedPayment]] = None
    # payments: Optional[List[PaymentResponseSchema]] = None
    page: int
    size: int
    total: int
    bank_summary: Optional[List[BankSummarySchema]] = None
    overall_summary: Optional[OverallSummarySchema] = None
    today_payments: Optional[List[Dict[str, Any]]] = None
    yesterday_payments: Optional[List[Dict[str, Any]]] = None
    last_7_days_payments: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class PayableInfoUpdateSchema(BaseModel):
    tracking_id: Optional[str] = None
    group_leader_code: Optional[str] = None
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
    tracking_id: str


class PilgrimPaymentBaseSchema(PaymentPayableBaseSchema):
    tracking_id: str
    bank_info_id: Optional[int] = None
    way_of_payment: Optional[str] = None
    transfer_no: Optional[str] = None
    voucher_no: Optional[str] = None,
    cheque_no: Optional[str] = None,
    cheque_bank: Optional[str] = None,


class GroupLeaderPaymentBaseSchema(PaymentPayableBaseSchema):
    group_leader: str
    pilgrims_tracking_id: Optional[List[str]] = None
    bank_info_id: Optional[int] = None
    way_of_payment: Optional[str] = None
    transfer_no: Optional[str] = None
    voucher_no: Optional[str] = None,
    cheque_no: Optional[str] = None,
    cheque_bank: Optional[str] = None,



class ReceiptPrintSchema(BaseModel):
    id: int
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    group_leader: Optional[str] = None
    payer_name: Optional[str] = None
    payee_name: Optional[str] = None
    category: Optional[str] = None
    transaction_id: Optional[str] = None
    tracking_id: Optional[str] = None
    payment_category: Optional[str] = None
    way_of_payment: Optional[str] = None
    bank_info_id: Optional[int] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_account_no: Optional[str] = None
    amount_in_words: Optional[str] = None
    voucher_no : Optional[str] = None
    cheque_no : Optional[str] = None
    cheque_bank : Optional[str] = None

class PilgrimPayableReportSchema(BaseModel):
    id: int
    name_en: Optional[str] = None
    name_bn: Optional[str] = None
    nid: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    tracking_id: Optional[str] = None
    amount_in_words: Optional[str] = None
    package_name : Optional[str] = None
    package_duration: Optional[int] = None
    package_bed_types: Optional[str] = None
    add_ons_services: Optional[Any] = None
    agency_name : str

class GroupLeaderPayableReportSchema(BaseModel):
    id: int
    name_en: Optional[str] = None
    agency_name: str
    code: Optional[str] = None
    amount: int
    amount_in_words: Optional[str] = None
    summary: Optional[Any] = None

class PayableUpdateSchema(BaseModel):
    payable_id : int
    tracking_id: Optional[str] = None
    group_leader: Optional[str] = None
    payment_category: Optional[str] = None
    amount: Optional[int] = None
    description: Optional[str] = None
    date: Optional[str] = None
    pilgrims_tracking_id: Optional[List[str]] = None
    cheque_no: Optional[str] = None
    cheque_bank: Optional[str] = None
    category: Optional[str] = None

class PaymentUpdateSchema(BaseModel):
    payment_id : int
    group_leader: Optional[str]= None
    tracking_id: Optional[str] = None
    amount: Optional[int] = None
    description: Optional[str] = None
    date: Optional[str] = None
    payment_category: Optional[str] = None
    bank_info_id: Optional[int] = None
    way_of_payment: Optional[str] = None
    transfer_no: Optional[str] = None
    voucher_no: Optional[str] = None
    cheque_no: Optional[str] = None
    cheque_bank: Optional[str] = None
    pilgrims_tracking_id: Optional[List[str]] = None,

class PaymentLedgerSchema(BaseModel):
    tracking_id: Optional[str] = None
    group_leader: Optional[str] = None
    name: Optional[str] = None
    mobile_no: Optional[str] = None
    total_payable: Optional[int] = 0
    total_available_amount: Optional[int] = 0
    total_payment: Optional[int] = 0
    total_due: Optional[int] = 0
    actual_payable : Optional[int]=0
    package_price_discount : Optional[int] = 0
    payable_list: Optional[List[PaymentResponseSchema]] = None
    payment_list: Optional[List[PaymentResponseSchema]] = None
    generated_on: Optional[datetime] = None

    class config:
        from_attributes: True
