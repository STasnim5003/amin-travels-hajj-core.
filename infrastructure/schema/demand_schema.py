
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
