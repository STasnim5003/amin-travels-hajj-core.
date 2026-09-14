from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel


class HotelPurchaseBase(BaseModel):
    # Matches the bucket key returned by GET /hotel-demand — copy city/category/
    # checkin/checkout straight out of that response when creating a purchase
    # against a demand window.
    city: str
    category: str
    checkin: str
    checkout: str
    hotel_name: str
    vendor_name: Optional[str] = None
    # {bed_type: room_count}, same shape as GET /hotel-demand's room_and_number_of_hajji
    rooms_purchased: Dict[str, int]
    cost: float
    currency: str = "BDT"
    purchase_date: Optional[str] = None
    booking_file: Optional[Any] = None
    remarks: Optional[str] = None


class HotelPurchaseCreateSchema(HotelPurchaseBase):
    pass


class HotelPurchaseUpdateSchema(BaseModel):
    id: int
    city: Optional[str] = None
    category: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    hotel_name: Optional[str] = None
    vendor_name: Optional[str] = None
    rooms_purchased: Optional[Dict[str, int]] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    purchase_date: Optional[str] = None
    booking_file: Optional[Any] = None
    remarks: Optional[str] = None


class HotelPurchaseResponseSchema(HotelPurchaseBase):
    id: int
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class HotelPurchaseListResponseSchema(BaseModel):
    hotel_purchases: List[HotelPurchaseResponseSchema]


class HotelPurchaseReconciliationItemSchema(BaseModel):
    city: str
    category: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    bed_type: Optional[str] = None
    number_of_hajji: int = 0
    rooms_purchased: int = 0
    remaining: int = 0


class HotelPurchaseReconciliationResponseSchema(BaseModel):
    windows: List[HotelPurchaseReconciliationItemSchema]
