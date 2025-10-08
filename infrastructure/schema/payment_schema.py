from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class PaymentSchema(BaseModel):
    description: Optional[str] = None
    date: Optional[str] = None
    amount: int
    category: str
    tracking_ids : Optional[List[str]] = None
    group_leader : Optional[str] = None

    class Config:
        from_attributes = True


class PaymentResponseSchema(PaymentSchema):
    id: int
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    due: Optional[int] = None
    transaction_id: Optional[str] = None
    status : Optional[str] = None
