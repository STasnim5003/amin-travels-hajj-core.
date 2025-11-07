from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ZoneRequestBaseSchema(BaseModel):
    zone_wise_tent_in_mina: Optional[str] = None
    zone_wise_pilgrims: Optional[int] = 0
    service_company_in_mina_arafat: Optional[str] = None
    package_in_mina_arafat: Optional[str] = None
    remarks: Optional[str] = None
    total_pilgrims: Optional[int] = 0

class ZoneRequestCreateSchema(ZoneRequestBaseSchema):
    pass

class ZoneRequestUpdateSchema(BaseModel):
    id: int
    zone_wise_tent_in_mina: Optional[str] = None
    zone_wise_pilgrims: Optional[int] = None
    service_company_in_mina_arafat: Optional[str] = None
    package_in_mina_arafat: Optional[str] = None
    remarks: Optional[str] = None
    total_pilgrims: Optional[int] = None
    is_active: Optional[bool] = None

class ZoneRequestResponseSchema(ZoneRequestBaseSchema):
    id: int
    agency_name: Optional[str] = None
    total_pilgrims: Optional[int] = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True

class ZoneRequestListResponseSchema(BaseModel):
    zone_requests: List[ZoneRequestResponseSchema]
