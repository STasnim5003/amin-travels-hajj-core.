from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel


class HotelRequestBase(BaseModel):
    city: str
    type: Optional[str] = None
    name: Optional[str] = None
    tasria_number: Optional[int] = None
    check_in: Dict[str, Any]
    check_out: Dict[str, Any]
    number_of_haji: int
    room_allocation: Dict[str, Any]
    hotel_contact_person: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    nusuk_request_id: Optional[str] = None

class HotelRequestResponseSchema(HotelRequestBase):
    id: int
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    agency_name : Optional[str] = None
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
    room_allocation: Optional[Dict[str, Any]] = None
    hotel_contact_person: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    nusuk_request_id: Optional[str] = None
    is_active: Optional[bool] = None