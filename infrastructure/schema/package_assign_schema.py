from typing import Dict, Any, List, Optional

from pydantic import BaseModel

class PackageAssignBaseSchema(BaseModel):
    package_name: str
    package_duration: int
    package_bed_types: str
    # Ignored: the server prices the package from the bed type + add-ons. Kept so old clients still validate.
    total_payable: Optional[int] = None
    add_ons_services: Optional[Dict[str, Any]] = None
    package_price_discount: Optional[int] = None


class PackageAssignSchema(PackageAssignBaseSchema):
    tracking_id: str


class PackageAssignForMultiplePilgrimSchema(PackageAssignBaseSchema):
    tracking_ids: List[str]


class PackageAssignUpdateItemSchema(BaseModel):
    # Any field left out keeps the pilgrim's current value.
    tracking_id: str
    package_name: Optional[str] = None
    package_duration: Optional[int] = None
    package_bed_types: Optional[str] = None
    add_ons_services: Optional[Dict[str, Any]] = None
    package_price_discount: Optional[int] = None


class PackageAssignUpdateSchema(PackageAssignUpdateItemSchema):
    # Either a single pilgrim (top-level fields) or many at once via `items`.
    tracking_id: Optional[str] = None
    total_payable: Optional[int] = None  # ignored, see PackageAssignBaseSchema
    items: Optional[List[PackageAssignUpdateItemSchema]] = None
