from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class AdminBaseSchema(BaseModel):
    user_name: str
    role: str
    agency_name: str
    license_number : str
    mobile_no : str
    location: Optional[str]
    email: Optional[str]
    passport_copy: Optional[List[Dict[str, Any]]] = None
    logo: Optional[List[Dict[str, Any]]] = None
    is_active: bool

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminResponseSchema(AdminBaseSchema):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

class AdminListResponseSchema(BaseModel):
    data: List[AdminResponseSchema]
    page: int
    size: int
    total: int

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str