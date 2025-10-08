from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from data.model.admin_user_model import AdminUserModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.admin_user_schema import AdminUserCreate
from infrastructure.schema.pilgrim_data_schema import PilgrimMinimalResponseSchema, \
    PilgrimResponseForAdminUser


async def get_all(db: AsyncSession, agency_name: str):
    try:
        stmt = select(AdminUserModel).where(AdminUserModel.agency_name == agency_name)
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def get_by_id(db: AsyncSession, user_id: int, agency_name: str):
    stmt = select(AdminUserModel).where(
        and_(
            AdminUserModel.id == user_id,
            AdminUserModel.agency_name == agency_name
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_by_mobile_passport(db: AsyncSession, userdata: AdminUserCreate):
    if userdata.passport_no:
        stmt = select(AdminUserModel).where(
            or_(
                AdminUserModel.mobile_no == userdata.mobile_no,
                AdminUserModel.passport_no == userdata.passport_no
            )
        )
    else:
        stmt = select(AdminUserModel).where(AdminUserModel.mobile_no == userdata.mobile_no)

    result = await db.execute(stmt)
    return result.scalars().first()


async def create_admin_user(db: AsyncSession, admin_user: AdminUserCreate, agency_name: str, code: str):
    try:
        user_data = admin_user.model_dump()
        user_data['agency_name'] = agency_name
        user_data["code"] = code
        new_user = AdminUserModel(**user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_admin_user_by_code(db: AsyncSession, code: str):
    try:
        result = await db.execute(
            select(AdminUserModel).where(AdminUserModel.code == code)
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            raise HTTPException(status_code=400, detail=f"Admin User with code {code} not found.")

        return admin_user
    except HTTPException as e:
        raise e

    except SQLAlchemyError as e:
        raise e


async def get_pilgrim_by_admin_user(db: AsyncSession, code: str):
    try:
        stmt = (
            select(PilgrimDataModel)
            .options(
                load_only(
                    PilgrimDataModel.id,
                    PilgrimDataModel.name_en,
                    PilgrimDataModel.name_bn,
                    PilgrimDataModel.passport_no,
                    PilgrimDataModel.mobile_no,
                    PilgrimDataModel.registration_status,
                    PilgrimDataModel.group_name,
                    PilgrimDataModel.total_payable,
                    PilgrimDataModel.total_payment,
                    PilgrimDataModel.group_leader,
                    PilgrimDataModel.group_name
                )
            )
            .where(PilgrimDataModel.group_leader == code)
        )

        result = await db.execute(stmt)
        pilgrims = result.scalars().all()

        stmt = (
            select(AdminUserModel)
            .options(
                load_only(
                    AdminUserModel.id,
                    AdminUserModel.total_due,
                    AdminUserModel.total_payment,
                    AdminUserModel.total_payable,
                    AdminUserModel.code
                )
            )
            .where(AdminUserModel.code == code)
        )

        admin_user_result = await db.execute(stmt)
        admin_user = admin_user_result.scalars().one_or_none()

        pilgrim_list = [PilgrimMinimalResponseSchema.model_validate(p) for p in pilgrims]
        total_payable_sum = sum(p.total_payable or 0 for p in pilgrim_list)

        # Wrap in the response schema
        response = PilgrimResponseForAdminUser(
            pilgrims=pilgrim_list,
            total=len(pilgrim_list),
            total_payable_sum = total_payable_sum,
            total_due = admin_user.total_due,
            total_payment = admin_user.total_payment
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
