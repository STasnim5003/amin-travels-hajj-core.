from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator


class FoodMenuBaseSchema(BaseModel):
    name: str
    items: Optional[Dict[str, Any]] = None
    is_publish: Optional[bool] = True
    area: str



class FoodMenuCreateSchema(FoodMenuBaseSchema):
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class FoodMenuUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    items: Optional[Dict[str, Any]] = None
    is_publish: Optional[bool] = True
    area: Optional[str] = None
    is_active: Optional[bool] = True



class FoodMenuResponseSchema(BaseModel):
    id: int
    name: Optional[str] = None
    items: Optional[Dict[str, Any]] = None
    area: Optional[str] = None
    agency_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_publish: Optional[bool] = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @field_validator("items", mode="before")
    def sort_items(cls, v):
        if not isinstance(v, dict):
            return v

        order = ["breakfast", "lunch", "dinner"]
        # Sort keys based on the order, keeping unknown keys at the end
        sorted_items = {k: v[k] for k in order if k in v}
        sorted_items.update({k: v[k] for k in v if k not in order})
        return sorted_items

    class Config:
        from_attributes = True


