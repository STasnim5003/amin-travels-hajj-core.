from datetime import date, datetime
from typing import List, Dict, Optional, Any

from pydantic import BaseModel

from infrastructure.schema.food_menu_schema import FoodMenuResponseSchema
from infrastructure.schema.route_schema import RouteResponseSchema
from infrastructure.schema.ziara_schema import ZiaraResponseSchema


class PackageBaseSchema(BaseModel):
    name: str
    discount: Optional[str] = None
    price: Optional[int] = None
    hajj_year: int
    duration: Optional[int] = None
    description_type: Optional[str] = None
    package_type: str
    is_publish: Optional[bool] = None

    # New fields from migration
    duration_range: Optional[Dict[str, Any]] = None
    makkah: Optional[Dict[str, Any]] = None
    madinah: Optional[Dict[str, Any]] = None
    azizia: Optional[Dict[str, Any]] = None
    flight_date: Optional[Dict[str, Any]] = None
    bed_type: Optional[Dict[str, Any]] = None
    return_ticket: Optional[str] = None
    fixed_or_shifting: Optional[str] = None
    food_menu_id: Optional[int] = None
    ziara_id: Optional[int] = None
    special_services: Optional[Dict[str, Any]] = None
    other_services: Optional[Dict[str, Any]] = None
    route_id: Optional[int] = None
    airlines: Optional[str] = None


    @property
    def locations(self) -> dict:
        return {
            "makkah": self.makkah or [],
            "madinah": self.madinah or [],
            "azizia": self.azizia or [],
            "others_feature": self.others_feature or [],
        }

class PackageCreateSchema(PackageBaseSchema):
    agency_name: Optional[str] = None

class PackageResponseSchema(PackageBaseSchema):
    id: int
    route: Optional[RouteResponseSchema] = None
    agency_name: Optional[str] = None
    ziara: Optional[ZiaraResponseSchema] = None
    food_menu: Optional[FoodMenuResponseSchema] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        extra = "allow"


class PackagesResponseSchema(BaseModel):
    packages: List[PackageResponseSchema]

    class Config:
        from_attributes = True
        populate_by_name = True
        extra = "allow"


class PackageMasterDataForFilterSchema(BaseModel):
    hajj_month: str
    hajj_year: int
    name: Optional[str]
    duration: Optional[int]
    description_type: Optional[str]
    package_type: str

    class Config:
        from_attributes = True
        populate_by_name = True


class PackageMasterDataForFilterListSchema(BaseModel):
    master_data_for_filter: List[PackageMasterDataForFilterSchema]

    class Config:
        from_attributes = True
        populate_by_name = True
        extra = "allow"

class PackageUpdateSchema(BaseModel):
    discount: Optional[str] = None
    price: Optional[int] = None
    duration: Optional[int] = None
    description_type: Optional[str] = None
    is_publish: Optional[bool] = None

    # New fields from migration
    duration_range: Optional[Dict[str, Any]] = None
    makkah: Optional[Dict[str, Any]] = None
    madinah: Optional[Dict[str, Any]] = None
    azizia: Optional[Dict[str, Any]] = None
    flight_date: Optional[Dict[str, Any]] = None
    bed_type: Optional[Dict[str, Any]] = None
    return_ticket: Optional[str] = None
    fixed_or_shifting: Optional[str] = None
    food_menu_id: Optional[int] = None
    ziara_id: Optional[int] = None
    special_services: Optional[Dict[str, Any]] = None
    other_services: Optional[Dict[str, Any]] = None
    route_id: Optional[int] = None
    airlines: Optional[str] = None

class PackageNameBaseSchema(BaseModel):
    name: str

class PackageNameResponseSchema(PackageNameBaseSchema):
    id: int
    agency_name : Optional[str] = None
    created_by : Optional[str] = None
    updated_by : Optional[str] = None
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None

class PackageNameUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None