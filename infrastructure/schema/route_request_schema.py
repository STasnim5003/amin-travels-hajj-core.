from typing import Optional, List, Any
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

class RouteRequestCreateSchema(BaseModel):
    route_requests : List[RouteRequestBaseSchema]
    total_price : float
    status : Optional[str] = None

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

class RouteRequestResponseSchema(BaseModel):
    id:int
    arrival: Optional[Any] = None
    departure: Optional[Any] = None
    between_cities_up: Optional[Any] = None
    between_cities_down: Optional[Any] = None
    mashaer: Optional[Any] = None
    agency_name: Optional[str] = None
    status: Optional[str] = None
    total_price: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    cancellation_status : Optional[str] = None


    class Config:
        from_attributes = True

class RouteRequestListResponseSchema(BaseModel):
    route_requests : Optional[List[RouteRequestResponseSchema]] = None
