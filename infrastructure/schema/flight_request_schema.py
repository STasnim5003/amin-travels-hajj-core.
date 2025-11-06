from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel


class FlightRequestBaseSchema(BaseModel):
    flight_name: str
    total_seat: int
    arrival_route: str
    arrival_date_option_1: Optional[Any] = None
    arrival_date_option_2: Optional[Any] = None
    departure_route: str
    departure_date_option_1: Optional[Any] = None
    departure_date_option_2: Optional[Any] = None


class FlightRequestCreateSchema(FlightRequestBaseSchema):
    pass


class FlightRequestUpdateSchema(BaseModel):
    id: int
    total_seat: Optional[int] = None
    flight_name: Optional[str] = None
    arrival_route: Optional[str] = None
    arrival_date_option_1: Optional[Any] = None
    arrival_date_option_2: Optional[Any] = None
    departure_route: Optional[str] = None
    departure_date_option_1: Optional[Any] = None
    departure_date_option_2: Optional[Any] = None
    is_active: Optional[bool] = None


class FlightRequestResponseSchema(FlightRequestBaseSchema):
    id: int
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