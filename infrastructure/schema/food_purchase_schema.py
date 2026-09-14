from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel


class FoodPurchaseBase(BaseModel):
    # Same shape as FoodDemandResponse.food_name/items — copy these straight out
    # of GET /food-demand when creating a purchase against it.
    food_name: str
    items: Optional[Any] = None
    vendor_name: Optional[str] = None
    meals_purchased: int
    cost: float
    currency: str = "BDT"
    purchase_date: Optional[str] = None
    booking_file: Optional[Any] = None
    remarks: Optional[str] = None


class FoodPurchaseCreateSchema(FoodPurchaseBase):
    pass


class FoodPurchaseUpdateSchema(BaseModel):
    id: int
    food_name: Optional[str] = None
    items: Optional[Any] = None
    vendor_name: Optional[str] = None
    meals_purchased: Optional[int] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    purchase_date: Optional[str] = None
    booking_file: Optional[Any] = None
    remarks: Optional[str] = None


class FoodPurchaseResponseSchema(FoodPurchaseBase):
    id: int
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class FoodPurchaseListResponseSchema(BaseModel):
    food_purchases: List[FoodPurchaseResponseSchema]


class FoodPurchaseReconciliationItemSchema(BaseModel):
    food_name: str
    number_of_hajji: int = 0
    total_meals_purchased: int = 0
    remaining_meals: int = 0


class FoodPurchaseReconciliationResponseSchema(BaseModel):
    food_items: List[FoodPurchaseReconciliationItemSchema]
