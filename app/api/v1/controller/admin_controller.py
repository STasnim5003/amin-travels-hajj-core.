import fastapi
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.service import admin_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_schema import AdminResponseSchema, AdminBaseSchema, TokenSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.post("/admin", response_model=AdminResponseSchema, tags=["admin"])
async def create_admin_endpoint(
        admin: AdminBaseSchema,
        db: AsyncSession = Depends(get_async_db)
):
    response = await admin_service.create_admin(admin_request_schema=admin, db=db)
    return JSONResponse(content=jsonable_encoder(response))


@router.post("/login", summary="Admin login", response_model=TokenSchema, tags=["admin"])
async def create_admin_login_endpoint(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    return await admin_service.admin_login(db, form_data)
