from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import add_ons_repository
from infrastructure.schema.add_ons_service_schema import AddOnsServiceBase, AddOnsServiceResponse, \
    AddOnsServiceUpdateSchema


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


async def update_add_ons_service(db:AsyncSession, update_request:AddOnsServiceUpdateSchema, agency_name:str):
    try:
        result = await add_ons_repository.get_add_on_service_by_id(db, update_request.id, agency_name)
        if not result:
            raise HTTPException(status_code=400, detail=f'Add on service not found')

        update_request_dict = update_request.model_dump(exclude_unset=True)
        update_request_dict['updated_by'] = agency_name

        updated_add_ons = await add_ons_repository.update_add_ons_service(db, update_request_dict)
        return AddOnsServiceResponse.model_validate(updated_add_ons)
    except Exception as e:
        raise e


async def delete_add_on_service(db:AsyncSession, service_id:int, agency_name:str):
    try:
        result = await add_ons_repository.get_add_on_service_by_id(db, service_id, agency_name)
        if not result:
            raise HTTPException(status_code=400, detail=f'Add on service not found')

        await add_ons_repository.delete_add_ons_service(db, service_id)

        add_ons_services = await add_ons_repository.get_all_add_on_services(db, agency_name)
        return [AddOnsServiceResponse.model_validate(service) for service in add_ons_services]
    except Exception as e:
        raise e