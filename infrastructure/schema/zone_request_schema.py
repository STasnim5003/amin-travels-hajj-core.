from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class ZoneRequestBaseSchema(BaseModel):
    total_pilgrims: Optional[int] = 0
    details : Optional[Any] = None
    remarks: Optional[str] = None


class ZoneRequestCreateSchema(ZoneRequestBaseSchema):
    pass

class ZoneRequestUpdateSchema(BaseModel):
    id: int
    details: Optional[Any] = None
    remarks: Optional[str] = None
    total_pilgrims: Optional[int] = None
    is_active: Optional[bool] = None

class ZoneRequestResponseSchema(ZoneRequestBaseSchema):
    id: int
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True

class ZoneRequestListResponseSchema(BaseModel):
    zone_requests: List[ZoneRequestResponseSchema]
