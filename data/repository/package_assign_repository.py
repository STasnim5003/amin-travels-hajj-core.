from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.package_model import PackageModel
from data.model.pilgrim_data_model import PilgrimDataModel
from data.repository import pilgrim_payment_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema
from infrastructure.schema.payment_schema import PaymentSchema


# TODO : package er sthe agency diye filter korte hobe
async def get_all_package_names(db: AsyncSession, agency_name: str):
    stmt = (
        select(PackageModel.name)
        .where(
            PackageModel.hajj_year == 2026,
            PackageModel.description_type == "DETAILS",
            PackageModel.package_type == "HAJJ",
            # PackageModel.agency_name == agency_name
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
            PackageModel.hajj_year == 2026,
            PackageModel.description_type == "DETAILS",
            PackageModel.package_type == "HAJJ"
            # PackageModel.agency_name == agency_name
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
            PackageModel.hajj_year == 2026,
            PackageModel.description_type == "DETAILS",
            PackageModel.package_type == "HAJJ"
            # PackageModel.agency_name == agency_name
        )
    )
    result = await db.execute(stmt)
    bed_type_json = result.scalars().first()
    if not bed_type_json:
        raise HTTPException(status_code=404, detail=f"No bed types found for {package_name}")
    return bed_type_json

async def assign_package(db:AsyncSession, request:PackageAssignSchema, agency_name:str):
    try:
        async with db.begin():
            pilgrim_result = await db.execute(
                select(PilgrimDataModel).where(PilgrimDataModel.tracking_id == request.tracking_id)
            )
            pilgrim = pilgrim_result.scalar_one_or_none()

            if not pilgrim:
                raise HTTPException(status_code=400, detail="Pilgrim not found")

            if pilgrim.group_name != agency_name:
                raise HTTPException(status_code=403, detail="Agency Name Mismatched")

            total_payable = pilgrim.total_payable + request.total_payable
            total_available_amount = pilgrim.total_available_amount or 0
            total_due = pilgrim.total_due or 0

            if total_payable >= total_available_amount:
                new_available_amount = 0
                new_due = total_payable - total_available_amount
            else:
                new_available_amount = total_available_amount - total_payable
                new_due = 0

            await db.execute(
                update(PilgrimDataModel)
                .where(PilgrimDataModel.tracking_id == request.tracking_id)
                .values(
                    package_name=request.package_name,
                    package_duration=request.package_duration,
                    package_bed_types=request.package_bed_types,
                    add_ons_services=request.add_ons_services,
                    total_payable=total_payable,
                    total_available_amount=new_available_amount,
                    total_due=new_due,
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
                db, payable_schema, agency_name, None
            )

        return {"message" : "Successfully Updated"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_assigned_package(
        db: AsyncSession,
        request_dict: dict,
        payable_create_schema: PaymentSchema,
        agency_name : str
):
    try:
        stmt = (
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id == request_dict["tracking_id"])
            .values(**request_dict)
            .returning(PilgrimDataModel)
        )



        result = await db.execute(stmt)
        await pilgrim_payment_repository.create_payable_for_pilgrim(db, payable_create_schema, agency_name, None)
        await db.commit()
        updated_pilgrim = result.scalar_one_or_none()
        if not updated_pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim not found for update")

        return updated_pilgrim
    except Exception as e:
        raise HTTPException(status_code=400, detail="Database Error")


async def get_package_assigned_pilgrims(db:AsyncSession, agency_name:str):
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
