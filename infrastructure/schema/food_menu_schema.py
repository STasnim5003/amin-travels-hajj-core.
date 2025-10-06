from typing import Optional, Dict, Any
from pydantic import BaseModel


class FoodMenuBaseSchema(BaseModel):
    name: str
    items: Optional[Dict[str, Any]] = None
    is_publish: Optional[bool] = True
    area: str



class FoodMenuCreateSchema(FoodMenuBaseSchema):
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class FoodMenuUpdateSchema(FoodMenuBaseSchema):
    name: Optional[str] = None


class FoodMenuResponseSchema(FoodMenuBaseSchema):
    id: int
    agency_name: Optional[str] = None
    is_active: Optional[bool] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
