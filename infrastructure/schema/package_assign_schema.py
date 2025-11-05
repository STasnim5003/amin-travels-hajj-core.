from typing import Dict, Any, List, Optional

from pydantic import BaseModel

class PackageAssignBaseSchema(BaseModel):
    package_name: str
    package_duration: int
    package_bed_types: str
    total_payable: int
    add_ons_services: Optional[Dict[str, Any]] = None
    package_price_discount: Optional[int] = None


class PackageAssignSchema(PackageAssignBaseSchema):
    tracking_id: str


class PackageAssignForMultiplePilgrimSchema(PackageAssignBaseSchema):
    tracking_ids: List[str]

class PackageAssignUpdateSchema(BaseModel):
    tracking_id : str
    add_ons_services: Dict[str, Any]
    total_payable: int
    package_price_discount: Optional[int] = None

