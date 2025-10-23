from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaymentCategoryBase(BaseModel):
    name: str

class PaymentCategoryResponse(PaymentCategoryBase):
    id : int
    updated_by: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PaymentCategoryUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    is_active: Optional[bool] = True