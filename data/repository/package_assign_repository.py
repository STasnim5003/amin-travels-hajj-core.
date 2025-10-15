from datetime import datetime
from pydoc import describe

from fastapi import HTTPException
from sqlalchemy import select, update, case, insert
from sqlalchemy.ext.asyncio import AsyncSession

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

async def assign_package_for_multiple_pilgrim(db:AsyncSession, request:PackageAssignForMultiplePilgrimSchema, agency_name:str):
    try:

        # Find each pilgrim and associated agency name
        pilgrims_result = await db.execute(
            select(PilgrimDataModel).where(PilgrimDataModel.tracking_id.in_(request.tracking_ids))
        )
        pilgrims = pilgrims_result.scalars().all()

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found for the given tracking IDs")

        for pilgrim in pilgrims:
            if pilgrim.group_name != agency_name:
                raise HTTPException(status_code=403, detail=f"Agency name mismatched for {pilgrim.tracking_id}")

        case_total_payable = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                pilgrim.total_payable + (request.total_payable or 0)
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_payable
        )

        case_total_due = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (pilgrim.total_payable + (request.total_payable or 0)) - (pilgrim.total_payment or 0))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_due
        )

        case_total_available = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (pilgrim.total_payment or 0) - (pilgrim.total_payable + (request.total_payable or 0)))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_available_amount
        )

        case_actual_payable = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                (pilgrim.total_payable + (request.total_payable or 0) - request.package_price_discount)
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_payable
        )
        await db.execute(
            update(PilgrimDataModel)
            .where(PilgrimDataModel.tracking_id.in_(request.tracking_ids))
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
                package_price_discount= request.package_price_discount
            )
        )

        payments_data = [
            {
                "description": "Package Assignment",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": request.total_payable,
                "tracking_id": tracking_id,
                "created_by": agency_name,
                "updated_by": agency_name,
            }
            for tracking_id in request.tracking_ids
        ]

        # Bulk insert
        stmt = insert(PaymentModel).values(payments_data)
        await db.execute(stmt)

        await db.commit()
        return {"message" : "Package assigned and billing updated successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error in package assignment")




