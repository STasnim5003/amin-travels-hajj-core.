from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserBaseSchema(BaseModel):
    name: str
    whats_app_no : str
    nid_images : List[dict]
    hajj_year : Optional[int]
    discount_category: Optional[int]
    package_id: Optional[int]

    class Config:
        from_attributes = True
        populate_by_name = True

class UserResponseSchema(UserBaseSchema):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]
    is_active: Optional[bool]


class UsersResponseSchema(BaseModel):
    users: List[UserResponseSchema]
    class Config:
        from_attributes = True
        populate_by_name = True