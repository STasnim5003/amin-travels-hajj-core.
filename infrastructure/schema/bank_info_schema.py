from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BankInfoBaseSchema(BaseModel):
    name : str
    account_no : Optional[str] = None
    branch : Optional[str] = None

class BankInfoResponseSchema(BankInfoBaseSchema):
    id : int
    agency_name : Optional[str] = None
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None

class BankInfoUpdateSchema(BaseModel):
    id : int
    name: Optional[str] = None
    account_no: Optional[str] = None
    branch : Optional[str] = None
    is_active: Optional[bool] = True