import fastapi
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.service.user_service import create_user
from data.db.db_config import get_async_db
from infrastructure.schema.user_schema import UserResponseSchema, UserBaseSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.post("/users", response_model=UserResponseSchema, tags=["users"])
@inject
async def create_user_endpoint(
        user: UserBaseSchema,
        db: AsyncSession = Depends(get_async_db)
):
    response = await create_user(user_request_schema=user, db=db)
    return JSONResponse(content=jsonable_encoder(response))

