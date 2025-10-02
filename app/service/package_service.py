from http.client import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import package_repository
from infrastructure.schema.package_schema import PackageBaseSchema, PackageResponseSchema


async def get_packages(name, search, hajj_year, package_type, duration, description_type, hajj_month, db):
    result = await package_repository.get_packages(db=db,
                                                   name=name,
                                                   search=search,
                                                   hajj_year=hajj_year,
                                                   package_type=package_type,
                                                   duration=duration,
                                                   description_type=description_type,
                                                   hajj_month=hajj_month)
    return result


async def get_package_master_data_for_filter(db, package_type, description_type):
    result = await package_repository.get_package_master_data_for_filtering(db, package_type, description_type)
    return result

async def create_package(db: AsyncSession, package: PackageBaseSchema) -> PackageResponseSchema:
    try:
        created_package = await package_repository.create_package(db, package)

        if not created_package:
            raise

        return PackageResponseSchema.model_validate(created_package)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"{str(e)}"
        )

async def get_package_by_id(db:AsyncSession, package_id : int):
    return await package_repository.get_package_by_id(db, package_id)