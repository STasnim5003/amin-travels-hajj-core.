from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel


class FlightRequestBaseSchema(BaseModel):
    flight_name: str
    total_seat: int
    departure_route: int
    departure_date_option_1: Optional[Any] = None
    departure_date_option_2: Optional[Any] = None
    arrival_route: int
    arrival_date_option_1: Optional[Any] = None
    arrival_date_option_2: Optional[Any] = None
    duration: Optional[str] = None


class FlightRequestCreateSchema(FlightRequestBaseSchema):
    pass


class FlightRequestUpdateSchema(BaseModel):
    id: int
    total_seat: Optional[int] = None
    flight_name: Optional[str] = None
    arrival_route: Optional[int] = None
    arrival_date_option_1: Optional[Any] = None
    arrival_date_option_2: Optional[Any] = None
    departure_route: Optional[int] = None
    departure_date_option_1: Optional[Any] = None
    departure_date_option_2: Optional[Any] = None
    is_active: Optional[bool] = None
    duration : Optional[str] = None


class FlightRequestResponseSchema(FlightRequestBaseSchema):
    id: int
    departure_route_description :Optional[str] = None
    arrival_route_description: Optional[str] = None
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True

class FlightRequestListResponseSchema(BaseModel):
    flight_requests: List[FlightRequestResponseSchema]