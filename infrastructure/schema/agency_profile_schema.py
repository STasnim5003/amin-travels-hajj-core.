from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AgencyProfileItemSchema(BaseModel):
    sl_no: Optional[int] = None
    hl: str
    agency_name: str
    email: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    pre_reg: Optional[int] = None
    reg: Optional[int] = None
    total: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgencyProfileListResponseSchema(BaseModel):
    success: bool
    count: int
    data: List[AgencyProfileItemSchema]
