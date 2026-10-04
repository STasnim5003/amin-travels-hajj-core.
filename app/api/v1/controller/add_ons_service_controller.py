import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import add_ons_service
from data.db.db_config import get_async_db
from infrastructure.schema.add_ons_service_schema import AddOnsServiceResponse, AddOnsServiceBase, \
    AddOnsServiceUpdateSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/add-ons-service", response_model=AddOnsServiceResponse, tags=["Add-Ons"])
async def create_add_ons(
        request: AddOnsServiceBase,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await add_ons_service.create_add_ons(db, request, agency_name, username)


@private_router.get("/add-ons-service", response_model=list[AddOnsServiceResponse], tags=["Add-Ons"])
async def list_add_on_services(
        hajj_year: int | None = None,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await add_ons_service.get_all_add_on_services(db, agency_name, hajj_year)


@private_router.put("/add-ons-service", response_model=AddOnsServiceResponse, tags=["Add-Ons"])
async def update_add_on_service(
        update_request: AddOnsServiceUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await add_ons_service.update_add_ons_service(db, update_request, agency_name, username)


@private_router.get("/add-ons-service/{service_id}", response_model=AddOnsServiceResponse, tags=["Add-Ons"])
async def get_add_on_service(
        service_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await add_ons_service.get_add_on_service_by_id(db, service_id, agency_name)


@private_router.delete("/add-ons-service/{service_id}", tags=["Add-Ons"])
async def delete_add_ons_service(
        service_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)
    agency_name = current_user["agency_name"]
    return await add_ons_service.delete_add_on_service(db, service_id, agency_name)
