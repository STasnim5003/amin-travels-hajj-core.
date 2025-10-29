import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import search_service
from data.db.db_config import get_async_db

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["search"])


@private_router.get("/pilgrim-search", tags=["search"])
async def get_pilgrim_search(
        search_term: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["SUPER_ADMIN", "ADMIN", "AGENCY"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    agency_name = None
    if current_user["role"] == "AGENCY":
        agency_name = current_user["agency_name"]
    return await search_service.pilgrim_search_service(db, search_term, agency_name)
