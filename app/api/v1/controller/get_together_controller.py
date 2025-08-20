import fastapi
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.service import get_together_service
from data.db.db_config import get_async_db
from infrastructure.schema.get_together_schema import GetTogetherProgramCreateSchema, \
    GetTogetherRegistrationCreateSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/get-together", tags=["get-together"])
async def create_get_together_by_admin(
        program_data: GetTogetherProgramCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    response = await  get_together_service.create_get_together_program(program_data, db)
    return JSONResponse(content=jsonable_encoder(response))

@router.post("/get-together-registration", tags=["get-together"])
async def registration_user_for_get_together(
        registration_data: GetTogetherRegistrationCreateSchema,
        db: AsyncSession = Depends(get_async_db)
):

    response = await get_together_service.create_get_together_registration(registration_data, db)
    return JSONResponse(content=jsonable_encoder(response))
