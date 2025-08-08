from typing import List, Dict, Optional

from pydantic import BaseModel


class PackageBaseSchema(BaseModel):
    name: str
    discount: Optional[str]
    price: int
    locations: Dict[str, List[str]]


class PackageResponseSchema(PackageBaseSchema):
    id: int

    class Config:
        from_attributes = True
        populate_by_name = True


class PackagesResponseSchema(BaseModel):
    packages: List[PackageResponseSchema]

    class Config:
        from_attributes = True
        populate_by_name = True
