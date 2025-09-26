from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class ViewFieldSchema(BaseModel):
    view_name: Optional[str] = None
    field_name: Optional[List[str]] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class ViewFieldResponseSchema(ViewFieldSchema):
    id: int
    username : str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

class ViewFieldListResponseSchema(BaseModel):
    data : List[ViewFieldResponseSchema]
