import logging

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema


async def insert_admin(admin: AdminBaseSchema, db: AsyncSession) -> AdminResponseSchema:
    stmt = select(AdminModel).where(AdminModel.user_name == admin.user_name)
    existing_user = await db.execute(stmt)
    existing_user_row = existing_user.fetchone()

    if existing_user_row is not None:
        raise ValueError("User already exists")

    user_data = admin.model_dump(exclude_unset=True, exclude_none=True)
    query = insert(AdminModel).values(**user_data).returning(AdminModel)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise ValueError("Admin insertion failed. No row returned.")

        admin_model_instance = row._mapping['AdminModel']
        return AdminResponseSchema.model_validate(admin_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise
