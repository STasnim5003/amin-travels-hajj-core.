from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.repository import ziara_repository
from infrastructure.schema.ziara_schema import ZiaraCreateSchema, ZiaraResponseSchema, ZiaraBaseSchema, \
    ZiaraUpdateSchema


async def create_ziara_service(db: AsyncSession, ziara: ZiaraBaseSchema, agency_name: str, username:str):
    ziara_data = ziara.model_dump()
    ziara_data["agency_name"] = agency_name
    ziara_data["created_by"] = username
    ziara_data["updated_by"] = username
    response = await ziara_repository.create_ziara(db, ZiaraCreateSchema(**ziara_data))
    return ZiaraResponseSchema.model_validate(response)

async def get_ziara_by_id_service(db: AsyncSession, ziara_id: int, agency_name: str):
    response = await ziara_repository.get_ziara_by_id(db, ziara_id, agency_name)
    return ZiaraResponseSchema.model_validate(response)


async def get_all_ziaras_service(db: AsyncSession, agency_name: str):
    responses = await ziara_repository.get_all_ziaras(db, agency_name)
    return [ZiaraResponseSchema.model_validate(r) for r in responses]


async def update_ziara(db:AsyncSession, update_request:ZiaraUpdateSchema, agency_name:str, username:str):
    try:
        result = await ziara_repository.get_ziara_by_id(db, update_request.id, agency_name)
        if not result:
            raise HTTPException(status_code=400, detail="Ziara not found")

        update_request_dict = update_request.model_dump(exclude_unset=True)
        update_request_dict["updated_by"] = username
        update_request_dict["updated_at"] = get_current_time()

        updated_ziara = await ziara_repository.update_ziara(db, update_request_dict)
        return ZiaraResponseSchema.model_validate(updated_ziara)
    except Exception as e:
        raise e


async def delete_ziara(db:AsyncSession, ziara_id:int, agency_name:str):
    result = await ziara_repository.get_ziara_by_id(db, ziara_id, agency_name)
    if not result:
        raise HTTPException(status_code=400, detail="Ziara not found")
    await ziara_repository.delete_ziara(db, ziara_id)

    ziaras = await ziara_repository.get_all_ziaras(db, agency_name)
    return [ZiaraResponseSchema.model_validate(ziara) for ziara in ziaras]