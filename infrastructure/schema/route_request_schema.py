from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class RouteRequestBaseSchema(BaseModel):
    route_type : str
    route_name : str
    route_price : float
    number_of_pax : int
    total_price : float
    status : Optional[str] = None
    route_mapping_id : Optional[str] = None
    cancellation_status : Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class RouteRequestUpdateSchema(BaseModel):
    id : int
    route_type: Optional[str] = None
    route_name: Optional[str] = None
    route_price: Optional[float] = None
    number_of_pax: Optional[int] = None
    total_price: Optional[float] = None
    status: Optional[str] = None
    route_mapping_id: Optional[str] = None
    cancellation_status: Optional[str] = None

class RouteRequestResponseSchema(RouteRequestBaseSchema):
    id:int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class RouteRequestListResponseSchema(BaseModel):
    route_requests : Optional[List[RouteRequestResponseSchema]] = None
