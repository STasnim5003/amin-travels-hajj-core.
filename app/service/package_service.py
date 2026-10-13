import math

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from app.service import package_assign_service
from data.repository import package_repository, admin_user_repository, package_assign_repository
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


def _validate_bed_type(bed_type) -> None:
    # Room types: {"<name>": <price>}; any number of them (at least one), names unique ignoring case.
    if not isinstance(bed_type, dict) or not bed_type:
        raise HTTPException(status_code=400, detail="bed_type must have at least one room type")
    seen = {}
    for name, price in bed_type.items():
        if not isinstance(name, str) or not name.strip():
            raise HTTPException(status_code=400, detail="Room type names can't be blank")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price):
            raise HTTPException(status_code=400, detail=f"Price of room type '{name}' must be a number")
        if price < 0:
            raise HTTPException(status_code=400, detail=f"Price of room type '{name}' can't be negative")
        key = package_assign_service._key(name)
        if key in seen:
            raise HTTPException(status_code=400,
                                detail=f"Room type '{name}' is repeated (same as '{seen[key]}'); names must be unique ignoring case")
        seen[key] = name


async def _reject_if_room_types_in_use(db: AsyncSession, existing_package: dict, new_bed_type: dict, agency_name: str):
    # A room type pilgrims are assigned to can't be removed or renamed; they'd keep a room type the package no longer has.
    kept = {package_assign_service._key(name) for name in new_bed_type}
    in_use = await package_assign_repository.count_assigned_pilgrims_by_bed_type(
        db, agency_name, existing_package["name"], existing_package.get("duration"), existing_package.get("hajj_year"))
    affected = [(name, count) for name, count in in_use if package_assign_service._key(name) not in kept]
    if affected:
        listing = ", ".join(f"'{name}' ({count} pilgrim{'s' if count != 1 else ''})" for name, count in sorted(affected))
        raise HTTPException(
            status_code=400,
            detail=f"Can't remove or rename room types that pilgrims are assigned to: {listing}. "
                   f"Move those pilgrims to another room type first.")


async def create_package(db: AsyncSession, package: PackageBaseSchema, agency_name: str,
                         username: str) -> PackageResponseSchema:
    _validate_bed_type(package.bed_type)
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
        if "bed_type" in update_data:
            _validate_bed_type(update_data["bed_type"])
            await _reject_if_room_types_in_use(db, existing_package, update_data["bed_type"], agency_name)
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
                old_duration=old_duration, new_duration=updated_package.duration,
                package_year=updated_package.hajj_year)
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
