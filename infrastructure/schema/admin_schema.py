from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class AdminBaseSchema(BaseModel):
    user_name: str
    password: str
    role: str
    agency_name: str
    license_number : str
    mobile_no : str
    location: Optional[str] = None
    email: Optional[str] = None
    passport_copy: Optional[List[Dict[str, Any]]] = None
    logo: Optional[List[Dict[str, Any]]] = None
    is_active: bool
    google_map_location : Optional[str] = None
    saudi_representatives : Optional[Dict[str, Any]] = None
    lead_agency : Optional[str] = None
    sar : Optional[float] = None
    bdt : Optional[float] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminResponseSchema(AdminBaseSchema):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    password: Optional[str] = Field(default=None, exclude=True)

class AdminListResponseSchema(BaseModel):
    data: List[AdminResponseSchema]
    page: int
    size: int
    total: int

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class AdminProfileUpdateSchema(BaseModel):
    user_name: str
    password: Optional[str] = None
    license_number: Optional[str] = None
    mobile_no: Optional[str] = None
    location: Optional[str]
    email: Optional[str]
    passport_copy: Optional[List[Dict[str, Any]]] = None
    logo: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class AdminProfileUpdateResponseSchema(BaseModel):
    message : str
    status: int

class AssignLeadAgencySchema(BaseModel):
    agency_name: Optional[str] = None
    lead_agency_name: str

class CheckLeadAssignResponseSchema(BaseModel):
    agency_name: Optional[str] = None
    lead_agency_name: Optional[str] = None

class PilgrimInfoSchemaForLeadAgency(BaseModel):
    name_en: Optional[str] = None
    name_bn: Optional[str] = None
    gender: Optional[str] = None
    tracking_id: Optional[str] = None
    serial_no: Optional[str] = None
    mobile_no: Optional[str] = None
    nid: Optional[str] = None
    passport_dob: Optional[str] = None
    passport_no: Optional[str] = None
    passport_expiry_date: Optional[str] = None
    passport_type: Optional[str] = None
    date_of_birth: Optional[str] = None
    pre_reg_voucher: Optional[str] = None
    reg_voucher: Optional[str] = None
    agency_name: Optional[str] = None


class AgencyPilgrimSummarySchemaForLeadAgency(BaseModel):
    agency_name: str
    total_pilgrims: int
    pilgrims: List[PilgrimInfoSchemaForLeadAgency]


class LeadAgencyPilgrimsResponseSchema(BaseModel):
    lead_agency_name: str
    agencies: List[AgencyPilgrimSummarySchemaForLeadAgency]

class SubAgencyAmountUpdateSchema(BaseModel):
    agency_name: str
    bdt:float
    sar:float