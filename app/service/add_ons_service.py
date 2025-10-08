from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import add_ons_repository
from infrastructure.schema.add_ons_service_schema import AddOnsServiceBase, AddOnsServiceResponse


async def create_add_ons(db: AsyncSession, request: AddOnsServiceBase, agency_name: str):
    try:
        agency_name = agency_name
        created_by = agency_name

        service_data = request.model_dump()
        service_data.update({
            "agency_name": agency_name,
            "created_by": created_by,
            "updated_by": created_by,
        })

        new_service = await add_ons_repository.create_add_on_service(db, service_data)
        return AddOnsServiceResponse.model_validate(new_service)

    except Exception as e:
        raise e


async def get_all_add_on_services(db: AsyncSession, agency_name: str):
    try:
        services = await add_ons_repository.get_all_add_on_services(db, agency_name)
        return [AddOnsServiceResponse.model_validate(s) for s in services]
    except Exception as e:
        raise e


async def get_add_on_service_by_id(db: AsyncSession, service_id: int, agency_name: str):
    try:
        service = await add_ons_repository.get_add_on_service_by_id(db, service_id, agency_name)
        return AddOnsServiceResponse.model_validate(service)
    except Exception as e:
        raise e
