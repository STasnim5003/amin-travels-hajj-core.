from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class AdminBaseSchema(BaseModel):
    user_name: str
    password: str
    role: str
    agency_name: str
    license_number : str
    mobile_no : str
    location: Optional[str] = None
    email: Optional[str] = None
    passport_copy: Optional[List[Dict[str, Any]]] = None
    logo: Optional[List[Dict[str, Any]]] = None
    is_active: bool
    google_map_location : Optional[str] = None
    saudi_representatives : Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminResponseSchema(AdminBaseSchema):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    password: Optional[str] = Field(default=None, exclude=True)

class AdminListResponseSchema(BaseModel):
    data: List[AdminResponseSchema]
    page: int
    size: int
    total: int

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class AdminProfileUpdateSchema(BaseModel):
    user_name: str
    password: Optional[str] = None
    license_number: Optional[str] = None
    mobile_no: Optional[str] = None
    location: Optional[str]
    email: Optional[str]
    passport_copy: Optional[List[Dict[str, Any]]] = None
    logo: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class AdminProfileUpdateResponseSchema(BaseModel):
    message : str
    status: int