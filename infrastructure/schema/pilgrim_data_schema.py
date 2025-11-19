from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from infrastructure.schema.view_field_schema import ViewFieldResponseSchema


class PilgrimDataBaseSchema(BaseModel):
    name_en: Optional[str] = None
    name_bn: Optional[str] = None
    tracking_id: Optional[str] = None
    serial_no: Optional[str] = None
    mobile_no: Optional[str] = None
    nid: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    spouse_name: Optional[str] = None
    family_code: Optional[str] = None
    group_name: Optional[str] = None
    sub_group: Optional[str] = None
    occupation: Optional[str] = None
    voucher: Optional[str] = None
    type: Optional[str] = None
    listed_in: Optional[str] = None
    management: Optional[str] = None
    passport_address: Optional[str] = None
    present_address: Optional[str] = None
    permanent_address: Optional[str] = None
    registration_status: Optional[str] = None
    is_assigned: Optional[bool] = None
    allocation_status: Optional[str] = None
    vaccination_center: Optional[str] = None
    passport_copy: Optional[List[Dict[str, Any]]] = None
    lead_agency: Optional[str] = None
    sub_reference : Optional[str] = None
    passport_dob : Optional[str] = None
    passport_expiry_date: Optional[str] = None
    pre_reg_voucher : Optional[str] = None
    reg_voucher : Optional[str] = None
    passport_type : Optional[str] = None


    class Config:
        from_attributes = True
        populate_by_name = True


class PilgrimDataResponseSchema(PilgrimDataBaseSchema):
    id: int
    package_id: Optional[int] = None
    package_name: Optional[str] = None
    comment_on_package: Optional[str] = None
    passport_no: Optional[str] = None
    payment_status: Optional[str] = None
    reference: Optional[str] = None
    group_leader: Optional[str] = None
    total_payable: Optional[int] = 0
    total_payment: Optional[int] = 0
    total_due : Optional[int] = 0
    total_available_amount : Optional[int] = 0
    package_price_discount: Optional[int] = 0
    package_bed_types: Optional[str] = None
    package_duration: Optional[int] = None
    add_ons_services: Optional[Dict[str, Any]] = None
    is_package_assigned: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None



class PaginatedPilgrimDataListResponseSchema(BaseModel):
    total: int
    size: int
    page: int
    data: Optional[List[PilgrimDataResponseSchema]] = None
    views: Optional[List[ViewFieldResponseSchema]] = None
    counts: Optional[Dict[str, int]] = None


class PilgrimUpdateSchema(BaseModel):
    tracking_id: str
    group_name: str
    is_assigned: bool


class BulkUpdatePilgrimRequestSchema(BaseModel):
    data: List[PilgrimUpdateSchema]


class UpdatePilgrimResponseSchema(BaseModel):
    message: str
    update_count: int


class PilgrimLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class PilgrimRegistrationRequestSchema(BaseModel):
    vaccination_center: str
    passport_copy: List[Dict[str, Any]]
    tracking_id: str
    package_id: int
    comment_on_package: Optional[str] = None


class PilgrimMinimalResponseSchema(BaseModel):
    id: int
    name_en: Optional[str] = None
    name_bn: Optional[str] = None
    passport_no: Optional[str] = None
    mobile_no: Optional[str] = None
    registration_status: Optional[str] = None
    group_name: Optional[str] = None
    sub_group: Optional[str] = None
    total_payable: Optional[int] = None
    total_payment: Optional[int] = None
    group_leader: Optional[str] = None

    class Config:
        from_attributes = True


class PilgrimResponseForAdminUser(BaseModel):
    pilgrims: Optional[List[PilgrimMinimalResponseSchema]] = None
    total: Optional[int] = None
    total_payable : Optional[int] = None
    total_due : Optional[int] = None
    total_payment : Optional[int] = None

class PilgrimFamilyGroupAssign(BaseModel):
    tracking_ids : List[str]
    family_code: str
