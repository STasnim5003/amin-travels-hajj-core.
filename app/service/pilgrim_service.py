from pyexpat.errors import messages
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import pilgrim_repository
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, \
    BulkUpdatePilgrimRequestSchema, UpdatePilgrimResponseSchema
from data.repository.pilgrim_repository import fetch_pilgrim_data_json


async def get_pilgrim_data(db: AsyncSession,
                           name: Optional[str],
                           tracking_id: Optional[str],
                           serial_no: Optional[str],
                           mobile_no: Optional[str],
                           group_name: Optional[str],
                           page: int, limit: int) -> PaginatedPilgrimDataListResponseSchema:
    skip = (page - 1) * limit
    pilgrims, total = await fetch_pilgrim_data_json(db, name, tracking_id, serial_no, mobile_no, group_name, skip, limit)

    return PaginatedPilgrimDataListResponseSchema(
        data=pilgrims,
        total=total,
        page=page,
        size=limit
    )

async def update_pilgrim_data_approval_status(db: AsyncSession, data: BulkUpdatePilgrimRequestSchema):
    try:
        response = await pilgrim_repository.update_pilgrim_approval_status(data=data, db=db)

        pilgrim_response = UpdatePilgrimResponseSchema(
            message = "Successfully Updated",
            update_count = response
        )

        return pilgrim_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))