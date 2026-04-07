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
    route_description : Optional[str]
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
    is_child_included_with_bed_transport: Optional[bool] = None
    is_visa: bool
    requisition_type: str
    b2b_agent_name: Optional[str] = None
    sales_person : Optional[str] = None
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
    guide: Optional[bool] = None
    train: Optional[bool] = None


class UmrahRequisitionUpdateSchema(BaseModel):
    id :int
    name: Optional[str] = None
    requisition_type: Optional[str] = None
    is_child_included_with_bed_transport: Optional[bool] = None
    b2b_agent_name: Optional[str] = None
    sales_person: Optional[str] = None
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
    train: Optional[bool] = None
    guide: Optional[bool] = None
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
    amin_office_code: Optional[str] = None
    name: Optional[str] = None
    requisition_type: Optional[str] = None
    b2b_agent_name: Optional[str] = None
    sales_person: Optional[str] = None
    number_of_traveller: Optional[int] = None
    is_child_included_with_bed_transport: Optional[bool] = None
    adult_traveller: Optional[int] = None
    other_traveller: Optional[Any] = None
    total_price: Optional[float] = None
    total_payment: Optional[float] = None
    total_due: Optional[float] = None
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
    train: Optional[bool] = None
    guide: Optional[bool] = None
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
    discount: Optional[float] = None

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
    exchange_rate : float
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

class UmrahRequisitionWithVendorsPrice(BaseModel):
    requisition : Optional[UmrahRequisitionResponseSchema] = None
    vendors_price : Optional[UmrahVendorsPriceResponseSchema] = None


class ConfirmedPilgrimsBasicInfo(BaseModel):
    name: str
    mobile_no: Optional[str]
    gender: Optional[str]
    dob: Optional[str]
    passport_no: Optional[str]
    issue: Optional[str]
    expiry: Optional[str]
    visa_no: Optional[str]
    visa_vendor: Optional[str]
    visa_status: Optional[str]
    voucher_no: Optional[str]
    group_code: Optional[str]
    group_name: Optional[str]


class ConfirmedPilgrimsFlightInfo(BaseModel):
    arrival_flight_date: Optional[str]
    arrival_carrier: Optional[str]
    arrival_flight_time: Optional[str]
    arrival_route: Optional[str]
    departure_flight_date: Optional[str]
    departure_carrier: Optional[str]
    departure_flight_time: Optional[str]
    departure_route: Optional[str]


class ConfirmedPilgrimsHotelInfo(BaseModel):
    makkah_hotel: Optional[str]
    makkah_check_in: Optional[str]
    makkah_check_out: Optional[str]
    makkah_hotel_vendor: Optional[str]
    madinah_hotel: Optional[str]
    madinah_check_in: Optional[str]
    madinah_check_out: Optional[str]
    madinah_hotel_vendor: Optional[str]


class ConfirmedPilgrimsTransportInfo(BaseModel):
    arrival_transport_route: Optional[str]
    arrival_transport_type: Optional[str]
    arrival_transport_vendor: Optional[str]
    inter_city_transport_route: Optional[str]
    inter_city_transport_type: Optional[str]
    inter_city_transport_date: Optional[str]
    inter_city_transport_vendor: Optional[str]
    departure_transport_route: Optional[str]
    departure_transport_type: Optional[str]
    departure_transport_vendor: Optional[str]
    makkah_jiyarah_date: Optional[str]
    makkah_jiyarah_vendor: Optional[str]
    madianh_jiyarah_date: Optional[str]
    madianh_jiyarah_vendor: Optional[str]
    others_jiyarah: Optional[str]


class ConfirmedPilgrimsKSAPartDataSubmission(BaseModel):
    qasswa_data_status: Optional[str]
    makkah_rep_data_status: Optional[str]
    madinah_rep_data_status: Optional[str]
    transport_rep_data_status: Optional[str]


class UmrahRequisitionConfirmedPilgrimsInfoSchema(BaseModel):
    id : int
    amin_office_code: str
    reference: Optional[str] = None
    confirmed_pilgrims_basic_info: List[ConfirmedPilgrimsBasicInfo]
    confirmed_pilgrims_flight_info: ConfirmedPilgrimsFlightInfo
    confirmed_pilgrims_hotel_info: ConfirmedPilgrimsHotelInfo
    confirmed_pilgrims_transport_info: ConfirmedPilgrimsTransportInfo
    confirmed_pilgrims_ksa_part_data_submission: ConfirmedPilgrimsKSAPartDataSubmission
    confirmed_remarks: Optional[str] = None
    confirmed_pilgrims_family_group: Optional[str] = None

class UmrahConfirmedPilgrimsResponseSchema(BaseModel):
    confirmed_pilgrims: List[UmrahRequisitionConfirmedPilgrimsInfoSchema]
    
