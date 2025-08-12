from typing import List, Dict, Optional

from pydantic import BaseModel


class PackageBaseSchema(BaseModel):
    name: str
    discount: Optional[str]
    price: Optional[int]
    locations: Optional[Dict[str, List[str]]]
    hajj_year: int
    duration: Optional[int]
    description_type: Optional[str]
    package_type: str
    hajj_month : Optional[str]




class PackageResponseSchema(PackageBaseSchema):
    id: int

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
