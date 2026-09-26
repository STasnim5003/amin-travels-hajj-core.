from typing import Optional

import fastapi
from fastapi import Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import has_required_permissions, STAFF_ROLES
from app.service import training_user_service
from data.db.db_config import get_async_db
from infrastructure.schema.training_schema import TrainingUserResponseSchema, TrainingUserBaseSchema, \
    PaginatedTrainingUserResponseSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.post("/training-user", response_model=TrainingUserResponseSchema, tags=["training-users"])
async def create_user_endpoint(
        training_user: TrainingUserBaseSchema,
        db: AsyncSession = Depends(get_async_db)
):
    response = await training_user_service.create_training_user(training_user_request_schema=training_user, db=db)
    return JSONResponse(content=jsonable_encoder(response))


@router.get("/training-user", response_model=PaginatedTrainingUserResponseSchema, tags=["training-users"])
async def get_training_user_endpoint(
        name: Optional[str] = Query(None),
        whats_app_no: Optional[str] = Query(None),
        search: str = Query(None),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["ADMIN", "SUPER_ADMIN", "AGENCY", *STAFF_ROLES])
    return await training_user_service.fetch_training_users(db, name, whats_app_no, search, page, limit)
