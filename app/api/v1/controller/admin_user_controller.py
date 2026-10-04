from typing import List

import fastapi
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user, get_current_admin_user
from app.core.utils.authorize_api import check_agency_or_staff_user, AGENCY_CREATABLE_ROLES
from app.service import admin_user_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_user_schema import AdminUserResponse, AdminUserCreate, GroupLeaderAssignSchema, \
    AdminUserResetPasswordSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimResponseForAdminUser

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")
public_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@private_router.get("/admin-user", response_model=List[AdminUserResponse], tags=["Admin User"])
async def list_admin_user(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_user_service.list_users(db, agency_name)


@private_router.get("/admin-user/profile", response_model=AdminUserResponse, tags=["Admin User"])
async def get_admin_user_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_admin_user)
) -> AdminUserResponse:
    code = current_user["code"]
    return await admin_user_service.get_admin_user_profile(db, code)


@private_router.get("/admin-user/pilgrim-data", response_model=PilgrimResponseForAdminUser, tags=["Admin User"])
async def get_pilgrim_data_by_admin_user(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_admin_user)
) -> PilgrimResponseForAdminUser:
    group_leader_code = current_user["code"]
    return await admin_user_service.get_pilgrim_data_by_admin_user(db, group_leader_code)


@private_router.get("/admin-user/{admin_id}", response_model=AdminUserResponse, tags=["Admin User"])
async def get_admin_user(admin_id: int, db: AsyncSession = Depends(get_async_db),
                         current_user: dict = Depends(get_current_user)):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_user_service.get_user(db, admin_id, agency_name)


@private_router.post("/admin-user", response_model=AdminUserResponse, tags=["Admin User"])
async def create_admin_user(
        user_data: AdminUserCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    if user_data.role not in AGENCY_CREATABLE_ROLES:
        raise HTTPException(status_code=400, detail=f"Role must be one of {AGENCY_CREATABLE_ROLES}")
    agency_name = current_user["agency_name"]
    # agency_name = "AMIN 26"
    username = current_user['username']
    return await admin_user_service.create_user(db, user_data, agency_name, username)


@public_router.post("/login", tags=["Admin User"])
async def admin_user_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    return await admin_user_service.admin_user_login(db, form_data)


@private_router.put("/assign-group-leader", tags=["Admin User"])
async def assign_group_leader(
        request_body: GroupLeaderAssignSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_user_service.assign_group_leader_to_pilgrims(db, request_body, agency_name)


@private_router.get("/group-leader-with-pilgrim-count", tags=["Admin User"])
async def get_group_leader_with_pilgrim_count(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await admin_user_service.get_group_leader_with_pilgrim_count(db, agency_name)

@private_router.post("/admin-user/reset-password", tags=["Admin User"])
async def reset_admin_user_password(
        request_body: AdminUserResetPasswordSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    username = current_user["username"]
    return await admin_user_service.reset_admin_user_password(db=db, request_body=request_body, username=username)