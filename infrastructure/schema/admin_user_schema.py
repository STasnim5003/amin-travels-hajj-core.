from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field


class AdminUserBase(BaseModel):
    name: str
    email: Optional[str] = None
    mobile_no: str
    role: str
    passport_no: Optional[str] = None
    passport_expiry_date : Optional[str] = None
    passport_address : Optional[str] = None
    passport_dob: Optional[str] = None
    password : Optional[str] = None
    hotel_name : Optional[str] = None
    ekama_file : Optional[Any] = None
    others : Optional[str] = None


class AdminUserCreate(AdminUserBase):
    pass

class AdminUserResponse(AdminUserBase):
    id: int
    code : Optional[str] = None
    agency_name : Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    password: Optional[str] = Field(exclude=True)

    class Config:
        from_attributes = True

class GroupLeaderAssignSchema(BaseModel):
    pilgrims_id : List[int]
    group_leader_code : str