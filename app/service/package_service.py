from http.client import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import package_repository
from infrastructure.schema.package_schema import PackageBaseSchema, PackageResponseSchema, PackageCreateSchema


async def get_packages(name, search, hajj_year, package_type, duration, description_type, hajj_month, agency_name,db):
    result = await package_repository.get_packages(db=db,
                                                   name=name,
                                                   search=search,
                                                   hajj_year=hajj_year,
                                                   package_type=package_type,
                                                   duration=duration,
                                                   description_type=description_type,
                                                   agency_name=agency_name,
                                                   hajj_month=hajj_month)
    return result


async def get_package_master_data_for_filter(db, package_type, description_type):
    result = await package_repository.get_package_master_data_for_filtering(db, package_type, description_type)
    return result

async def create_package(db: AsyncSession, package: PackageBaseSchema, agency_name : str) -> PackageResponseSchema:
    try:
        package_data = package.model_dump()
        package_data["agency_name"] = agency_name
        created_package = await package_repository.create_package(db, PackageCreateSchema(**package_data))

        if not created_package:
            raise

        return PackageResponseSchema.model_validate(created_package)
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"{str(e)}")

async def get_package_by_id(db:AsyncSession, package_id : int):
    return await package_repository.get_package_by_id(db, package_id)

async def get_package_by_id_for_agency(db: AsyncSession, package_id : int, agency_name : str):
    try:
        response = await package_repository.get_package_by_id_for_agency(db, package_id, agency_name)
        if response and response.get("agency_name") == agency_name:
            return response
        else:
            raise HTTPException(status_code=400,detail=f"{str(e)}")
    except Exception as e:
        raise e