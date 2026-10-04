import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import has_required_permissions, STAFF_ROLES, PRP_FETCHER_ROLE
from app.service import script_service
from data.db.db_config import get_async_db
from infrastructure.schema.script_schema import PrpDataFetchRequestSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")
public_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@private_router.post("/fetch-prp-data", response_model=None, tags=["prp"])
async def prp_data_fetch_update(
        request: PrpDataFetchRequestSchema,
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", *STAFF_ROLES, PRP_FETCHER_ROLE])
    return await script_service.prp_data_fetch_update(current_user, request)


@private_router.get("/prp-agencies", tags=["prp"])
async def prp_agency_names_fetch(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN"])
    return await script_service.prp_agency_names_fetch(db)


@public_router.get("/agency-hajji-list", tags=["prp"])
async def agency_hajji_count_fetch(
        db: AsyncSession = Depends(get_async_db)
):
    result = await script_service.agency_hajji_count_fetch(db)
    return [r.model_dump(by_alias=False) for r in result]
