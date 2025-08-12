from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TrainingUserBaseSchema(BaseModel):
    name: str
    whats_app_no: str
    hajj_year: Optional[int]

    class Config:
        from_attributes = True
        populate_by_name = True


class TrainingUserResponseSchema(TrainingUserBaseSchema):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class PaginatedTrainingUserResponseSchema(BaseModel):
    users: List[TrainingUserResponseSchema]
    total: int
    page: int
    limit: int
