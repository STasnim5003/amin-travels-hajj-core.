from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from infrastructure.schema.admin_user_schema import AdminUserCreate

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



async def create_admin_user(db: AsyncSession, admin_user: AdminUserCreate, agency_name : str, code : str):
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
            raise HTTPException(status_code=404,detail=f"Admin User with code {code} not found.")

        return admin_user
    except HTTPException as e:
         raise e

    except SQLAlchemyError as e:
        raise e

    except Exception as e:
        raise e