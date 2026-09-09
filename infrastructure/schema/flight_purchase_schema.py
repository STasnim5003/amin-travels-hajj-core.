from datetime import datetime
from typing import Optional, Any, Dict, List

from pydantic import BaseModel


class FlightPurchaseBase(BaseModel):
    # Same shape as FlightDemandResponse.flight_date_start/end
    # (e.g. {"english_calendar": "...", "arabic_calendar": "..."}) — copy the window
    # straight out of GET /flight-demand when creating a purchase against it.
    flight_date_start: Dict[str, Any]
    flight_date_end: Dict[str, Any]
    airline_name: str
    vendor_name: Optional[str] = None
    pnr: str
    seats_purchased: int
    cost: float
    currency: str = "BDT"
    purchase_date: Optional[str] = None
    ticket_file: Optional[Any] = None
    remarks: Optional[str] = None


class FlightPurchaseCreateSchema(FlightPurchaseBase):
    pass


class FlightPurchaseUpdateSchema(BaseModel):
    id: int
    flight_date_start: Optional[Dict[str, Any]] = None
    flight_date_end: Optional[Dict[str, Any]] = None
    airline_name: Optional[str] = None
    vendor_name: Optional[str] = None
    pnr: Optional[str] = None
    seats_purchased: Optional[int] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    purchase_date: Optional[str] = None
    ticket_file: Optional[Any] = None
    remarks: Optional[str] = None


class FlightPurchaseResponseSchema(FlightPurchaseBase):
    id: int
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class FlightPurchaseListResponseSchema(BaseModel):
    flight_purchases: List[FlightPurchaseResponseSchema]


class FlightPurchaseReconciliationItemSchema(BaseModel):
    flight_date_start: Optional[Any]
    flight_date_end: Optional[Any]
    number_of_hajji: int = 0
    total_seats_purchased: int = 0
    remaining_seats: int = 0


class FlightPurchaseReconciliationResponseSchema(BaseModel):
    windows: List[FlightPurchaseReconciliationItemSchema]
