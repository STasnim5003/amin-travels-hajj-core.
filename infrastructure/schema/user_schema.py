from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from infrastructure.schema.file_schema import FileUploadResponseSchema
from infrastructure.schema.package_schema import PackageBaseSchema, PackageResponseSchema


class UserBaseSchema(BaseModel):
    name: str
    whats_app_no : str
    nid_images : Optional[List[FileUploadResponseSchema]]
    hajj_year : Optional[int]
    discount_category: Optional[int]
    package_id: Optional[int] = None
    payment_status: Optional[str] = "PENDING"
    passport_images: Optional[List[FileUploadResponseSchema]]
    vaccine_center: Optional[str]
    registration_status: str = "PREREGISTERED"
    role: str = "PREREGISTERED_USER"
    username: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class UserResponseSchema(UserBaseSchema):
    id: int
    package: Optional[PackageResponseSchema] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None




class UsersResponseSchema(BaseModel):
    users: List[UserResponseSchema]
    total: Optional[int] = 0
    page: Optional[int] = 1
    limit: Optional[int] = 10
    class Config:
        from_attributes = True
        populate_by_name = True

class UpdateUserRequestSchema(BaseModel):
    passport_images: Optional[List[FileUploadResponseSchema]]
    vaccine_center: Optional[str]
    registration_status: str = "REGISTERED"
    role: str = "REGISTERED_USER"