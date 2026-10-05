import re
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal

from pydantic import BaseModel, Field, field_validator, ConfigDict

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_email(value: Optional[str]) -> Optional[str]:
    value = (value or "").strip()
    if not value:
        return None
    if not EMAIL_RE.match(value):
        raise ValueError(f"Invalid email: {value}")
    return value


class _TrimmedModel(BaseModel):
    # trims every string; blank becomes None
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("*", mode="after")
    @classmethod
    def _blank_to_none(cls, v):
        return None if v == "" else v


class BillingContactSchema(_TrimmedModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v):
        return clean_email(v)


class BankAccountSchema(_TrimmedModel):
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[Literal["CURRENT", "SAVINGS"]] = None
    branch: Optional[str] = None
    routing_number: Optional[str] = None
    is_primary: bool = False

    @field_validator("account_type", mode="before")
    @classmethod
    def _account_type(cls, v):
        return v.strip().upper() or None if isinstance(v, str) else v


def normalize_bank_accounts(accounts: List[BankAccountSchema]) -> List[Dict[str, Any]]:
    """At most one primary; when none is marked the first one is primary."""
    if sum(a.is_primary for a in accounts) > 1:
        raise ValueError("Only one bank account can be primary")
    if accounts and not any(a.is_primary for a in accounts):
        accounts[0].is_primary = True
    return [a.model_dump() for a in accounts]


class PublicAgencySchema(BaseModel):
    """Issuing agency block on public (no-auth) PDF endpoints."""
    model_config = ConfigDict(from_attributes=True)

    agency_name: str
    agency_name_bn: Optional[str] = None
    license_number: Optional[str] = None
    umrah_license_number: Optional[str] = None
    logo: Optional[List[Dict[str, Any]]] = None
    address: Optional[str] = None
    office_phone: Optional[str] = None
    office_email: Optional[str] = None
    website: Optional[str] = None
    mobile_no: Optional[str] = None
    email: Optional[str] = None
    billing_contact: Optional[Dict[str, Any]] = None
    bank_accounts: Optional[List[Dict[str, Any]]] = None


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
    rfq_no : Optional[int] = None
    agency_name_bn: Optional[str] = None
    umrah_license_number: Optional[str] = None
    address: Optional[str] = None
    office_phone: Optional[str] = None
    office_email: Optional[str] = None
    website: Optional[str] = None
    billing_contact: Optional[Dict[str, Any]] = None
    bank_accounts: Optional[List[Dict[str, Any]]] = None
    signature: Optional[List[Dict[str, Any]]] = None
    seal: Optional[List[Dict[str, Any]]] = None
    signatory_name: Optional[str] = None
    signatory_designation: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminResponseSchema(AdminBaseSchema):
    id: int
    # nullable in the DB; one agency without them must not 500 the whole admin list
    license_number: Optional[str] = None
    mobile_no: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    password: Optional[str] = Field(default=None, exclude=True)
    # per-agency feature flags (e.g. {"umrah": true}); only filled on the logged-in profile endpoints
    features: Dict[str, bool] = Field(default_factory=dict)

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
    details: str

class LogoUpdateSchema(BaseModel):
    logo : Optional[List[Dict[str, Any]]] = None
    passport_copy: Optional[List[Dict[str, Any]]] = None