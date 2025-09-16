from typing import Optional

import fastapi
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.service import pilgrim_service
from data.db.db_config import get_async_db
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

public_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@public_router.get("/pilgrim-data", response_model=PaginatedPilgrimDataListResponseSchema, tags=["Pilgrim"])
async def get_pilgrim_data(
        name: Optional[str] = Query(None),
        tracking_id: Optional[str] = Query(None),
        serial_no: Optional[str] = Query(None),
        mobile_no: Optional[str] = Query(None),
        group_name: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db)
) -> PaginatedPilgrimDataListResponseSchema:

    return await pilgrim_service.get_pilgrim_data(db, name, tracking_id, serial_no, mobile_no, group_name, page, limit)
