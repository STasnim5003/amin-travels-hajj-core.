from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdminUserBase(BaseModel):
    name: str
    email: str
    mobile_no: str
    role: str
    passport_no: Optional[str] = None
    passport_expiry_date : Optional[str] = None
    passport_address : Optional[str] = None
    passport_dob: Optional[str] = None


class AdminUserCreate(AdminUserBase):
    pass

class AdminUserResponse(AdminUserBase):
    id: int
    agency_name : Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True