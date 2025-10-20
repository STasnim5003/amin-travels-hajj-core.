import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.middleware.middleware import get_current_user
from app.service import package_assign_service
from data.db.db_config import get_async_db
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema

private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


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
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    agency_name = current_user["agency_name"]
    return await package_assign_service.get_bed_types_by_package_name(db, package_name, agency_name)


@private_router.post("/assign-package", tags=["package-assign"])
async def assign_package(
        request: PackageAssignSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Not Authorized")
    agency_name = current_user["agency_name"]
    return await package_assign_service.assign_package(db, request, agency_name)


@private_router.put("/update-assigned-package", tags=["package-assign"])
async def update_assign_package(
        request: PackageAssignUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Not Authorized")
    agency_name = current_user["agency_name"]
    return await package_assign_service.update_assigned_package(db, request, agency_name)


@private_router.get("/package-assigned-pilgrims", tags=["package-assign"])
async def get_package_assigned_pilgrims(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Not Authorized")
    agency_name = current_user["agency_name"]
    return await package_assign_service.get_package_assigned_pilgrims(db, agency_name)


@private_router.post("/assign-package-multiple-pilgrim", tags=["package-assign"])
async def assign_package_multiple_pilgrim(
        request: PackageAssignForMultiplePilgrimSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "AGENCY":
        raise HTTPException(status_code=403, detail="Not Authorized")
    agency_name = current_user["agency_name"]
    return await package_assign_service.assign_package_for_multiple_pilgrims(db, request, agency_name)
