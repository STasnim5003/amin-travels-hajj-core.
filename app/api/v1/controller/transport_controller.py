from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import transport_service
from data.db.db_config import get_async_db
from infrastructure.schema.transport_schema import TransportServiceResponseSchema, TransportServiceCreateSchema, \
    TransportServiceListResponseSchema, TransportServiceUpdateSchema

private_router = APIRouter(prefix="/amin-travels-hajj-core/api/v1/private", tags=["Transport Service"])


@private_router.post("/transport-service", response_model=TransportServiceResponseSchema)
async def create_transport_service(
        request: TransportServiceCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user['agency_name']
    return await transport_service.create_transport_service(db, request, agency_name)


@private_router.get("/transport-service", response_model=TransportServiceListResponseSchema)
async def get_transport_services(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user['agency_name']
    return await transport_service.get_transport_service_list(db, agency_name)


@private_router.put("/transport-service")
async def update_transport_service(
        request: TransportServiceUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user['agency_name']
    return await transport_service.update_transport_service(db, request, agency_name)
