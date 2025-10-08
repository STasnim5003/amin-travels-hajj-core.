from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel


class AddOnsServiceBase(BaseModel):
    name: str
    price: str


class AddOnsServiceCreate(AddOnsServiceBase):
    pass


class AddOnsServiceResponse(AddOnsServiceBase):
    id: int
    agency_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True