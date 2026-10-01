from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import package_assign_service
from data.repository import package_repository, admin_user_repository
from infrastructure.schema.package_schema import PackageBaseSchema, PackageResponseSchema, PackageCreateSchema, \
    PackageUpdateSchema, PackageNameBaseSchema


async def get_packages(name, search, hajj_year, package_type, duration, description_type, hajj_month, agency_name, db):
    child_agencies = await admin_user_repository.get_mother_agencies(db=db, agency_name=agency_name)
    result = await package_repository.get_packages(db=db,
                                                   name=name,
                                                   search=search,
                                                   hajj_year=hajj_year,
                                                   package_type=package_type,
                                                   duration=duration,
                                                   description_type=description_type,
                                                   agencies=child_agencies,
                                                   hajj_month=hajj_month)
    return result


async def get_package_master_data_for_filter(db, package_type, description_type):
    result = await package_repository.get_package_master_data_for_filtering(db, package_type, description_type)
    return result


async def create_package(db: AsyncSession, package: PackageBaseSchema, agency_name: str,
                         username: str) -> PackageResponseSchema:
    try:
        package_data = package.model_dump()
        package_data["agency_name"] = agency_name
        package_data["created_by"] = username
        package_data["updated_by"] = username
        created_package = await package_repository.create_package(db, PackageCreateSchema(**package_data))

        if not created_package:
            raise

        return PackageResponseSchema.model_validate(created_package)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{str(e)}")


async def get_package_by_id(db: AsyncSession, package_id: int):
    return await package_repository.get_package_by_id(db, package_id)


async def get_package_by_id_for_agency(db: AsyncSession, package_id: int, agency_name: str):
    try:
        response = await package_repository.get_package_by_id_for_agency(db, package_id, agency_name)
        if response and response.get("agency_name") == agency_name:
            return response
        else:
            raise HTTPException(status_code=400, detail=f"{str(e)}")
    except Exception as e:
        raise e


async def update_package(db: AsyncSession, package_id: int, package: PackageUpdateSchema, agency_name: str,
                         username: str) -> PackageResponseSchema:
    try:
        existing_package = await package_repository.get_package_by_id_for_agency(db, package_id, agency_name)
        if not existing_package:
            raise HTTPException(status_code=400, detail="Package not found")

        update_data = package.model_dump(exclude_unset=True)
        update_data["updated_by"] = username
        update_data["updated_at"] = get_current_time()
        if not update_data:
            return existing_package

        old_bed_type, old_duration = existing_package.get("bed_type"), existing_package.get("duration")
        affects_bills = (
            ("bed_type" in update_data and update_data["bed_type"] != old_bed_type)
            or ("duration" in update_data and update_data["duration"] != old_duration)
        )

        updated_package = await package_repository.update_package(
            db, package_id, agency_name, update_data, commit=not affects_bills)
        response = PackageResponseSchema.model_validate(updated_package)

        if affects_bills:
            # Package prices are universal: re-bill every pilgrim on this package (commits), moving them
            # along if the duration changed.
            response.skipped_pilgrims = await package_assign_service.reprice_assigned_pilgrims(
                db, agency_name, username, package_name=existing_package["name"],
                old_duration=old_duration, new_duration=updated_package.duration)
        return response
    except Exception as e:
        raise e


async def create_package_names(db: AsyncSession, request: PackageNameBaseSchema, agency_name: str, username: str):
    try:
        request_dict = request.model_dump(exclude_unset=True)
        request_dict['agency_name'] = agency_name
        request_dict['created_by'] = username
        request_dict['updated_by'] = username

        return await package_repository.create_package_name(db, request_dict)
    except Exception as e:
        raise e


async def get_package_names(
        db: AsyncSession, agency_name: str
):
    try:
        return await package_repository.get_package_names(db, agency_name)
    except Exception as e:
        raise e


async def delete_package_name(db, package_name_id, agency_name):
    try:
        package_name = await package_repository.get_package_name_by_id(db, package_name_id)
        if not package_name or package_name.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Package Name not found")

        await package_repository.delete_package_name_by_id(db, package_name_id)

        return await package_repository.get_package_names(db, agency_name)

    except Exception as e:
        raise e


async def update_package_name(db, request, agency_name, username):
    try:
        package_name = await package_repository.get_package_name_by_id(db, request.id)
        if not package_name or package_name.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Package Name not found")
        request_dict = request.model_dump(exclude_unset=True)
        request_dict['updated_by'] = username

        return await package_repository.update_package_name(db, request_dict)
    except Exception as e:
        raise e


async def get_package_name_by_id(db, package_name_id, agency_name):
    try:
        result = await package_repository.get_package_name_by_id(db, package_name_id)
        if not result or result.agency_name != agency_name:
            raise HTTPException(status_code=400, detail="Package Name not found")
        return result
    except Exception as e:
        raise e


async def delete_package_by_id(db: AsyncSession, package_id: int, agency_name: str):
    try:
        package = await package_repository.get_package_by_id(db, package_id)
        if package and package['agency_name'] != agency_name:
            raise HTTPException(status_code=400, detail="Package Name not found")
        await package_repository.delete_package_by_id(db, package_id)
        return True
    except Exception as e:
        raise e
