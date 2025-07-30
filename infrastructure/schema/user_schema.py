from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserBaseSchema(BaseModel):
    name: str
    whats_app_no : str = Field(alias="whatsAppNo")
    nid_images : List[dict] = Field(alias="nidImages")
    hajj_year : Optional[int] = Field(None, alias="hajjYear")
    discount_category: Optional[int] = Field(None, alias="discountCategory")
    package_id: Optional[int] = Field(None, alias="packageId")

    class Config:
        from_attributes = True
        populate_by_name = True

class UserResponseSchema(UserBaseSchema):
    id: int
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
    is_active: Optional[bool] = Field(None, alias="isActive")

