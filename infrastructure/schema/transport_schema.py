from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TransportServiceBaseSchema(BaseModel):
    name: str
    seats: str


class TransportServiceCreateSchema(TransportServiceBaseSchema):
    pass


class TransportServiceUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    seats: Optional[str] = None
    is_active: Optional[bool] = None


class TransportServiceResponseSchema(TransportServiceBaseSchema):
    id: int
    agency_name: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class TransportServiceListResponseSchema(BaseModel):
    transport_services: List[TransportServiceResponseSchema]
