import random
import string
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import case, func
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from data.model.pilgrim_data_model import PilgrimDataModel
from data.repository import package_assign_repository, pilgrim_repository, package_repository, payment_repository, \
    pilgrim_payment_repository, admin_user_repository
from infrastructure.schema.package_assign_schema import PackageAssignSchema, PackageAssignUpdateSchema, \
    PackageAssignForMultiplePilgrimSchema
from infrastructure.schema.payment_schema import PaymentSchema
from infrastructure.schema.pilgrim_data_schema import PaginatedPilgrimDataListResponseSchema, PilgrimDataResponseSchema


async def get_all_package_names(db: AsyncSession, agency_name: str):
    return await package_assign_repository.get_all_package_names(db, agency_name)


async def get_durations_by_package_name(db: AsyncSession, package_name: str, agency_name: str):
    return await package_assign_repository.get_durations_by_package_name(db, package_name, agency_name)


async def get_bed_types_by_package_name(db: AsyncSession, package_name: str, duration:int, agency_name: str):
    return await package_assign_repository.get_bed_types_by_package_name(db, package_name, duration, agency_name)


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
        result =  await package_assign_repository.get_package_assigned_pilgrims(db, agency_name)
        return [PilgrimDataResponseSchema.model_validate(r) for r in result]
    except Exception as e:
        raise e


async def assign_package_for_multiple_pilgrims(db: AsyncSession, request: PackageAssignForMultiplePilgrimSchema,
                                               agency_name: str):
    try:
        pilgrims = await pilgrim_repository.get_pilgrims_by_tracking_ids(db, request.tracking_ids)

        if not pilgrims:
            raise HTTPException(status_code=400, detail="No pilgrims found for the given tracking IDs")

        group_leader_payment = {}
        pilgrim_without_group_leader = []
        pilgrim_without_group_leader_tracking_ids = []
        pilgrim_with_group_leader_tracking_ids = []
        group_leader_codes = []

        for pilgrim in pilgrims:
            if pilgrim.group_name != agency_name:
                raise HTTPException(status_code=403, detail=f"Agency name mismatched for {pilgrim.tracking_id}")

            if not pilgrim.group_leader:
                pilgrim_without_group_leader.append(pilgrim)
                pilgrim_without_group_leader_tracking_ids.append(pilgrim.tracking_id)
                continue

            # Calculate Group Leader Payable
            group_leader_payment[pilgrim.group_leader] = (
                    group_leader_payment.get(pilgrim.group_leader, 0) + request.total_payable - request.package_price_discount
            )

            pilgrim_without_group_leader.append(pilgrim)
            group_leader_codes.append(pilgrim.group_leader)
            pilgrim_with_group_leader_tracking_ids.append(pilgrim.tracking_id)

        case_total_payable_for_group_leader = case(
            *[
                (
                    (AdminUserModel.code == group_leader),
                    AdminUserModel.total_payable + payable
                )
                for group_leader, payable in group_leader_payment.items()
            ],
            else_=AdminUserModel.total_payable
        )

        case_total_due_for_group_leader = case(
            *[
                (
                    (AdminUserModel.code == group_leader),
                    func.greatest(
                        0,
                        (AdminUserModel.total_payable + payable) - AdminUserModel.total_payment
                    )
                )
                for group_leader, payable in group_leader_payment.items()
            ],
            else_=AdminUserModel.total_due
        )

        case_total_available_amount_for_group_leader = case(
            *[
                (
                    (AdminUserModel.code == group_leader),
                    func.greatest(
                        0,
                        AdminUserModel.total_payment - (AdminUserModel.total_payable + payable)
                    )
                )
                for group_leader, payable in group_leader_payment.items()
            ],
            else_=AdminUserModel.total_available_amount
        )

        case_total_payable_for_pilgrims = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                pilgrim.total_payable + (request.total_payable or 0)
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_payable
        )

        case_total_due_for_pilgrims = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (pilgrim.total_payable + (request.total_payable or 0)) - (pilgrim.total_payment or 0))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_due
        )

        case_total_available_for_pilgrims = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                max(0, (pilgrim.total_payment or 0) - (pilgrim.total_payable + (request.total_payable or 0)))
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_available_amount
        )

        case_actual_payable_for_pilgrims = case(
            *((
                PilgrimDataModel.tracking_id == pilgrim.tracking_id,
                (pilgrim.total_payable + (request.total_payable or 0) - request.package_price_discount)
            ) for pilgrim in pilgrims),
            else_=PilgrimDataModel.total_payable
        )

        pilgrim_payments_data = [
            {
                "description": "Package Assignment Bill",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": request.total_payable,
                "tracking_id": tracking_id,
                "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "created_by": agency_name,
                "updated_by": agency_name,
                "category" : "Payable"
            }
            for tracking_id in pilgrim_without_group_leader_tracking_ids
        ]

        group_leader_payments_data = [
            {
                "description": "Package Assignment Bill",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": payable,
                "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "created_by": agency_name,
                "updated_by": agency_name,
                "pilgrims_tracking_id": pilgrim_with_group_leader_tracking_ids,
                "no_of_hajji": len(pilgrim_with_group_leader_tracking_ids),
                "group_leader": group_leader,
                "category": "Payable"
            }
            for group_leader, payable in group_leader_payment.items()
        ]

        # It will update the package info of pilgrim only not finance
        # if pilgrim_with_group_leader_tracking_ids:
        #     await package_assign_repository.save_pilgrim_package_info(db, request, pilgrim_with_group_leader_tracking_ids, agency_name)

        await package_assign_repository.save_pilgrims_package_finance_info(
            db, request.tracking_ids,
            case_total_payable_for_pilgrims, case_total_due_for_pilgrims, case_total_available_for_pilgrims,
            case_actual_payable_for_pilgrims, request, agency_name
        )

        await package_assign_repository.update_group_leaders_finance(
            db, group_leader_codes, case_total_payable_for_group_leader,
            case_total_due_for_group_leader, case_total_available_amount_for_group_leader, agency_name
        )

        await package_assign_repository.insert_bulk_payments(db, pilgrim_payments_data, group_leader_payments_data)

        await package_assign_repository.commit_transaction(db)
        return {"message": "Package assigned and billing updated successfully"}

    except Exception as e:
        raise e

