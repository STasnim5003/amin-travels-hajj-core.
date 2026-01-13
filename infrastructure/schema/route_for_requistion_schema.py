from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class RouteForRequisitionBaseSchema(BaseModel):
    route_type : str
    route_name : str
    route_price : float
    agency_name: Optional[str] = None

class RouteForRequisitionUpdateSchema(BaseModel):
    id: int
    route_type: Optional[str] = None
    route_name: Optional[str] = None
    route_price: Optional[str] = None

class RouteForRequisitionResponseSchema(RouteForRequisitionBaseSchema):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class RouteForRequisitionListResponseSchema(BaseModel):
    routes : Optional[List[RouteForRequisitionResponseSchema]] = None