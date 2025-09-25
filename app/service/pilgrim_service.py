from os import access
from pyexpat.errors import messages
from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.utils import verify_pilgrim_password, create_access_token_for_pilgrim, \
    create_refresh_token_for_pilgrim
from data.repository import pilgrim_repository
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, \
    BulkUpdatePilgrimRequestSchema, UpdatePilgrimResponseSchema, PilgrimLoginResponseSchema, PilgrimDataResponseSchema
from data.repository.pilgrim_repository import fetch_pilgrim_data_json


async def get_pilgrim_data(db: AsyncSession,
                           name: Optional[str],
                           tracking_id: Optional[str],
                           serial_no: Optional[str],
                           mobile_no: Optional[str],
                           group_name: Optional[str],
                           allocation_status: Optional[str],
                           page: int, limit: int) -> PaginatedPilgrimDataListResponseSchema:
    skip = (page - 1) * limit
    pilgrims, total = await fetch_pilgrim_data_json(db, name, tracking_id, serial_no, mobile_no, group_name, allocation_status, skip, limit)

    return PaginatedPilgrimDataListResponseSchema(
        data=pilgrims,
        total=total,
        page=page,
        size=limit
    )

async def update_pilgrim_data_approval_status(db: AsyncSession, data: BulkUpdatePilgrimRequestSchema, username:str):
    try:
        response = await pilgrim_repository.update_pilgrim_approval_status(data=data, db=db, username=username)

        pilgrim_response = UpdatePilgrimResponseSchema(
            message = "Successfully Updated",
            update_count = response
        )

        return pilgrim_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def pilgrim_login(db: AsyncSession, request_credentials : OAuth2PasswordRequestForm):
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_mobile_no(db,request_credentials.username)

        if not pilgrim:
            raise HTTPException(status_code=404, detail="Incorrect Mobile number or Password.")

        is_password_matched =  verify_pilgrim_password(request_credentials.password, pilgrim.password)
        if not is_password_matched:
            raise HTTPException(status_code=404, detail="Incorrect Mobile number or Password.")

        access_token = create_access_token_for_pilgrim(subject=pilgrim.name_bn,mobile_no=request_credentials.username, tracking_id=pilgrim.tracking_id)
        refresh_token = create_refresh_token_for_pilgrim(subject=pilgrim.name_bn, mobile_no=request_credentials.username, tracking_id=pilgrim.tracking_id)

        return PilgrimLoginResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

async def get_pilgrim_by_tracking_id(db:AsyncSession, tracking_id: str):
    return await pilgrim_repository.get_pilgrim_by_tracking_id(db,tracking_id)
