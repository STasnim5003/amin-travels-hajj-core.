from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel

class UmrahRequisitionVendorPrice(BaseModel):
    vendor_name : Optional[str] = None
    vendor_price: Optional[float] = None
    service_charge: Optional[float] = None
    total_price: Optional[float] = None
    per_head_price_adult: Optional[float] = None
    per_head_price_child: Optional[float] = None
    per_head_price_infant: Optional[float] = None

class UmrahRequisitionHotelType(BaseModel):
    food: str
    hotel_name: Optional[str] = None
    type: str
class UmrahRequisitionHotelSchema(BaseModel):
    city: str
    hotels: List[UmrahRequisitionHotelType]
    distance : str
    room_type : Any
    check_in : Any
    check_out : Any

    price : Optional[UmrahRequisitionVendorPrice] = None

class UmrahRequisitionTransportSchema(BaseModel):
    route_id : int
    transport: Any
    price : Optional[UmrahRequisitionVendorPrice] = None

class UmrahRequisitionTravellerPassportInfo(BaseModel):
    passport_name : str
    passport_no : str
    passport_expiry_date : str
    passport_type : str

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
    return_date_option_1: Optional[Any] = None
    return_date_option_2: Optional[Any] = None
    return_date_final: Optional[Any] = None
    passport_info : Optional[Any] = None
    ziara: Optional[bool] = None

class UmrahRequisitionUpdateSchema(BaseModel):
    id :int
    name: Optional[str] = None
    number_of_traveller: Optional[int] = None
    adult_traveller: Optional[int] = None
    other_traveller: Optional[Any] = None
    is_visa: Optional[bool] = None
    with_hotel_brn: Optional[bool] = None
    air_ticket: bool = None
    air_ticket_category: Optional[str] = None
    airline_preference: Optional[str] = None
    flight_data: Optional[Any] = None
    hotel_info: Optional[List[UmrahRequisitionHotelSchema]] = None
    transport: Optional[List[UmrahRequisitionTransportSchema]] = None
    remarks: Optional[str] = None
    food: Optional[bool] = None
    mobile_no: Optional[str] = None
    flight_date_option_1: Optional[Any] = None
    flight_date_option_2: Optional[Any] = None
    flight_date_final: Optional[Any] = None
    return_date_option_1: Optional[Any] = None
    return_date_option_2: Optional[Any] = None
    return_date_final: Optional[Any] = None
    passport_info: Optional[Any] = None
    ziara: Optional[bool] = None


class UmrahRequisitionAssignedService(BaseModel):
    id : int
    name: Optional[str] = None
    number_of_traveller: Optional[int] = None
    adult_traveller: Optional[int] = None
    other_traveller: Optional[Any] = None
    is_visa: Optional[bool] = None
    with_hotel_brn: Optional[bool] = None
    air_ticket: Optional[bool] = None
    air_ticket_category: Optional[str] = None
    airline_preference: Optional[str] = None
    flight_data: Optional[Any] = None
    remarks: Optional[str] = None
    food: Optional[bool] = None
    mobile_no: Optional[str] = None
    flight_date_option_1: Optional[Any] = None
    flight_date_option_2: Optional[Any] = None
    flight_date_final: Optional[Any] = None
    passport_info: Optional[Any] = None
    ziara: Optional[bool] = None
    hotel_info: Optional[List[UmrahRequisitionHotelSchema]] = None
    transport: Optional[List[UmrahRequisitionTransportSchema]] = None
    visa_price: Optional[UmrahRequisitionVendorPrice] = None
    air_ticket_price: Optional[UmrahRequisitionVendorPrice] = None
    train_price: Optional[UmrahRequisitionVendorPrice] = None
    ziara_price: Optional[UmrahRequisitionVendorPrice] = None
    guide_price: Optional[UmrahRequisitionVendorPrice] = None
    food_price: Optional[UmrahRequisitionVendorPrice] = None
    others_price: Optional[UmrahRequisitionVendorPrice] = None
    total_vendor_price: Optional[float] = None
    total_service_charge: Optional[float] = None
    total_price: Optional[float] = None
    per_head_price_adult: Optional[float] = None
    per_head_price_child: Optional[float] = None
    per_head_price_infant: Optional[float] = None
    is_active : Optional[bool] = None
    return_date_option_1: Optional[Any] = None
    return_date_option_2: Optional[Any] = None
    return_date_final: Optional[Any] = None
    exchange_rate: Optional[float] = None
    child_service: Optional[Any] = None
    infant_service: Optional[Any] = None

class UmrahRequisitionConfirmationSchema(BaseModel):
    id : int
    is_confirmed: bool
    passport_info: List[UmrahRequisitionTravellerPassportInfo]

class UmrahRequisitionResponseSchema(UmrahRequisitionAssignedService):
    is_confirmed: Optional[bool] = None
    agency_name : Optional[str] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None

    class Config:
        from_attributes = True

class UmrahRequisitionListResponseSchema(BaseModel):
    umrah_requisitions: List[UmrahRequisitionResponseSchema]


class UmrahVendorsPriceCreateSchema(BaseModel):
    umrah_requisition_id : int
    hotel_vendors_price : Optional[Any] = None
    transport_vendors_price : Optional[Any] = None
    air_ticket_vendors_price : Optional[Any] = None
    visa_vendors_price : Optional[Any] = None
    train_vendors_price : Optional[Any] = None
    ziara_vendors_price : Optional[Any] = None
    food_vendors_price : Optional[Any] = None
    others_vendors_price : Optional[Any] = None

class UmrahVendorsPriceResponseSchema(UmrahVendorsPriceCreateSchema):
    id : int
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None

    class Config:
        from_attributes = True