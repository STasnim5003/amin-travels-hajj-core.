from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class ViewFieldSchema(BaseModel):
    view_name: str
    field_name: List[str]
    table_name : str

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

    class Config:
        from_attributes = True
        populate_by_name = True

class ViewFieldListResponseSchema(BaseModel):
    data : List[ViewFieldResponseSchema]
