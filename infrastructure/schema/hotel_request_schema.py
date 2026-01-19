from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel

class HotelPricingSchema(BaseModel):
    with_vat : float
    without_vat : float
    with_loading_unloading_fee: Optional[bool] = None

class HotelRequestRoomAllocationSchema(BaseModel):
    room_type : str
    no_of_room : int
    per_room_price_without_vat : float
    per_room_price_with_vat : float
    total_price_without_vat : float
    total_price_with_vat : float

class HotelRequestGrandTotal(BaseModel):
    no_of_room : int
    total_price_without_vat : float
    total_price_with_vat : float

class HotelRequestBase(BaseModel):
    city: str
    type: Optional[str] = None
    name: Optional[str] = None
    tasria_number: Optional[int] = None
    check_in: Dict[str, Any]
    check_out: Dict[str, Any]
    number_of_haji: int
    room_allocation: Optional[List[HotelRequestRoomAllocationSchema]] = None
    hotel_contact_person: Optional[Dict[str, Any]] = None
    pricing: Optional[HotelPricingSchema] = None
    document: Optional[List[Dict[str, Any]]] = None
    price_per_hajji: Optional[HotelPricingSchema] = None
    grand_total: Optional[HotelRequestGrandTotal] = None
    cancel_request_status : Optional[str] = None
    tasria_copy: Optional[List[Dict[str, Any]]] = None
    tent: Optional[str] = None
    rfq_no : Optional[int] = None

class HotelRequestResponseSchema(HotelRequestBase):
    id: int
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    agency_name : Optional[str] = None
    status : Optional[str] = None
    nusuk_request_id: Optional[str] = None
    nusuk_request_file_category: Optional[str] = None
    remarks : Optional[str] = None
    rfq_no : Optional[int] = None
    class Config:
        from_attributes = True

class HotelRequestListResponseSchema(BaseModel):
    hotel_requests: List[HotelRequestResponseSchema]

class HotelRequestUpdateSchema(BaseModel):
    id: int
    city: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    tasria_number: Optional[int] = None
    check_in: Optional[Dict[str, Any]] = None
    check_out: Optional[Dict[str, Any]] = None
    number_of_haji: Optional[int] = None
    room_allocation: Optional[List[HotelRequestRoomAllocationSchema]] = None
    hotel_contact_person: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    nusuk_request_id: Optional[str] = None
    is_active: Optional[bool] = None
    document: Optional[Any] = None
    tasria_copy: Optional[Any] = None
    pricing: Optional[HotelPricingSchema] = None
    price_per_hajji: Optional[HotelPricingSchema] = None
    grand_total: Optional[HotelRequestGrandTotal] = None
    nusuk_request_file_category : Optional[str] = None
    remarks: Optional[str] = None
    tent : Optional[str] = None
    rfq_no : Optional[int] = None