async def change_assigned_package(db: AsyncSession, request: PackageAssignSchema, agency_name : str):
    try:
        pilgrim = await pilgrim_repository.get_pilgrim_by_tracking_id(db, request.tracking_id)
        if not pilgrim:
            raise HTTPException(status_code=400, detail="Pilgrim Not Found")
        if pilgrim.group_name != agency_name:
            raise HTTPException(status_code=400, detail="Pilgrim Agency Name Mismatch")

        pilgrim_existing_package_name = pilgrim.package_name
        pilgrim_existing_package_duration = pilgrim.package_duration
        pilgrim_existing_package_bed_types = pilgrim.package_bed_types

        package_info = await package_repository.get_package_by_name_and_duration(db=db,
                                                                                 package_name=pilgrim_existing_package_name,
                                                                                 duration=pilgrim_existing_package_duration,
                                                                                 agency_name=agency_name)
        package_info_bed_types = package_info.bed_type
        package_price_based_on_bed_types = package_info_bed_types.get(pilgrim_existing_package_bed_types)

        if isinstance(package_price_based_on_bed_types, str):
            package_price_based_on_bed_types = int(package_price_based_on_bed_types)

        # pilgrim finance info calculate
        total_payable = pilgrim.total_payable or 0
        total_payment = pilgrim.total_payment or 0

        # remove previous package price
        total_payable = total_payable - package_price_based_on_bed_types + request.total_payable
        total_due = max(total_payable - total_payment, 0)
        total_available_amount = max(total_payment - total_payable, 0)
        package_price_discount = request.package_price_discount or 0
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
            "updated_by": agency_name
        }

        await package_assign_repository.individual_pilgrim_package_change(db, pilgrim_package_and_finance_update)

        if not pilgrim.group_leader:
            # payment table er row
            pilgrim_payable_info = {
                "description": "Package Change Bill",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": request.total_payable,
                "tracking_id": request.tracking_id,
                "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "created_by": agency_name,
                "updated_by": agency_name,
                "category" : "Payable"
            }
            await pilgrim_payment_repository.create_payable_for_package_change(db, pilgrim_payable_info)


        else:

            #group leader finance info calculate
            group_leader = await admin_user_repository.get_admin_user_by_code(db, pilgrim.group_leader)
            total_payable_of_group_leader = group_leader.total_payable
            total_payment_of_group_leader = group_leader.total_payment

            total_payable_of_group_leader = total_payable_of_group_leader - package_price_based_on_bed_types + total_actual_payable
            total_due_of_group_leader = max(total_payable_of_group_leader - total_payment_of_group_leader, 0)
            total_available_of_group_leader = max(total_payment_of_group_leader - total_payable_of_group_leader, 0)

            group_leader_finance_info = {
                "total_payable" : total_payable_of_group_leader,
                "total_payment" : total_payment_of_group_leader,
                "total_due" : total_due_of_group_leader,
                "total_available_amount" : total_available_of_group_leader,
                "code" : group_leader.code
            }
            await pilgrim_payment_repository.update_group_leader_payment_info(db, group_leader_finance_info)


            # payment table er row
            group_leader_payable_info = {
                "description": "Package Change Bill",
                "date": datetime.today().strftime("%Y-%m-%d"),
                "amount": request.total_payable,
                "group_leader" : group_leader.code,
                "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "created_by": agency_name,
                "updated_by": agency_name,
                "category": "Payable",
                "pilgrims_tracking_id": [request.tracking_id],
                "no_of_hajji" : 1
            }
            await pilgrim_payment_repository.create_payable_for_package_change(db, group_leader_payable_info)

        await db.commit()
        return {"message": "package changed successfully"}

    except Exception as e:
        await db.rollback()
        raise e


