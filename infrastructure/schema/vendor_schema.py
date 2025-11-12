from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class VendorBase(BaseModel):
    name: str
    category: str
    area: Optional[str] = None

class VendorCreateSchema(VendorBase):
    pass


class VendorUpdateSchema(BaseModel):
    id : int
    name: Optional[str] = None
    category: Optional[str] = None
    area: Optional[str] = None
    is_active: Optional[bool] = None


class VendorResponseSchema(VendorBase):
    id: int
    agency_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class VendorListResponseSchema(BaseModel):
    vendors : List[VendorResponseSchema]