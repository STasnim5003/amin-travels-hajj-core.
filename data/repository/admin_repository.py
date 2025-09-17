from http.client import HTTPException

from sqlalchemy import insert, select, or_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema


async def insert_admin(admin: AdminBaseSchema, db: AsyncSession) -> AdminResponseSchema:
    stmt = select(AdminModel).where(
        or_(
            AdminModel.mobile_no == admin.mobile_no,
            AdminModel.agency_name == admin.agency_name,
            AdminModel.user_name == admin.user_name,
        )
    )
    existing_user = await db.execute(stmt)
    existing_user_row = existing_user.fetchone()

    if existing_user_row is not None:
        raise HTTPException(status_code=400, detail="User Already Exists")

    user_data = admin.model_dump(exclude_unset=True, exclude_none=True)
    query = insert(AdminModel).values(**user_data).returning(AdminModel)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=400, detail="Admin insertion failed. No row returned.")

        admin_model_instance = row._mapping['AdminModel']
        return AdminResponseSchema.model_validate(admin_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error Occur!")


# async def get_admin_by_username(db: AsyncSession, username: str):
#     stmt = select(AdminModel).where(AdminModel.user_name == username)
#     result = await db.execute(stmt)
#     admin = result.scalar_one_or_none()
#     return admin


async def get_all_admin(db: AsyncSession, offset: int, limit: int):
    try:
        total_query = await db.execute(
            select(func.count()).select_from(AdminModel).where(AdminModel.user_name != "super_admin")
        )
        total = total_query.scalar()

        result = await db.execute(
            select(AdminModel)
            .where(AdminModel.user_name != "super_admin")
            .offset(offset)
            .limit(limit)
            .order_by(AdminModel.created_at.desc())  # Optional: order by created date
        )
        admins = result.scalars().all()

        return admins, total


    except SQLAlchemyError:
        raise HTTPException(status_code=500,detail="Database error occurred while fetching admin records.")

    except Exception:raise HTTPException(status_code=500,detail="Unexpected error occurred while accessing the admin repository.")

async def get_admin_by_id(db: AsyncSession,admin_id : int):
    try:
        result = await db.execute(
            select(AdminModel).where(AdminModel.id == admin_id)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(
                status_code=404,
                detail=f"Admin with id {id} not found."
            )

        return admin

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving admin by ID."
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while fetching admin by ID."
        )

async def get_admin_by_username(db: AsyncSession, username : str):
    try:
        result = await db.execute(
            select(AdminModel).where(AdminModel.user_name == username)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(
                status_code=404,
                detail=f"Admin with id {id} not found."
            )

        return admin

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving admin by ID."
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while fetching admin by ID."
        )