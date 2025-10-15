from typing import Dict, Any, Optional

from pydantic import BaseModel


class PackageAssignSchema(BaseModel):
    tracking_id : str
    package_name : str
    package_duration : int
    package_bed_types: str
    add_ons_services : Dict[str, Any]
    total_payable : int
    discount: Optional[int] = None

class PackageAssignUpdateSchema(BaseModel):
    tracking_id : str
    add_ons_services: Dict[str, Any]
    total_payable: int
    package_price_discount: Optional[int] = None

