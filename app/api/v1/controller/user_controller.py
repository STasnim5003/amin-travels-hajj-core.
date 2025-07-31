import fastapi
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.service import user_service
from data.db.db_config import get_async_db
from infrastructure.schema.user_schema import UserResponseSchema, UserBaseSchema, UsersResponseSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.post("/users", response_model=UserResponseSchema, tags=["users"])
@inject
async def create_user_endpoint(
        user: UserBaseSchema,
        db: AsyncSession = Depends(get_async_db)
):
    response = await user_service.create_user(user_request_schema=user, db=db)
    return JSONResponse(content=jsonable_encoder(response))



@router.get("/users", response_model=UsersResponseSchema, tags=["users"])
@inject
async def get_users_endpoint(
        name:str =None,
        whats_app_no: str=None,
        db: AsyncSession = Depends(get_async_db)
):
    response = await user_service.get_users(name=name, whats_app_no=whats_app_no, db=db)
    return JSONResponse(content=jsonable_encoder(response))