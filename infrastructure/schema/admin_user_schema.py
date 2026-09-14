from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field


class AdminUserBase(BaseModel):
    name: str
    username:Optional[str] = None
    email: Optional[str] = None
    mobile_no: str
    role: str
    passport_no: Optional[str] = None
    passport_expiry_date : Optional[str] = None
    passport_dob: Optional[str] = None
    password : Optional[str] = None
    hotel_name : Optional[str] = None
    ekama_file : Optional[Any] = None
    others : Optional[str] = None
    nid : Optional[str] = None
    tracking_id : Optional[str] = None
    dob : Optional[str] = None
    ksa_mobile: Optional[str] = None
    gender: Optional[str] = None

    class Config:
        from_attributes=True


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

class AdminUserResetPasswordSchema(BaseModel):
    new_password: str