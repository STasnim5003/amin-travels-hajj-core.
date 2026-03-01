import random
import string
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import case, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.get_current_time import get_current_time
from data.model.pilgrim_data_model import PilgrimDataModel
from data.repository import package_assign_repository, pilgrim_repository, pilgrim_payment_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema
from infrastructure.schema.pilgrim_data_schema import PilgrimDataResponseSchema


async def get_all_package_names(db: AsyncSession, agency_name: str):
    return await package_assign_repository.get_all_package_names(db, agency_name)


async def get_durations_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_durations_by_package_name(db, package_name, agency_name)


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, duration: int, agency_name: str):
    return await package_assign_repository.get_bed_types_by_package_name(db, package_name, duration, agency_name)

async def update_assigned_package(db: AsyncSession, request: PackageAssignUpdateSchema, agency_name: str):
    try:
        if request.total_payable <= 0 or request.package_price_discount < 0:
            raise HTTPException(status_code=400, detail="Payment Amount Must be Positive")

        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, request.tracking_id)
        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim not found")
        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="This pilgrim not in your agency")
        if not pilgrim.is_package_assigned:
            raise HTTPException(status_code=400, detail="This pilgrim is not previously assigned")

        total_payable = request.total_payable
        total_payment = pilgrim.total_payment
        discount = request.package_price_discount

        request_dict = request.model_dump(exclude_unset=True)
        request_dict['total_available_amount'] = max(0, total_payment - (total_payable - discount))
        request_dict['total_due'] = max(0, total_payable - discount - total_payment)
        request_dict['actual_payable'] = total_payable - discount
        request_dict['updated_by'] = agency_name
        request_dict['updated_at'] = get_current_time()

        await package_assign_repository.individual_pilgrim_package_change(db, request_dict)

        # payment table er row
        pilgrim_payable_info = {
            "description": "Updated Package Bill",
            "date": datetime.today().strftime("%Y-%m-%d"),
            "amount": request.total_payable - (request.package_price_discount or 0),
            "tracking_id": request.tracking_id,
            "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            "updated_by": agency_name,
            "updated_at": get_current_time()
        }
        await pilgrim_payment_repository.create_payable_for_package_change(db, pilgrim_payable_info)

        await db.commit()
        return {"message": "package updated successfully"}

    except Exception as e:
        await db.rollback()
        raise e


async def get_package_assigned_pilgrims(db: AsyncSession, agency_name: str):
    try:
        result = await package_assign_repository.get_package_assigned_pilgrims(db, agency_name)
        return [PilgrimDataResponseSchema.model_validate(r) for r in result]
    except Exception as e:
        raise e


async def assign_package_for_multiple_pilgrims(db: AsyncSession, request: PackageAssignForMultiplePilgrimSchema,
                                               agency_name: str):
    try:
        pilgrims = await pilgrim_repository.get_pilgrims_by_tracking_ids(db, request.tracking_ids)

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found for the given tracking IDs")

        for pilgrim in pilgrims:
            if pilgrim.group_name != agency_name:
                raise HTTPException(status_code=403, detail=f"Agency name mismatched for {pilgrim.tracking_id}")

        extra_payable = request.total_payable or 0
        discount = request.package_price_discount or 0

        case_total_payable_for_pilgrims = case(
            *(
                (
                    PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                    pilgrim.total_payable + extra_payable,
                )
                for pilgrim in pilgrims
            ),
            else_=PilgrimDataModel.total_payable,
        )

        case_actual_payable_for_pilgrims = case(
            *(
                (
                    PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                    pilgrim.actual_payable + extra_payable - discount,
                )
                for pilgrim in pilgrims
            ),
            else_=PilgrimDataModel.actual_payable,
        )

        case_total_due_for_pilgrims = case(
            *(
                (
                    PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                    func.greatest(
                        0,
                        (pilgrim.actual_payable + extra_payable - discount)
                        - (pilgrim.total_payment or 0),
                    ),
                )
                for pilgrim in pilgrims
            ),
            else_=PilgrimDataModel.total_due,
        )

        case_total_available_for_pilgrims = case(
            *(
                (
                    PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                    func.greatest(
                        0,
                        (pilgrim.total_payment or 0)
                        - (pilgrim.actual_payable + extra_payable - discount),
                    ),
                )
                for pilgrim in pilgrims
            ),
            else_=PilgrimDataModel.total_available_amount,
        )

        pilgrim_payments_data = [
            {
                "description": "Package Bill",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": request.total_payable - (request.package_price_discount or 0),
                "tracking_id": tracking_id,
                "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "created_by": agency_name,
                "updated_by": agency_name,
                "category": "Payable"
            }
            for tracking_id in request.tracking_ids
        ]

        await package_assign_repository.save_pilgrims_package_finance_info(
            db, request.tracking_ids,
            case_total_payable_for_pilgrims, case_total_due_for_pilgrims, case_total_available_for_pilgrims,
            case_actual_payable_for_pilgrims, request, agency_name
        )

        await package_assign_repository.insert_bulk_payments(db, pilgrim_payments_data, None)

        await package_assign_repository.commit_transaction(db)
        return {"message": "Package assigned and billing updated successfully"}

    except Exception as e:
        raise e


async def change_assigned_package(db: AsyncSession, request: PackageAssignSchema, agency_name: str):
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, request.tracking_id)
        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim Not Found")
        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim Agency Name Mismatch")

        total_payment = pilgrim.total_payment or 0
        total_payable = request.total_payable
        package_price_discount = request.package_price_discount or 0

        total_due = max(total_payable - package_price_discount - total_payment, 0)
        total_available_amount = max(total_payment - (total_payable - package_price_discount), 0)
        total_actual_payable = total_payable - package_price_discount

        # pilgrim package and finance info update
        pilgrim_package_and_finance_update = {
            "total_payable": total_payable,
            "total_due": total_due,
            "total_available_amount": total_available_amount,
            "actual_payable": total_actual_payable,
            "package_price_discount": package_price_discount,
            "package_name": request.package_name,
            "package_duration": request.package_duration,
            "package_bed_types": request.package_bed_types,
            "tracking_id": request.tracking_id,
            "add_ons_services": request.add_ons_services,
            "updated_by": agency_name,
            "updated_at": get_current_time()
        }

        await package_assign_repository.individual_pilgrim_package_change(db, pilgrim_package_and_finance_update)

        # payment table er row
        pilgrim_payable_info = {
            "description": "Updated Package Bill",
            "date": datetime.today().strftime("%Y-%m-%d"),
            "amount": request.total_payable - (request.package_price_discount or 0),
            "tracking_id": request.tracking_id,
            "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            "updated_by": agency_name,
            "updated_at": get_current_time()
        }
        await pilgrim_payment_repository.create_payable_for_package_change(db, pilgrim_payable_info)

        await db.commit()
        return {"message": "package changed successfully"}

    except Exception as e:
        await db.rollback()
        raise e
