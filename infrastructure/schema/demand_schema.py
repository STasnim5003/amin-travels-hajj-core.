
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

class FlightDemandResponse(BaseModel):
    flight_date_start : Optional[Any]
    flight_date_end : Optional[Any]
    number_of_hajji : int = 0
    # package_name: str
    # package_duration: str

class FlightDemandListResponse(BaseModel):
    flight_demands: List[FlightDemandResponse]

class RouteDemandResponse(BaseModel):
    route_name : str
    package_duration : int
    number_of_hajji : int = 0

class RouteDemandListResponse(BaseModel):
    route_demands: List[RouteDemandResponse]

class FoodDemandResponse(BaseModel):
    food_name : str
    items : Any
    number_of_hajji : int = 0

class FoodDemandListResponse(BaseModel):
    food_demands: List[FoodDemandResponse]

class HotelDemandResponse(BaseModel):
    # checkin/checkout/category are pulled from packages.<city> JSONB via ->>, so a
    # package row missing that key (legacy/incomplete data) yields None rather than
    # a validation error — keep these Optional.
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    package_name: str
    package_duration: int
    category: Optional[str] = None
    room_and_number_of_hajji: Dict[str, int] = {}

# Keyed by city (makkah/madinah/azizia), matching demand_service.get_hotel_demand's
# actual return shape — a flat HotelDemandListResponse would not match this.
HotelDemandByCityResponse = Dict[str, List[HotelDemandResponse]]
