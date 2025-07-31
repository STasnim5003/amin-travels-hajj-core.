from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PackageBaseSchema(BaseModel):
    name : str
    description : str
    price : int

    class Config:
        from_attributes = True
        populate_by_name = True

class PackageResponseSchema(PackageBaseSchema):
    id: int

class PackagesResponseSchema(BaseModel):
    packages: List[PackageResponseSchema]

    class Config:
        from_attributes = True
        populate_by_name = True
