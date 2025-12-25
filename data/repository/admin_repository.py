from typing import List, Dict, Any

from fastapi import HTTPException
from sqlalchemy import insert, select, or_, func, update, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.admin_model import AdminModel
from data.model.pilgrim_data_model import PilgrimDataModel
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema, AssignLeadAgencySchema


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
        raise HTTPException(status_code=400, detail=str(e))


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
        raise HTTPException(status_code=500, detail="Database error occurred while fetching admin records.")

    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while accessing the admin repository.")


async def get_admin_by_id(db: AsyncSession, admin_id: int):
    try:
        result = await db.execute(
            select(AdminModel).where(AdminModel.id == admin_id)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(
                status_code=404,
                detail=f"Admin with id {admin_id} not found."
            )

        return admin
    except HTTPException:
        raise

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


async def get_admin_by_username(db: AsyncSession, username: str):
    try:
        result = await db.execute(
            select(AdminModel).where(AdminModel.user_name == username)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(
                status_code=404,
                detail=f"Admin with username {username} not found."
            )

        return admin
    except HTTPException as e:
        raise e

    except SQLAlchemyError as e:
        raise e

    except Exception as e:
        raise e


async def delete_admin_by_id(db: AsyncSession, admin_id: int):
    try:

        result = await db.execute(
            select(AdminModel).where(AdminModel.id == admin_id)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=404, detail=f"Admin with id {admin_id} does not exist.")

        if admin.user_name == "super_admin":
            raise HTTPException(status_code=403, detail="Cannot delete the super_admin account.")

        await db.delete(admin)
        await db.commit()

        return {"message": f"Admin with id {admin_id} deleted successfully."}

    except HTTPException:
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred while deleting the admin.")

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting the admin.")


async def update_admin_profile(
        db: AsyncSession,
        location: str,
        google_map_location: str,
        logo: List[Dict[str, Any]],
        passport_copy: List[Dict[str, Any]],
        agency_name: str
):
    stmt = select(AdminModel).where(AdminModel.agency_name == agency_name)
    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    stmt = (
        update(AdminModel)
        .where(AdminModel.agency_name == agency_name)
        .values(
            location=location,
            google_map_location=google_map_location,
            logo=logo,
            passport_copy=passport_copy,
        )
        .returning(AdminModel)
    )

    result = await db.execute(stmt)
    await db.commit()
    updated_admin = result.scalar_one_or_none()

    if not updated_admin:
        raise HTTPException(status_code=400, detail="Update failed")

    return AdminResponseSchema.model_validate(updated_admin)


async def get_agency_by_agency_name(db: AsyncSession, agency_name: str):
    try:
        result = await db.execute(
            select(AdminModel).where(AdminModel.agency_name == agency_name)
        )

        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def assign_lead_agency(db: AsyncSession, request: dict):
    try:
        await db.execute(
            update(AdminModel)
            .where(AdminModel.agency_name == request['agency_name'])
            .values(lead_agency = request['lead_agency_name'])
        )

        await db.commit()

        return True
    except Exception as e:
        raise e

# TODO: more fields will be added in pilgrim data and also change here
async def get_lead_agency_pilgrims(db, lead_agency_name):
    try:
        query = text("""
            WITH agencies AS (
                SELECT agency_name
                FROM core.admin
                WHERE lead_agency = :lead_agency_name
            )
            SELECT 
                a.agency_name,
                COALESCE(COUNT(pd.tracking_id), 0) AS total_pilgrims,
                COALESCE(
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'name_en', pd.name_en,
                            'tracking_id', pd.tracking_id,
                            'serial_no', pd.serial_no,
                            'voucher', pd.voucher,
                            'mobile_no', pd.mobile_no,
                            'passport_no', pd.passport_no,
                            'passport_expiry_date', pd.passport_expiry_date,
                            'date_of_birth', pd.date_of_birth,
                            'nid', pd.nid,
                            'gender', pd.gender,
                            'agency_name', pd.group_name,
                            'passport_dob', pd.passport_dob,
                            'passport_type', pd.passport_type
                        )
                    ) FILTER (WHERE pd.tracking_id IS NOT NULL),
                    '[]'
                ) AS pilgrims
            FROM agencies a
            LEFT JOIN core.pilgrim_data pd 
                ON a.agency_name = pd.group_name
            GROUP BY a.agency_name
            ORDER BY a.agency_name;
        """)
        result = await db.execute(query, {"lead_agency_name": lead_agency_name})
        return result.mappings().all()

    except Exception as e:
        raise e


async def check_lead_agency_assignment(db, agency_name):
    try:
        result = await db.execute(
            select(AdminModel.lead_agency)
            .where(AdminModel.agency_name == agency_name)
            .limit(1)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def get_child_agencies(db, lead_agency_name):
    try:
        result = await db.execute(
            select(AdminModel.agency_name)
            .where(AdminModel.lead_agency == lead_agency_name)
        )

        return result.scalars().all()
    except Exception as e:
        raise e

async def get_lead_agency(db:AsyncSession, agency_name:str):
    try:
        result = await db.execute(
            select(AdminModel.lead_agency)
            .where(AdminModel.agency_name == agency_name)
        )

        return result.scalar_one_or_none()
    except Exception as e:
        raise e


async def update_sub_agency_amount(db:AsyncSession, request_schema:dict):
    try:
        result = await db.execute(
            update(AdminModel)
            .values(**request_schema)
            .where(AdminModel.agency_name == request_schema['agency_name'])
            .returning(AdminModel)
        )

        await db.commit()
        return result.scalar_one_or_none()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error Updating Sub Agency Amount")

async def get_agency_by_agency_name(db:AsyncSession, agency_name:str):
    try:
        stmt = (
            select(AdminModel)
            .where(AdminModel.agency_name == agency_name)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        raise e