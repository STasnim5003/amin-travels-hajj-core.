from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import package_assign_service
from data.repository import add_ons_repository
from infrastructure.schema.add_ons_service_schema import AddOnsServiceBase, AddOnsServiceResponse, \
    AddOnsServiceUpdateSchema


async def create_add_ons(db: AsyncSession, request: AddOnsServiceBase, agency_name: str,username:str):
    try:
        agency_name = agency_name
        created_by = agency_name

        service_data = request.model_dump()
        service_data.update({
            "agency_name": agency_name,
            "created_by": username,
            "updated_by": username,
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


def _parse_price(price):
    if price is None:
        return None
    try:
        value = float(str(price).replace(",", "").strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Add-on price must be a number")
    return int(value) if value.is_integer() else value


async def update_add_ons_service(db:AsyncSession, update_request:AddOnsServiceUpdateSchema, agency_name:str, username:str):
    try:
        result = await add_ons_repository.get_add_on_service_by_id(db, update_request.id, agency_name)
        if not result:
            raise HTTPException(status_code=400, detail=f'Add on service not found')

        update_request_dict = update_request.model_dump(exclude_unset=True)
        update_request_dict['updated_by'] = username
        update_request_dict['updated_at'] = get_current_time()

        package_sync = None
        if 'name' in update_request_dict or 'price' in update_request_dict:
            package_sync = {
                "agency_name": agency_name,
                "old_name": result.name,
                "new_name": update_request_dict.get('name') or " ".join(result.name.split()),
                "new_price": _parse_price(update_request_dict.get('price')),
            }

        # Captured before the update: the ORM refreshes `result` with the new values.
        old_name, old_price, old_active = result.name, _parse_price(result.price), result.is_active
        new_name = " ".join((update_request_dict.get('name') or old_name).split())
        affects_bills = (
            new_name != " ".join(old_name.split())
            or ('price' in update_request_dict and _parse_price(update_request_dict['price']) != old_price)
            or update_request_dict.get('is_active', old_active) != old_active
        )

        updated_add_ons = await add_ons_repository.update_add_ons_service(
            db, update_request_dict, package_sync, commit=not affects_bills)
        response = AddOnsServiceResponse.model_validate(updated_add_ons)

        if affects_bills:
            # Add-on prices are universal: re-bill every assigned pilgrim that has this add-on (commits).
            response.skipped_pilgrims = await package_assign_service.reprice_assigned_pilgrims(
                db, agency_name, username, add_on_old_name=old_name, add_on_new_name=new_name)
        return response
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