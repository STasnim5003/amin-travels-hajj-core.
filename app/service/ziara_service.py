from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import ziara_repository
from infrastructure.schema.ziara_schema import ZiaraCreateSchema, ZiaraResponseSchema, ZiaraBaseSchema


async def create_ziara_service(db: AsyncSession, ziara: ZiaraBaseSchema, agency_name: str):
    ziara_data = ziara.model_dump()
    ziara_data["agency_name"] = agency_name
    ziara_data["created_by"] = agency_name
    ziara_data["updated_by"] = agency_name
    response = await ziara_repository.create_ziara(db, ZiaraCreateSchema(**ziara_data))
    return ZiaraResponseSchema.model_validate(response)

async def get_ziara_by_id_service(db: AsyncSession, ziara_id: int, agency_name: str):
    response = await ziara_repository.get_ziara_by_id(db, ziara_id, agency_name)
    return ZiaraResponseSchema.model_validate(response)


async def get_all_ziaras_service(db: AsyncSession, agency_name: str):
    responses = await ziara_repository.get_all_ziaras(db, agency_name)
    return [ZiaraResponseSchema.model_validate(r) for r in responses]
