from typing import List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import admin_user_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_user_schema import AdminUserResponse, AdminUserCreate

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.get("/admin-user", response_model=List[AdminUserResponse], tags=["Admin User"])
async def list_admin_user(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await admin_user_service.list_users(db,agency_name)


@private_router.get("/admin-user/{admin_id}", response_model=AdminUserResponse, tags=["Admin User"])
async def get_admin_user(admin_id: int, db: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await admin_user_service.get_user(db, admin_id, agency_name)


@private_router.post("/admin-user", response_model=AdminUserResponse, tags=["Admin User"])
async def create_admin_user(
        user_data: AdminUserCreate,
        db: AsyncSession = Depends(get_async_db),
        # current_user: dict = Depends(get_current_user)
):
    # if current_user["role"] != "AGENCY":
    #     raise HTTPException(status_code=400, detail="Unauthorized")
    # agency_name = current_user["agency_name"]
    agency_name = "AMIN 26"
    return await admin_user_service.create_user(db, user_data, agency_name)
