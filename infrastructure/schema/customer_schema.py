from typing import Optional, List

from pydantic import BaseModel


class CustomerCreateSchema(BaseModel):
    name_en : str
    name_bn : str
    nid: str
    date_of_birth : str
    mobile_no : Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class CustomerAppliedForRegistrationSchema(BaseModel):
    tracking_ids : List[str]

