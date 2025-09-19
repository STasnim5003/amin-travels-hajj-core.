from http.client import responses
from typing import Optional

import fastapi
from fastapi import Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user, get_current_pilgrim
from app.service import pilgrim_service
from data.db.db_config import get_async_db
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, \
    UpdatePilgrimResponseSchema, BulkUpdatePilgrimRequestSchema, PilgrimLoginResponseSchema, PilgrimDataResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

public_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@private_router.get("/pilgrim-data", response_model=PaginatedPilgrimDataListResponseSchema, tags=["Pilgrim"])
async def get_pilgrim_data(
        name: Optional[str] = Query(None),
        tracking_id: Optional[str] = Query(None),
        serial_no: Optional[str] = Query(None),
        mobile_no: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> PaginatedPilgrimDataListResponseSchema:

    if current_user["role"] == "SUPER_ADMIN":
        return await pilgrim_service.get_pilgrim_data(db, name, tracking_id, serial_no, mobile_no, None, page, limit)
    else:
        group_name = current_user["agency_name"]
        return await pilgrim_service.get_pilgrim_data(db, name, tracking_id, serial_no, mobile_no, group_name, page,
                                                      limit)

@private_router.put("/pilgrim-data", response_model=UpdatePilgrimResponseSchema, tags=["Pilgrim"])
async def update_pilgrim_data(
        pilgrim_request_schema : BulkUpdatePilgrimRequestSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user:dict = Depends(get_current_user)
) -> UpdatePilgrimResponseSchema:
    if current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        return await pilgrim_service.update_pilgrim_data_approval_status(db, pilgrim_request_schema)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@public_router.post("/pilgrim/login", response_model=PilgrimLoginResponseSchema, tags=["Pilgrim"])
async def pilgrim_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
) -> PilgrimLoginResponseSchema:
    try:
        return await pilgrim_service.pilgrim_login(db, form_data)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@private_router.get("/pilgrim/profile", response_model=PilgrimDataResponseSchema, tags=["Pilgrim"])
async def get_pilgrim_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_pilgrim)
) -> PilgrimDataResponseSchema:

    tracking_id = current_user.get("tracking_id")
    if not tracking_id:
        raise HTTPException(status_code=400, detail="Tracking ID is missing in user context")

    result = await pilgrim_service.get_pilgrim_by_tracking_id(db, tracking_id)

    return PilgrimDataResponseSchema.model_validate(result)