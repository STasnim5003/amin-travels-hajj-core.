from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import umrah_requisition_repository
from infrastructure.schema.umrah_requisition_schema import UmrahRequisitionBase, UmrahRequisitionResponseSchema


async def create_requisition(db: AsyncSession, request: UmrahRequisitionBase, agency_name: str):
    try:
        request_dict = request.model_dump()
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name

        saved = await umrah_requisition_repository.create(db, request_dict)
        return UmrahRequisitionResponseSchema.model_validate(saved)
    except Exception as e:
        raise e