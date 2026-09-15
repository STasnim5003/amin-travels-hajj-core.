import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import agency_profile_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_schema import AdminResponseSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.get("/agency-profile", response_model=AdminResponseSchema, tags=["agency-profile"])
async def get_agency_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminResponseSchema:
    username = current_user["username"]
    agency_name = current_user["agency_name"]
    return await agency_profile_service.get_agency_profile(db=db, username=username, agency_name=agency_name)
