from typing import Dict, Any

from pydantic import BaseModel


class PackageAssignSchema(BaseModel):
    tracking_id : str
    package_name : str
    package_duration : int
    package_bed_types: str
    add_ons_services : Dict[str, Any]
    total_payable : int
