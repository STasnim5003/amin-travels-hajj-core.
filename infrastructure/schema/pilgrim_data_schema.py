from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PilgrimDataBaseSchema(BaseModel):
    name_bn: str
    father_name: Optional[str] = None
    spouse_name: Optional[str] = None
    occupation: Optional[str] = None
    nid: Optional[str] = None
    voucher: Optional[str] = None
    type: Optional[str] = None
    listed_in: Optional[str] = None
    mother_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    management: Optional[str] = None
    mobile_no: Optional[str] = None
    passport_address: Optional[str] = None
    present_address: Optional[str] = None
    permanent_address: Optional[str] = None
    tracking_id: Optional[str] = None
    serial_no: Optional[str] = None
    group_name: Optional[str] = None
    registration_status: Optional[str] = None


    class Config:
        from_attributes = True
        populate_by_name = True

class PilgrimDataResponseSchema(PilgrimDataBaseSchema):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class PaginatedPilgrimDataListResponseSchema(BaseModel):
    total: int
    size : int
    page : int
    data : Optional[List[PilgrimDataResponseSchema]]

class PilgrimUpdateSchema(BaseModel):
    tracking_id : str
    group_name : str
    is_assigned : bool

class BulkUpdatePilgrimRequestSchema(BaseModel):
    data : List[PilgrimUpdateSchema]

class UpdatePilgrimResponseSchema(BaseModel):
    message: str
    update_count: int