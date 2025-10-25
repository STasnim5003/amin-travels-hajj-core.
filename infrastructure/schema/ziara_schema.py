from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ZiaraBaseSchema(BaseModel):
    description: str
    is_active: Optional[bool] = True

class ZiaraCreateSchema(ZiaraBaseSchema):
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ZiaraUpdateSchema(BaseModel):
    id:int
    description: Optional[str] = None
    is_active: Optional[bool] = True


class ZiaraResponseSchema(BaseModel):
    id: int
    description: Optional[str] = None
    agency_name: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
