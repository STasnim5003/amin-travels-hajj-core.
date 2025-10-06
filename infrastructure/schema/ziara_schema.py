from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ZiaraBaseSchema(BaseModel):
    description: str

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
