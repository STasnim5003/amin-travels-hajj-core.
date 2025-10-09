import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import add_ons_service
from data.db.db_config import get_async_db
from infrastructure.schema.add_ons_service_schema import AddOnsServiceResponse, AddOnsServiceBase

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/add-ons-service", response_model=AddOnsServiceResponse, tags = ["Add-Ons"])
async def create_add_ons(
        request : AddOnsServiceBase,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=400, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await add_ons_service.create_add_ons(db, request, agency_name)

@private_router.get("/add-ons-service", response_model=list[AddOnsServiceResponse], tags = ["Add-Ons"])
async def list_add_on_services(
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await add_ons_service.get_all_add_on_services(db, agency_name)


@private_router.get("/add-ons-service/{service_id}", response_model=AddOnsServiceResponse, tags = ["Add-Ons"])
async def get_add_on_service(
    service_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Unauthorized")
    agency_name = current_user["agency_name"]
    return await add_ons_service.get_add_on_service_by_id(db, service_id, agency_name)