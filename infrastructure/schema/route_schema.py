from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class RouteBaseSchema(BaseModel):
    description: str
    is_publish: Optional[bool] = False
    is_active: Optional[bool] = True


class RouteCreateSchema(RouteBaseSchema):
    agency_name: Optional[str] = None
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