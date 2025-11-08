from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class CityNameBaseSchema(BaseModel):
    name: str

class CityNameCreateSchema(CityNameBaseSchema):
    pass

class CityNameUpdateSchema(BaseModel):
    id: int
    name : Optional[str] = None
    is_active: Optional[bool] = None


class CityNameResponseSchema(CityNameBaseSchema):
    id: int
    agency_name: Optional[str] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class CityNameListResponseSchema(BaseModel):
    city_names: List[CityNameResponseSchema]
