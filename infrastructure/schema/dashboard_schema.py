from typing import Optional

from pydantic import BaseModel

class DashboardResponseSchema(BaseModel):
    number_of_hajji : Optional[int] = None
    flight_requested : Optional[int] = None
    bdt : Optional[float] = None
    sar : Optional[float] = None
    hotel_requested: Optional[int] = None
    route_requested: Optional[int] = None
    agency_name: Optional[str] = None
