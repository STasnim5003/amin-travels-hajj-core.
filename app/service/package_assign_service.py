from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.service import pilgrim_payment_service
from data.repository import package_assign_repository, pilgrim_payment_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema
from infrastructure.schema.payment_schema import PaymentSchema


async def get_all_package_names(db: AsyncSession, agency_name: str):
    return await package_assign_repository.get_all_package_names(db, agency_name)


async def get_durations_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_durations_by_package_name(db, package_name, agency_name)


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_bed_types_by_package_name(db, package_name, agency_name)

async def assign_package(db:AsyncSession, request : PackageAssignSchema, agency_name : str):
    try:
        return await package_assign_repository.assign_package(db, request, agency_name)
    except Exception as e:
        raise e