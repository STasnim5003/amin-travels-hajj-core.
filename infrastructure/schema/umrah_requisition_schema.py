from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel


class UmrahRequisitionHotelSchema(BaseModel):
    city: str
    hotel_name : str
    type : str
    distance : str
    room_type : Any
    check_in : Any
    check_out : Any
    food: str

class UmrahRequisitionTransportSchema(BaseModel):
    route_id : int
    transport: Any


class UmrahRequisitionBase(BaseModel):
    name: str
    number_of_traveller: int
    adult_traveller: int
    other_traveller: Optional[Any] = None
    is_visa: bool
    with_hotel_brn: Optional[bool] = None
    air_ticket: bool = None
    air_ticket_category: Optional[str] = None
    airline_preference: Optional[str] = None
    flight_data: Optional[Any] = None
    hotel_info: List[UmrahRequisitionHotelSchema]
    transport: List[UmrahRequisitionTransportSchema]
    remarks: Optional[str] = None
    food : Optional[bool] = None
    mobile_no : Optional[str] = None
    flight_date_option_1 : Optional[Any] = None
    flight_date_option_2 : Optional[Any] = None
    flight_date_final : Optional[Any] = None
    passport_info : Optional[Any] = None

class UmrahRequisitionResponseSchema(UmrahRequisitionBase):
    id : int
    agency_name : Optional[str] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None
    is_active : Optional[bool] = None

    class Config:
        from_attributes = True

class UmrahRequisitionListResponseSchema(BaseModel):
    umrah_requisitions: List[UmrahRequisitionResponseSchema]
