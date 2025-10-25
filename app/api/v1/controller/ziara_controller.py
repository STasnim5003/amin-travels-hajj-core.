import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import ziara_service
from data.db.db_config import get_async_db
from infrastructure.schema.ziara_schema import ZiaraResponseSchema, ZiaraCreateSchema, ZiaraBaseSchema, \
    ZiaraUpdateSchema

ziara_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@ziara_router.post("/ziara", response_model=ZiaraResponseSchema, tags=["Ziara"])
async def create_ziara(
        ziara: ZiaraBaseSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await ziara_service.create_ziara_service(db, ziara, agency_name)


@ziara_router.get("/ziara/{ziara_id}", response_model=ZiaraResponseSchema, tags=["Ziara"])
async def get_ziara(ziara_id: int, db: AsyncSession = Depends(get_async_db),current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    db_ziara = await ziara_service.get_ziara_by_id_service(db, ziara_id, agency_name)
    if not db_ziara:
        raise HTTPException(status_code=404, detail="Ziara not found")
    return db_ziara


@ziara_router.get("/ziaras", response_model=list[ZiaraResponseSchema], tags=["Ziara"])
async def get_all_ziaras(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await ziara_service.get_all_ziaras_service(db, agency_name)

@ziara_router.put("/ziara", response_model=ZiaraResponseSchema, tags=["Ziara"])
async def update_ziara(
        update_request: ZiaraUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await ziara_service.update_ziara(db, update_request, agency_name)

@ziara_router.delete("/ziara/{ziara_id}", tags=["Ziara"])
async def delete_ziara(
        ziara_id:int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]

    return await ziara_service.delete_ziara(db, ziara_id, agency_name)
