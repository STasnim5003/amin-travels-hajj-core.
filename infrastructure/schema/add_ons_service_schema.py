from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, field_validator


def _strip_name(value):
    # Add-on names are used as JSON keys in packages/pilgrims; stray whitespace splits one add-on into two keys.
    if isinstance(value, str):
        value = " ".join(value.split())
    return value


class AddOnsServiceBase(BaseModel):
    name: str
    price: str
    is_active: Optional[bool] = True
    # Defaults to the current open Hajj season.
    hajj_year: Optional[int] = None

    _normalize_name = field_validator("name", mode="before")(_strip_name)

class AddOnsServiceCreate(AddOnsServiceBase):
    pass


class AddOnsServiceResponse(BaseModel):
    id: int
    name: Optional[str] = None
    price: Optional[str] = None
    agency_name: Optional[str] = None
    hajj_year: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    # Set on update: assigned pilgrims that could not be re-billed with the new price.
    skipped_pilgrims: Optional[list[str]] = None

    class Config:
        from_attributes = True

class AddOnsServiceUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    price: Optional[str] = None
    is_active: Optional[bool] = True

    _normalize_name = field_validator("name", mode="before")(_strip_name)