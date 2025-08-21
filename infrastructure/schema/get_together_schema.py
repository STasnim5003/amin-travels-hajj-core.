from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


# ========== Program Schemas ==========
class GetTogetherProgramBase(BaseModel):
    name: Optional[str]
    program_date: Optional[date]
    registration_deadline: Optional[date]
    program_venue: Optional[str]
    total_seat: Optional[int]
    description: Optional[str]


class GetTogetherProgramCreateSchema(GetTogetherProgramBase):
    pass


class GetTogetherProgramResponse(GetTogetherProgramBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    is_active: bool


    class Config:
        orm_mode = True
        from_attributes = True


# ========== Registration Schemas ==========
class GetTogetherRegistrationBase(BaseModel):
    name: str
    phone_no: str
    no_of_attendance: int
    get_together_program_id: int


class GetTogetherRegistrationCreateSchema(GetTogetherRegistrationBase):
    pass


class GetTogetherRegistrationResponse(GetTogetherRegistrationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    is_active: bool

    program: Optional[GetTogetherProgramResponse]

    class Config:
        orm_mode = True
        from_attributes = True

class PaginatedGetTogetherParticipantsResponseSchema(BaseModel):
    participants: List[GetTogetherRegistrationResponse]
    total: int
    page: int
    limit: int