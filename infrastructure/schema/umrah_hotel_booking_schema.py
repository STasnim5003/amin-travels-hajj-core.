from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UmrahHotelBookingCreate(BaseModel):
    res_no: str
    guest_name: str
    hotel_name: str
    room_type: Optional[str]
    mp: Optional[str]
    qty: Optional[str]
    check_in: Optional[str]
    check_out: Optional[str]
    remarks: Optional[str]

class UmrahHotelBookingUpdate(BaseModel):
    id: int
    res_no: Optional[str] = None
    guest_name: Optional[str] = None
    hotel_name: Optional[str] = None
    room_type: Optional[str] = None
    mp: Optional[str] = None
    qty: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    remarks: Optional[str] = None

class UmrahHotelBookingResponse(UmrahHotelBookingCreate):
    id: int
    agency_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True