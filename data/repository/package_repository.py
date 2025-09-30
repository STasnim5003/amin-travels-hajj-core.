from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.filter.query_filter import filter_query
from data.model.package_model import PackageModel
from infrastructure.schema.package_schema import PackageResponseSchema, PackageMasterDataForFilterSchema, \
    PackageMasterDataForFilterListSchema, PackageBaseSchema


async def get_packages(db: AsyncSession,
                       name: str = None,
                       search: str = None,
                       hajj_year: int = None,
                       package_type: str = None,
                       duration: int = None,
                       description_type: str = None,
                       hajj_month: str = None):
    try:
        packages, count = await filter_query(
            db=db,
            model=PackageModel,
            name=name,
            search=search,
            hajj_year=hajj_year,
            package_type=package_type,
            duration=duration,
            description_type=description_type,
            hajj_month=hajj_month,
            search_fields=["name", "hajj_year", "package_type", "duration", "description_type", "hajj_month"],
            sort_by=[("id", "asc")],
            is_active=True,
        )
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

            package_data.pop("makkah", None)
            package_data.pop("madinah", None)
            package_data.pop("azizia", None)
            package_data.pop("others_feature", None)
            package_data.pop("includes", None)
            package_data.pop("hotel_info", None)
            package_data.pop("excludes", None)

            packages_response.append(package_data)
        return packages_response
    except Exception as e:
        raise


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
    query = select(PackageModel).where(PackageModel.id == package_id)
    result = await db.execute(query)
    package = result.scalars().one_or_none()
    return PackageResponseSchema.model_validate(package).model_dump()

async def create_package(db: AsyncSession, payload: PackageBaseSchema) -> PackageModel:
    package = PackageModel(**payload.model_dump())
    try:
        db.add(package)
        await db.commit()
        await db.refresh(package)
        return package
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )

