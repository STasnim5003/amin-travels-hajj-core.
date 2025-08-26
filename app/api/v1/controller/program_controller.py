import fastapi
from fastapi import Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.service import program_service
from data.db.db_config import get_async_db
from infrastructure.schema.program_schema import ProgramCreateSchema, \
    ProgramRegistrationCreateSchema, ProgramUpdateSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/program", tags=["program"])
async def create_get_together_by_admin(
        program_data: ProgramCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    response = await  program_service.create_get_together_program(program_data, db)
    return JSONResponse(content=jsonable_encoder(response))


@router.post("/program-registration", tags=["program"])
async def registration_user_for_get_together(
        registration_data: ProgramRegistrationCreateSchema,
        db: AsyncSession = Depends(get_async_db)
):
    response = await program_service.create_get_together_registration(registration_data, db)
    return JSONResponse(content=jsonable_encoder(response))


@router.get("/program", tags=["program"])
async def get_all_available_programs(
        program_type: str = "GET_TOGETHER",
        is_active: bool = True,
        db: AsyncSession = Depends(get_async_db)
):
    response = await program_service.get_active_programs(db, program_type, is_active)
    return JSONResponse(content=jsonable_encoder(response))


@private_router.get("/program-participants/{program_id}", tags=["program"])
async def find_participants_by_program_id(
        program_id: int,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await program_service.fetch_participants_by_program_id(program_id, db, page, limit)


@private_router.get("/all-programs", tags=["program"])
async def get_all_programs(
        program_type: str = "GET_TOGETHER",
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    return await program_service.get_all_programs(db, program_type)


@private_router.patch("/program/{program_id}", tags=["program"])
async def update_program(
        program_id: int,
        program_data: ProgramUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    response = await  program_service.update_program(db, program_id, program_data)
    return JSONResponse(content=jsonable_encoder(response))


@private_router.delete("/program/{program_id}", tags=["program"])
async def delete_program(
        program_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    await program_service.delete_program(db, program_id)
    return JSONResponse(status_code=200, content={"message": "Program deleted successfully"})
