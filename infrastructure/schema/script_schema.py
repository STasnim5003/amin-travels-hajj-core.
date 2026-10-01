from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PrpDataFetchRequestSchema(BaseModel):
    email: str
    password: str


class AgencyHajjiCountFetchResponseSchema(BaseModel):
    hl : Optional[str] = None
    agency : Optional[str] = None
    preregistered_pilgrim : Optional[int] = None
    registered_pilgrim : Optional[int] = None
    voucher_from_details : Optional[int] = None
    need_to_pay_voucher : Optional[int] = None
    registered_percentage: Optional[float] = Field(
        None, alias="percentage_registered"
    )
    total_pilgrims : Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
