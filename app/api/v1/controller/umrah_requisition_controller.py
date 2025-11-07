import fastapi
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import umrah_requisition_service
from data.db.db_config import get_async_db
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionResponseSchema, UmrahRequisitionBase

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")

@private_router.post("/umrah-requisition", response_model=UmrahRequisitionResponseSchema, tags = ['Umrah Requisition'])
async def create_umrah_requisition(
        request : UmrahRequisitionBase,
        db: AsyncSession = Depends(get_async_db),
        current_user : dict = Depends(get_current_user)
) -> UmrahRequisitionResponseSchema:
    if current_user['role'] != 'AGENCY':
        raise HTTPException(status_code=403, detail='Unauthorized')
    agency_name = current_user['agency_name']
    return await umrah_requisition_service.create_requisition(db=db, request=request, agency_name=agency_name)