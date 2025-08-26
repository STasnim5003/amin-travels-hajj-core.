from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


# ========== Program Schemas ==========
class ProgramBaseSchema(BaseModel):
    name: Optional[str]
    program_date: Optional[date]
    registration_deadline: Optional[date]
    program_venue: Optional[str]
    total_seat: Optional[int]
    description: Optional[str]
    venue_address : Optional[str]
    venue_map_location : Optional[str]
    start_time : Optional[str]
    program_type : str


class ProgramCreateSchema(ProgramBaseSchema):
    pass

class ProgramUpdateSchema(BaseModel):
    name: Optional[str]
    program_date: Optional[date]
    registration_deadline: Optional[date]
    program_venue: Optional[str]
    total_seat: Optional[int]
    description: Optional[str]
    venue_address: Optional[str]
    venue_map_location: Optional[str]
    start_time: Optional[str]
    is_active: Optional[bool]
    program_type: Optional[str]

    class Config:
        orm_mode = True

class ProgramResponseSchema(ProgramBaseSchema):
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
class ProgramRegistrationBaseSchema(BaseModel):
    name: str
    phone_no: str
    no_of_attendance: int
    get_together_program_id: int


class ProgramRegistrationCreateSchema(ProgramRegistrationBaseSchema):
    pass


class ProgramRegistrationResponse(ProgramRegistrationBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    is_active: bool

    program: Optional[ProgramResponseSchema]

    class Config:
        orm_mode = True
        from_attributes = True

class PaginatedProgramParticipantsResponseSchema(BaseModel):
    participants: List[ProgramRegistrationResponse]
    total: int
    page: int
    limit: int