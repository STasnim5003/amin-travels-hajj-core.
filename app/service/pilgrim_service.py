from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema
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
        pilgrims=pilgrims,
        total=total,
        page=page,
        size=limit
    )