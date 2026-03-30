from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UmrahB2BAgentCreate(BaseModel):
    name: str
    details: Optional[str] = None


class UmrahB2BAgentUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    details: Optional[str] = None
    is_active: Optional[bool] = None


class UmrahB2BAgentResponse(UmrahB2BAgentCreate):
    id: int
    total_bill: int
    total_due: int
    total_credit: int
    agency_name: Optional[str]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class UmrahB2BAgentListResponse(BaseModel):
    b2b_agent_list: List[UmrahB2BAgentResponse]