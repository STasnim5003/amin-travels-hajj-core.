from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ZiaraBaseSchema(BaseModel):
    name: str
    description: str
    location: str
    google_map_location: str
    area: str
    pic: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = True


class ZiaraCreateSchema(ZiaraBaseSchema):
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ZiaraUpdateSchema(ZiaraBaseSchema):
    updated_by: Optional[str] = None


class ZiaraResponseSchema(ZiaraBaseSchema):
    id: int
    agency_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
