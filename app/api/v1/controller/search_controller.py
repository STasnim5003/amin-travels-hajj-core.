import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import has_required_permissions, STAFF_ROLES
from app.service import search_service
from data.db.db_config import get_async_db

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["search"])


@private_router.get("/pilgrim-search", tags=["search"])
async def get_pilgrim_search(
        search_term: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "ADMIN", "AGENCY", *STAFF_ROLES])

    agency_name = None
    if current_user["role"] in ["AGENCY", *STAFF_ROLES]:
        agency_name = current_user["agency_name"]
    return await search_service.pilgrim_search_service(db, search_term, agency_name)
