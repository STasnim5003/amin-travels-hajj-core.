from typing import List

from fastapi import HTTPException

STAFF_ROLES = ["STAFF", "ACCOUNT_STAFF"]
# Roles an agency (or its staff) may create for its own agency; AGENCY/ADMIN/SUPER_ADMIN are excluded.
AGENCY_CREATABLE_ROLES = [*STAFF_ROLES, "GROUP_LEADER", "GUIDE", "SAUDI_REPRESENTATIVE", "SAUDI_REPRESENTATIVES",
                          "GROUND_STAFF"]


def has_required_permissions(current_user: dict, roles: List[str]):
    if current_user['role'] not in roles:
        raise HTTPException(status_code=403, detail='Unauthorized')

def check_agency_or_staff_user(current_user:dict):
    if current_user["role"] not in ["AGENCY", *STAFF_ROLES]:
        raise HTTPException(status_code=403, detail="Unauthorized")
