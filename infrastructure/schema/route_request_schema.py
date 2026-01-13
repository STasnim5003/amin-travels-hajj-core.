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
    cancellation_status : Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class RouteRequestResponseSchema(RouteRequestBaseSchema):
    id:int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class RouteRequestListResponseSchema(BaseModel):
    route_requests : Optional[List[RouteRequestResponseSchema]] = None
