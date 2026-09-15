import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import has_required_permissions
from app.service import agency_profile_service
from data.db.db_config import get_async_db
from infrastructure.schema.agency_profile_schema import AgencyProfileListResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.get("/agency-profile", response_model=AgencyProfileListResponseSchema, tags=["agency-profile"])
async def get_agency_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AgencyProfileListResponseSchema:
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", "STAFF"])
    return await agency_profile_service.get_agency_profiles(db=db)
