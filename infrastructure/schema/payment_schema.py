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


class PaginatedPaymentResponseForAgency(BaseModel):
    payments: Optional[List[PaymentResponseSchema]] =  None
    page: int
    size: int
    total: int

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



