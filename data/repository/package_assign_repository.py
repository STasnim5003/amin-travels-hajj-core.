from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, update, insert, delete, func
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
    return durations


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, duration:int, agency_name: str):
    stmt = (
        select(PackageModel.bed_type)
        .where(
            PackageModel.name == package_name,
            PackageModel.duration == duration,
            PackageModel.package_type == "HAJJ",
            PackageModel.agency_name == agency_name
        )
    )
    result = await db.execute(stmt)
    bed_type_json = result.scalars().first()
    return bed_type_json

async def get_package_assigned_pilgrims(db: AsyncSession, agency_name: str):
    try:
        stmt = (
            select(PilgrimDataModel)
            .where(PilgrimDataModel.group_name == agency_name, PilgrimDataModel.is_package_assigned == True)
            .order_by(PilgrimDataModel.updated_at.desc())
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
                updated_at=func.now(),
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

PACKAGE_BILL_DESCRIPTIONS = ("Package Bill", "Updated Package Bill")


async def get_hajj_package(db: AsyncSession, package_name: str, duration: int, agency_name: str,
                           hajj_year: int | None = None):
    # Prefer the package of the pilgrim's own hajj year; fall back to the latest one with that name.
    stmt = (
        select(PackageModel)
        .where(
            PackageModel.name == package_name,
            PackageModel.duration == duration,
            PackageModel.package_type == "HAJJ",
            PackageModel.agency_name == agency_name
        )
        .order_by((PackageModel.hajj_year == hajj_year).desc().nulls_last(), PackageModel.id.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_payable_summary(db: AsyncSession, tracking_ids: list[str]) -> dict:
    # Per pilgrim: sum of non-package payables, and the amount of the latest package bill row (None if none).
    is_package_bill = PaymentModel.description.in_(PACKAGE_BILL_DESCRIPTIONS)
    result = await db.execute(
        select(PaymentModel.tracking_id, PaymentModel.amount, is_package_bill.label("is_package_bill"))
        .where(PaymentModel.tracking_id.in_(tracking_ids), PaymentModel.category == "Payable")
        .order_by(PaymentModel.id)
    )
    summary = {tid: {"other": 0, "last_package_amount": None} for tid in tracking_ids}
    for tracking_id, amount, package_bill in result.all():
        if package_bill:
            summary[tracking_id]["last_package_amount"] = amount or 0
        else:
            summary[tracking_id]["other"] += amount or 0
    return summary


async def replace_package_bills(db: AsyncSession, tracking_ids: list[str], package_bill_rows: list[dict]):
    # Each pilgrim keeps exactly one package bill row in the ledger.
    await db.execute(
        delete(PaymentModel).where(
            PaymentModel.tracking_id.in_(tracking_ids),
            PaymentModel.category == "Payable",
            PaymentModel.description.in_(PACKAGE_BILL_DESCRIPTIONS),
        )
    )
    if package_bill_rows:
        await db.execute(insert(PaymentModel).values(package_bill_rows))


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