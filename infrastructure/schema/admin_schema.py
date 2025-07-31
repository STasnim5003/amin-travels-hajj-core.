from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AdminBaseSchema(BaseModel):
    user_name: str
    profile_pic: Optional[List[dict]]
    password: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminResponseSchema(AdminBaseSchema):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

# class UsersResponseSchema(UserBaseSchema):
#     users: List[UserResponseSchema]
#     class Config:
#         from_attributes = True
#         populate_by_name = True
