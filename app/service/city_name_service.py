from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import city_name_repository
from infrastructure.schema.city_name_schema import CityNameCreateSchema, CityNameResponseSchema, \
    CityNameListResponseSchema


async def create_city_name(db:AsyncSession, request : CityNameCreateSchema, agency_name : str):
    try:
        request_dict = request.model_dump()
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = agency_name
        request_dict['updated_by'] = agency_name

        result = await city_name_repository.create_city_name(db,request_dict)
        return CityNameResponseSchema.model_validate(result)
    except Exception as e:
        raise e


async def get_city_name(db:AsyncSession, agency_name:str):
    try:
        result = await city_name_repository.get_city_names(db,agency_name)
        city_names = []
        for city in result:
            city_names.append(CityNameResponseSchema.model_validate(city))
        return CityNameListResponseSchema(city_names=city_names)
    except Exception as e:
        raise e