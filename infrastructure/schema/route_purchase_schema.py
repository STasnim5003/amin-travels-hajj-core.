from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel


class RoutePurchaseBase(BaseModel):
    # Same shape as RouteDemandResponse.route_name/package_duration — copy these
    # straight out of GET /route-demand when creating a purchase against it.
    route_name: str
    package_duration: int
    transport_name: str
    vendor_name: Optional[str] = None
    seats_purchased: int
    cost: float
    currency: str = "BDT"
    purchase_date: Optional[str] = None
    booking_file: Optional[Any] = None
    remarks: Optional[str] = None


class RoutePurchaseCreateSchema(RoutePurchaseBase):
    pass


class RoutePurchaseUpdateSchema(BaseModel):
    id: int
    route_name: Optional[str] = None
    package_duration: Optional[int] = None
    transport_name: Optional[str] = None
    vendor_name: Optional[str] = None
    seats_purchased: Optional[int] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    purchase_date: Optional[str] = None
    booking_file: Optional[Any] = None
    remarks: Optional[str] = None


class RoutePurchaseResponseSchema(RoutePurchaseBase):
    id: int
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class RoutePurchaseListResponseSchema(BaseModel):
    route_purchases: List[RoutePurchaseResponseSchema]


class RoutePurchaseReconciliationItemSchema(BaseModel):
    route_name: str
    package_duration: int
    number_of_hajji: int = 0
    total_seats_purchased: int = 0
    remaining_seats: int = 0


class RoutePurchaseReconciliationResponseSchema(BaseModel):
    routes: List[RoutePurchaseReconciliationItemSchema]
