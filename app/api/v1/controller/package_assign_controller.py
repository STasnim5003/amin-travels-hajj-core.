import logging

import fastapi
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import check_agency_or_staff_user
from app.service import package_assign_service
from data.db.db_config import get_async_db
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema, PackageUnassignSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")
audit_logger = logging.getLogger("pilgrim_audit")


@private_router.get("/packages/names", tags=["package-assign"])
async def get_package_names(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    agency_name = current_user["agency_name"]
    return await package_assign_service.get_all_package_names(db, agency_name)


@private_router.get("/{package_name}/duration", tags=["package-assign"])
async def get_duration_by_package_name(
        package_name: str,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    agency_name = current_user["agency_name"]
    return await package_assign_service.get_durations_by_package_name(db, package_name, agency_name)


@private_router.get("/{package_name}/bed-types", tags=["package-assign"])
async def get_bed_types_by_package_name(
        package_name: str,
        duration: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    agency_name = current_user["agency_name"]
    return await package_assign_service.get_bed_types_by_package_name(db, package_name, duration, agency_name)


@private_router.put("/update-assigned-package", tags=["package-assign"])
async def update_assign_package(
        request: PackageAssignUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await package_assign_service.update_assigned_package(db, request, agency_name, username)


@private_router.get("/package-assigned-pilgrims", tags=["package-assign"])
async def get_package_assigned_pilgrims(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    return await package_assign_service.get_package_assigned_pilgrims(db, agency_name)


@private_router.post("/assign-package-multiple-pilgrim", tags=["package-assign"])
async def assign_package_multiple_pilgrim(
        request: PackageAssignForMultiplePilgrimSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await package_assign_service.assign_package_for_multiple_pilgrims(db, request, agency_name, username)


@private_router.put("/change-package", tags=['package-assign'])
async def change_package(
        request: PackageAssignSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    return await package_assign_service.change_assigned_package(db=db, request=request, agency_name=agency_name, username=username)


@private_router.put("/unassign-package", tags=["package-assign"])
async def unassign_package(
        request: PackageUnassignSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    check_agency_or_staff_user(current_user=current_user)

    agency_name = current_user["agency_name"]
    username = current_user["username"]
    result = await package_assign_service.unassign_package(db=db, request=request, agency_name=agency_name, username=username)
    audit_logger.info(
        "AUDIT package unassign by user=%s role=%s agency=%s tracking_ids=%s",
        current_user.get("username"), current_user.get("role"), agency_name, request.tracking_ids,
    )
    return result
