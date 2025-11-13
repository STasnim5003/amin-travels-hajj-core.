from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, update, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from urllib3 import request

from data.model.admin_user_model import AdminUserModel
from data.model.package_model import PackageModel
from data.model.payment_model import PaymentModel
from data.model.pilgrim_data_model import PilgrimDataModel
from data.repository import pilgrim_payment_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignForMultiplePilgrimSchema
from infrastructure.schema.payment_schema import PaymentSchema


# TODO : package er sthe agency diye filter korte hobe
async def get_all_package_names(db: AsyncSession, agency_name: str):
    stmt = (
        select(PackageModel.name)
        .where(
            PackageModel.package_type == "HAJJ",
            PackageModel.agency_name == agency_name
        )
        .distinct()
    )
    result = await db.execute(stmt)
    names = [row[0] for row in result.fetchall()]
    return names


async def get_durations_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    stmt = (
        select(PackageModel.duration)
        .where(
            PackageModel.name == package_name,
            PackageModel.package_type == "HAJJ",
            PackageModel.agency_name == agency_name
        )
        .distinct()
    )
    result = await db.execute(stmt)
    durations = [row[0] for row in result.fetchall()]
    if not durations:
        raise HTTPException(status_code=404, detail=f"No durations found for {package_name}")
    return durations


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    stmt = (
        select(PackageModel.bed_type)
        .where(
            PackageModel.name == package_name,
            PackageModel.package_type == "HAJJ",
            PackageModel.agency_name == agency_name
        )
    )
    result = await db.execute(stmt)
    bed_type_json = result.scalars().first()
    if not bed_type_json:
        raise HTTPException(status_code=400, detail=f"No bed types found for {package_name}")
    return bed_type_json


async def assign_package(db: AsyncSession, request: PackageAssignSchema, agency_name: str):
    try:
        pilgrim_result = await db.execute(
            select(PilgrimDataModel).where(PilgrimDataModel.tracking_id == request.tracking_id)
        )
        pilgrim = pilgrim_result.scalar_one_or_none()

        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim not found")

        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=403, detail="Agency Name Mismatched")

        # Update Pilgrim Payable info
        prev_total_payable = pilgrim.total_payable
        prev_total_payment = pilgrim.total_payment

        await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == request.tracking_id)
            .values(
                package_name=request.package_name,
                package_duration=request.package_duration,
                package_bed_types=request.package_bed_types,
                add_ons_services=request.add_ons_services,
                updated_by=agency_name,
                is_package_assigned=True
            )
        )

        payable_schema = PaymentSchema(
            description="Hajj Package & Add ons bill",
            date=datetime.today().strftime('%Y-%m-%d'),
            amount=request.total_payable,
            tracking_id=request.tracking_id,
            category="Payable"
        )
        await pilgrim_payment_repository.create_payable_for_pilgrim(
            db, payable_schema, agency_name, None, prev_total_payable, prev_total_payment
        )

        return {"message": "Successfully Updated"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def update_assigned_package(
        db: AsyncSession,
        request_dict: dict,
        payable_create_schema: PaymentSchema,
        agency_name: str
):
    try:
        # Step 1: Update pilgrim and return the updated record
        stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == request_dict["tracking_id"])
            .values(**request_dict)
            .returning(PilgrimDataModel)
        )

        result = await db.execute(stmt)
        updated_pilgrim = result.scalar_one_or_none()

        if not updated_pilgrim:
            await db.rollback()
            raise HTTPException(status_code=404, detail="Pilgrim not found for update")

        # Step 2: Prepare payment data and insert new record
        payable_create_schema_dict = payable_create_schema.model_dump()
        payable_create_schema_dict.update({
            "created_by": agency_name,
            "updated_by": agency_name
        })

        await db.execute(
            insert(PaymentModel).values(**payable_create_schema_dict)
        )

        # Step 3: Commit both operations
        await db.commit()

        return updated_pilgrim

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def get_package_assigned_pilgrims(db: AsyncSession, agency_name: str):
    try:
        stmt = (
            select(PilgrimDataModel)
            .where(PilgrimDataModel.group_name == agency_name, PilgrimDataModel.is_package_assigned == True)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database Error")


async def save_pilgrims_package_finance_info(
        db, tracking_ids, case_total_payable, case_total_due, case_total_available, case_actual_payable, request,
        agency_name
):
    if tracking_ids:
        await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(tracking_ids))
            .values(
                package_name=request.package_name,
                package_duration=request.package_duration,
                package_bed_types=request.package_bed_types,
                add_ons_services=request.add_ons_services,
                updated_by=agency_name,
                is_package_assigned=True,
                total_payable=case_total_payable,
                total_due=case_total_due,
                total_available_amount=case_total_available,
                actual_payable=case_actual_payable,
                package_price_discount=request.package_price_discount
            )
        )

async def save_pilgrim_package_info(
        db, request, pilgrim_with_group_leader_tracking_ids, agency_name
):
    await db.execute(
        update(PilgrimDataModel)
        .where(PilgrimDataModel.tracking_id.in_(pilgrim_with_group_leader_tracking_ids))
        .values(
            package_name=request.package_name,
            package_duration=request.package_duration,
            package_bed_types=request.package_bed_types,
            add_ons_services=request.add_ons_services,
            is_package_assigned=True,
            updated_by=agency_name
        )
    )

async def update_group_leaders_finance(
    db, group_leader_codes, case_total_payable, case_total_due, case_total_available,agency_name
):
    if group_leader_codes:
        await db.execute(
            update(AdminUserModel)
            .where(AdminUserModel.code.in_(group_leader_codes))
            .values(
                total_payable=case_total_payable,
                total_due=case_total_due,
                total_available_amount=case_total_available,
                updated_by=agency_name,
            )
        )


async def insert_bulk_payments(db, pilgrim_payments_data, group_leader_payments_data):
    if pilgrim_payments_data:
        await db.execute(insert(PaymentModel).values(pilgrim_payments_data))
    if group_leader_payments_data:
        await db.execute(insert(PaymentModel).values(group_leader_payments_data))

async def individual_pilgrim_package_change(db: AsyncSession, pilgrim_package_and_finance_update : dict):
    try:
        await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == pilgrim_package_and_finance_update.get("tracking_id"))
            .values(**pilgrim_package_and_finance_update)
        )
    except Exception as e:
        raise e

async def commit_transaction(db):
    await db.commit()