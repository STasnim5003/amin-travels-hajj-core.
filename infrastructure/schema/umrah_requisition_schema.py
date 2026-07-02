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
    city: Optional[str] = None


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
    nights: Optional[int] = None

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
    b2b_type : Optional[str] = None
    b2b_partial_guests : Optional[Any] = None
    b2b_partial_description : Optional[Any] = None


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
    hotel_info: Optional[Any] = None
    transport: Optional[List[UmrahRequisitionTransportSchema]] = None
    visa_price: Optional[UmrahRequisitionVendorPrice] = None
    air_ticket_price: Optional[UmrahRequisitionVendorPrice] = None
    train_price: Optional[UmrahRequisitionVendorPrice] = None
    ziara_price: Optional[UmrahRequisitionVendorPrice] = None
    guide_price: Optional[Any] = None
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
    b2b_type: Optional[str] = None
    b2b_partial_guests: Optional[Any] = None
    b2b_partial_description: Optional[Any] = None

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
    guide_vendors_price : Optional[Any] = None
    child_service: Optional[Any] = None
    infant_service: Optional[Any] = None
    discount: Optional[float] = None

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
    mobile_no: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    passport_no: Optional[str] = None
    issue: Optional[str] = None
    expiry: Optional[str] = None
    visa_no: Optional[str] = None
    visa_vendor: Optional[str] = None
    visa_status: Optional[str] = None
    voucher_no: Optional[str] = None
    group_code: Optional[str] = None
    group_name: Optional[str] = None


class ConfirmedPilgrimsFlightInfo(BaseModel):
    arrival_flight_date: Optional[str] = None
    arrival_carrier: Optional[str] = None
    arrival_flight_time: Optional[str] = None
    arrival_route: Optional[str] = None
    departure_flight_date: Optional[str] = None
    departure_carrier: Optional[str] = None
    departure_flight_time: Optional[str] = None
    departure_route: Optional[str] = None


class ConfirmedPilgrimsHotelInfo(BaseModel):
    makkah_hotel: Optional[str] = None
    makkah_check_in: Optional[str] = None
    makkah_check_out: Optional[str] = None
    makkah_hotel_vendor: Optional[str] = None
    madina_hotel: Optional[str] = None
    madina_check_in: Optional[str] = None
    madina_check_out: Optional[str] = None
    madina_hotel_vendor: Optional[str] = None


class ConfirmedPilgrimsTransportInfo(BaseModel):
    arrival_transport_route: Optional[str] = None
    arrival_transport_type: Optional[str] = None
    arrival_transport_vendor: Optional[str] = None
    inter_city_transport_route: Optional[str] = None
    inter_city_transport_type: Optional[str] = None
    inter_city_transport_date: Optional[str] = None
    inter_city_transport_vendor: Optional[str] = None
    departure_transport_route: Optional[str] = None
    departure_transport_type: Optional[str] = None
    departure_transport_vendor: Optional[str] = None
    makkah_ziara_date: Optional[str] = None
    makkah_ziara_vendor: Optional[str] = None
    madianh_ziara_date: Optional[str] = None
    madianh_ziara_vendor: Optional[str] = None
    others_ziara: Optional[str] = None


class ConfirmedPilgrimsKSAPartDataSubmission(BaseModel):
    qasswa_data_status: Optional[str] = None
    makkah_rep_data_status: Optional[str] = None
    madinah_rep_data_status: Optional[str] = None
    transport_rep_data_status: Optional[str] = None

class ServiceConfirmationStatus(BaseModel):
    hotel: Optional[bool] = None
    visa: Optional[bool] = None
    air_ticket: Optional[bool] = None
    transport: Optional[bool] = None
    ziara: Optional[bool] = None
    guide: Optional[bool] = None
    food: Optional[bool] = None
    train: Optional[bool] = None


class EmergencyContractPerson(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None
    mobile_no: Optional[str] = None


class UmrahRequisitionConfirmedPilgrimsInfoSchema(BaseModel):
    id: int
    amin_office_code: str
    number_of_traveller: Optional[int] = None
    reference: Optional[str] = None
    confirmed_pilgrims_basic_info: Optional[List[ConfirmedPilgrimsBasicInfo]] = None
    confirmed_pilgrims_flight_info: Optional[ConfirmedPilgrimsFlightInfo] = None
    confirmed_pilgrims_hotel_info: Optional[ConfirmedPilgrimsHotelInfo] = None
    confirmed_pilgrims_transport_info: Optional[ConfirmedPilgrimsTransportInfo] = None
    confirmed_pilgrims_ksa_part_data_submission: Optional[ConfirmedPilgrimsKSAPartDataSubmission] = None
    confirmed_remarks: Optional[str] = None
    confirmed_pilgrims_family_group: Optional[str] = None
    service_confirmation_status: Optional[ServiceConfirmationStatus] = None
    emergency_contract_person: Optional[List[EmergencyContractPerson]] = None
    b2b_type: Optional[str] = None
    b2b_partial_guests : Optional[Any] = None
    b2b_partial_description : Optional[Any] = None



class UmrahConfirmedPilgrimItemSchema(UmrahRequisitionConfirmedPilgrimsInfoSchema):
    total_price: Optional[float]
    total_due: Optional[float]
    total_payment: Optional[float]
    discount: Optional[float]
    is_visa: Optional[bool] = None
    is_air_ticket: Optional[bool] = None
    is_hotel: Optional[bool] = None
    is_transport: Optional[bool] = None
    is_ziara: Optional[bool] = None
    is_guide: Optional[bool] = None
    is_food: Optional[bool] = None
    is_train: Optional[bool] = None


class UmrahConfirmedPilgrimsResponseSchema(BaseModel):
    confirmed_pilgrims: List[UmrahConfirmedPilgrimItemSchema]
