from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class RouteBaseSchema(BaseModel):
    route_name: str
    description: str
    is_active: Optional[bool] = True
    is_publish: Optional[bool] = False



class RouteCreateSchema(BaseModel):
    route_name: str
    description: str
    agency_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_publish: Optional[bool] = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class RouteResponseSchema(RouteBaseSchema):
    id: int
    agency_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class RouteUpdateSchema(BaseModel):
    id :int
    description: Optional[str] = None
    is_publish: Optional[bool] = True
    is_active: Optional[bool] = True
    route_name: Optional[str] = None