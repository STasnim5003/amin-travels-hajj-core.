from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel

class RouteForRequisitionBaseSchema(BaseModel):
    route_type : str
    route_name : str
    route_price : float
    route_mapping_id : Optional[str] = None
    agency_name: Optional[str] = None

class RouteForRequisitionCreateSchema(BaseModel):
    route_type_1 : str
    route_name_1 : str
    route_type_2: Optional[str] = None
    route_name_2: Optional[str] = None
    route_price : float

class RouteForRequisitionUpdateSchema(BaseModel):
    id: int
    route_type: Optional[str] = None
    route_name: Optional[str] = None
    route_price: Optional[float] = None

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