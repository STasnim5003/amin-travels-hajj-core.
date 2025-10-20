from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from data.repository import package_assign_repository, pilgrim_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema
from infrastructure.schema.payment_schema import PaymentSchema


async def get_all_package_names(db: AsyncSession, agency_name: str):
    return await package_assign_repository.get_all_package_names(db, agency_name)


async def get_durations_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_durations_by_package_name(db, package_name, agency_name)


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_bed_types_by_package_name(db, package_name, agency_name)


async def assign_package(db: AsyncSession, request: PackageAssignSchema, agency_name: str):
    try:
        return await package_assign_repository.assign_package(db, request, agency_name)
    except Exception as e:
        raise e


async def update_assigned_package(db: AsyncSession, request: PackageAssignUpdateSchema, agency_name: str):
    try:
        if request.total_payable < 0:
            raise HTTPException(status_code=400, detail="Payment Amount Must be Positive")

        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, request.tracking_id)
        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim not found")
        if pilgrim.group_name != agency_name or not pilgrim.is_package_assigned:
            raise HTTPException(status_code=400, detail="This pilgrim not in your agency")

        prev_total_payable = pilgrim.total_payable
        prev_total_payment = pilgrim.total_payment

        new_total_payable = prev_total_payable + request.total_payable
        discount = request.package_price_discount or 0

        request_dict = request.model_dump(exclude_unset=True)
        filtered_data = {k: v for k, v in request_dict.items() if v is not None}

        # Add computed values
        filtered_data.update({
            "total_payable": new_total_payable,
            "total_available_amount": max(0, prev_total_payment - new_total_payable),
            "total_due": max(0, new_total_payable - prev_total_payment),
            "actual_payable": new_total_payable - discount,
            "updated_by": agency_name,
            "add_ons_services" : request.add_ons_services
        })

        payable_create_schema = PaymentSchema(
            description="Package Update",
            date=datetime.today().strftime('%Y-%m-%d'),
            amount=new_total_payable,
            category="Payable",
            tracking_id=request.tracking_id
        )

        return await package_assign_repository.update_assigned_package(db, filtered_data, payable_create_schema,
                                                                       agency_name)

    except Exception as e:
        raise e


async def get_package_assigned_pilgrims(db: AsyncSession, agency_name: str):
    try:
        return await package_assign_repository.get_package_assigned_pilgrims(db, agency_name)
    except Exception as e:
        raise e


async def assign_package_for_multiple_pilgrims(db: AsyncSession, request: PackageAssignForMultiplePilgrimSchema,
                                               agency_name: str):
    try:
        return await package_assign_repository.assign_package_for_multiple_pilgrim(db, request, agency_name)
    except Exception as e:
        raise e
