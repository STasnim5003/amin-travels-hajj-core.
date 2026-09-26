from typing import List

from fastapi import HTTPException

STAFF_ROLES = ["STAFF", "ACCOUNT_STAFF"]


def has_required_permissions(current_user: dict, roles: List[str]):
    if current_user['role'] not in roles:
        raise HTTPException(status_code=403, detail='Unauthorized')

def check_agency_or_staff_user(current_user:dict):
    if current_user["role"] not in ["AGENCY", *STAFF_ROLES]:
        raise HTTPException(status_code=403, detail="Unauthorized")
