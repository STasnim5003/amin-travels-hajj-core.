from typing import List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_pilgrim, get_current_user
from app.service import view_field_service
from data.db.db_config import get_async_db
from infrastructure.schema.view_field_schema import ViewFieldResponseSchema, ViewFieldSchema, \
    ViewFieldListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/view", response_model=ViewFieldResponseSchema, tags=["View Fields"])
async def create_view(
        request_body: ViewFieldSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> ViewFieldResponseSchema:

    role = current_user.get("role")
    username = current_user.get("username")

    if role not in ["SUPER_ADMIN","ADMIN", "AGENCY"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    request_body = ViewFieldSchema(
        view_name=request_body.view_name,
        field_name = request_body.field_name,
    )

    return await view_field_service.create_view(db, request_body, username)

@private_router.get("/view", response_model=ViewFieldListResponseSchema, tags=["View Fields"])
async def get_all_views(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> ViewFieldListResponseSchema:
    username = current_user.get("username")
    return await view_field_service.get_views(db, username)
