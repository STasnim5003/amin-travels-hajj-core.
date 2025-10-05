from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_user_model import AdminUserModel
from infrastructure.schema.admin_user_schema import AdminUserCreate

async def get_all(db: AsyncSession):
    try:
        stmt = select(AdminUserModel)  # select all rows
        result = await db.execute(stmt)
        return result.scalars().all()  # returns list of AdminUserModel instances
    except Exception as e:
        await db.rollback()  # rollback just in case
        raise HTTPException(status_code=400, detail=str(e))



async def get_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(AdminUserModel).where(AdminUserModel.id == user_id)
    )
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



async def create_admin_user(db: AsyncSession, admin_user: AdminUserCreate, agency_name : str):
    try:
        user_data = admin_user.model_dump()
        user_data['agency_name'] = agency_name
        new_user = AdminUserModel(**user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))