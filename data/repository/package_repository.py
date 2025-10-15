from attr import attributes
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from data.filter.query_filter import filter_query
from data.model.package_model import PackageModel
from infrastructure.schema.package_schema import PackageResponseSchema, PackageMasterDataForFilterSchema, \
    PackageMasterDataForFilterListSchema, PackageBaseSchema, PackageCreateSchema


async def get_packages(db: AsyncSession,
                       name: str = None,
                       search: str = None,
                       hajj_year: int = None,
                       package_type: str = None,
                       duration: int = None,
                       description_type: str = None,
                       hajj_month: str = None,
                       agency_name:str= None):
    try:
        # Start query
        query = (select(PackageModel)
                 .options(joinedload(PackageModel.route))
                 .options(joinedload(PackageModel.food_menu))
                 .options(joinedload(PackageModel.ziara))
                 )

        # Apply filters
        if name:
            query = query.where(PackageModel.name == name)
        if hajj_year:
            query = query.where(PackageModel.hajj_year == hajj_year)
        if package_type:
            query = query.where(PackageModel.package_type == package_type)
        if duration:
            query = query.where(PackageModel.duration == duration)
        if description_type:
            query = query.where(PackageModel.description_type == description_type)
        if hajj_month:
            query = query.where(PackageModel.hajj_month == hajj_month)
        if agency_name:
            query = query.where(PackageModel.agency_name == agency_name)
        query = query.where(PackageModel.is_publish == True)

        query = query.order_by(PackageModel.id.asc())

        # Execute query
        result = await db.execute(query)
        packages = result.scalars().all()

        # Convert to Pydantic with locations
        packages_response = []
        for package in packages:
            package_data = PackageResponseSchema.model_validate(package).model_dump()
            package_data["locations"] = {
                "makkah": package.makkah or [],
                "madinah": package.madinah or [],
                "azizia": package.azizia or [],
                "others_feature": package.others_feature or [],
                "includes": package.includes or [],
                "hotel_info": package.hotel_info or [],
                "excludes": package.excludes or []
            }
            for field in ["makkah", "madinah", "azizia", "others_feature", "includes", "hotel_info", "excludes"]:
                package_data.pop(field, None)
            packages_response.append(package_data)

        return packages_response

    except Exception as e:
        raise e


async def get_package_master_data_for_filtering(
        db: AsyncSession,
        package_type: str = None,
        description_type: str = None
):
    filters = []

    if package_type:
        filters.append(PackageModel.package_type == package_type)
    if description_type:
        filters.append(PackageModel.description_type == description_type)

    stmt = (
        select(
            PackageModel.hajj_month,
            PackageModel.hajj_year,
            PackageModel.duration,
            PackageModel.name,
            PackageModel.description_type,
            PackageModel.package_type,
        )
        .where(*filters)
        .distinct()
    )

    result = await db.execute(stmt)
    rows = result.all()
    master_data = []
    for row in rows:
        master_data.append(PackageMasterDataForFilterSchema.model_validate(row).model_dump())
    return master_data

async def get_package_by_id(db:AsyncSession, package_id : int):
    query = (
        select(PackageModel)
        .options(joinedload(PackageModel.route))
        .options(joinedload(PackageModel.food_menu))
        .options(joinedload(PackageModel.ziara))
        .where(PackageModel.id == package_id)
    )
    result = await db.execute(query)
    package = result.scalars().one_or_none()
    return PackageResponseSchema.model_validate(package).model_dump()



async def create_package(db: AsyncSession, payload: PackageCreateSchema) -> PackageModel:
    package = PackageModel(**payload.model_dump())
    try:
        db.add(package)
        await db.commit()
        await db.refresh(package, attribute_names=["route", "ziara", "food_menu"],)
        return package
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )

async def get_package_by_id_for_agency(db: AsyncSession, package_id:int, agency_name : str):
    try:
        query = (
            select(PackageModel)
            .options(joinedload(PackageModel.route))
            .options(joinedload(PackageModel.food_menu))
            .options(joinedload(PackageModel.ziara))
            .where(PackageModel.id == package_id)
        )
        result = await db.execute(query)
        package = result.scalars().one_or_none()
        return PackageResponseSchema.model_validate(package).model_dump()
    except Exception as e:
        raise e

async def update_package(db: AsyncSession, package_id: int, agency_name: str, update_data: dict):
    stmt = (
            update(PackageModel)
            .where(
                PackageModel.id == package_id,
                PackageModel.agency_name == agency_name
            )
            .values(**update_data)
            .returning(PackageModel)
        )
    result = await db.execute(stmt)
    updated_package = result.scalar_one_or_none()
    await db.commit()

    if not updated_package:
        raise HTTPException(status_code=400, detail="Package not found after update")

    await db.refresh(updated_package, attribute_names=["route", "ziara", "food_menu"])

    return updated_package