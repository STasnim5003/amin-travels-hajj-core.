from logging import setLoggerClass
import logging

from fastapi import HTTPException
from sqlalchemy import insert, select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.model.package_model import PackageModel
from data.model.user_model import UserModel
from infrastructure.schema.package_schema import PackageResponseSchema
from infrastructure.schema.user_schema import UserBaseSchema, UserResponseSchema, UsersResponseSchema


async def insert_user(user: UserBaseSchema, db: AsyncSession) -> UserResponseSchema:
    user.username = str(user.whats_app_no)
    user_data = user.model_dump(exclude_unset=True, exclude_none=True)
    query = insert(UserModel).values(**user_data).returning(UserModel)
    try:
        result = await db.execute(query)
        await db.commit()

        row = result.fetchone()
        if row is None:
            raise ValueError("User insertion failed. No row returned.")

        user_model_instance = row._mapping['UserModel']
        return UserResponseSchema.model_validate(user_model_instance.__dict__)

    except Exception as e:
        await db.rollback()
        logging.error("Error : ", str(e))
        raise

async def get_users(db: AsyncSession, name: str = None, whats_app_no: str = None, search: str = None, page:int=0, limit: int=10, ):
    try:
        query = select(UserModel, PackageModel).join(PackageModel).where(PackageModel.id == UserModel.package_id)
        offset = (page-1)*limit
        if name:
            query = query.where(UserModel.name == name)

        if whats_app_no:
            query = query.where(UserModel.whats_app_no == whats_app_no)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    UserModel.name.ilike(search_term),
                    UserModel.whats_app_no.ilike(search_term)
                )
            )
        query = query.order_by(UserModel.updated_at.asc())

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        response = result.all()

        return get_user_response_schema(response,page, limit)
    except Exception as e:
        logging.error("Error : ", str(e))
        raise

def get_user_response_schema(responses, page, limit):
    users_response = []
    for user, package in responses:
        user_schema = UserResponseSchema.model_validate(user)
        user_schema.package = PackageResponseSchema.model_validate(package)
        users_response.append(user_schema)

    return UsersResponseSchema(users=users_response, total=len(responses), page=page,limit=limit)

async def update_user(id: int, payment_status:str, db: AsyncSession):
    # Pick only specific fields to update manually
    db_user = await db.get(UserModel, id)

    if db_user is None:
        return None  # Or raise 404

    update_data = {}

    if payment_status and db_user.payment_status != payment_status:
        update_data["payment_status"] = payment_status
    # if user.name is not None:
    #     update_data["name"] = user.name
    #
    # if user.whats_app_no is not None:
    #     update_data["whats_app_no"] = user.whats_app_no
    #
    # if user.hajj_year is not None:
    #     update_data["hajj_year"] = user.hajj_year

    # Add more fields as needed...

    if not update_data:
        return None  # Nothing to update

    stmt = (
        update(UserModel)
        .where(UserModel.id == id)
        .values(**update_data)
        .execution_options(synchronize_session="fetch")
    )

    await db.execute(stmt)
    await db.commit()

    result = await db.execute(select(UserModel).where(UserModel.id == id))
    result = result.scalar()
    return UserResponseSchema.model_validate(result)


async def create_credentials(password, db):
    # Build the update statement
    stmt = (
        update(UserModel)
        .values(password=password)
        .execution_options(synchronize_session="fetch")
    )

    # Execute the update
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}


async def get_user_by_username(username, db):
    stmt = select(UserModel).where(UserModel.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def update_user_password(id, username, old_password, new_password, db):
    stmt = (
        update(UserModel)
        .where(UserModel.id == id)
        .values(password=new_password)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}


async def get_user_by_id(id, db):
    stmt = select(UserModel).where(UserModel.id == id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def update_user_registration(id, user_update, db: AsyncSession):
    try:
        # Fetch the user
        user = await db.get(UserModel, id)

        if not user:
            return {"status": "not_found", "message": "No user found with the given ID"}

        updated_fields = []

        # Handle passport_images with proper serialization
        if user_update.passport_images is not None:
            # Convert FileUploadResponseSchema objects to dictionaries
            if isinstance(user_update.passport_images, list):
                passport_images_data = [
                    img.dict() if hasattr(img, 'dict') else img
                    for img in user_update.passport_images
                ]
            else:
                passport_images_data = user_update.passport_images.dict() if hasattr(user_update.passport_images,
                                                                                     'dict') else user_update.passport_images

            user.passport_images = passport_images_data
            updated_fields.append("passport_images")

        if user_update.vaccine_center is not None:
            user.vaccine_center = user_update.vaccine_center
            updated_fields.append("vaccine_center")
        if user_update.registration_status is not None:
            user.registration_status = user_update.registration_status
            updated_fields.append("registration_status")
        if user_update.role is not None:
            user.role = user_update.role
            updated_fields.append("role")

        if updated_fields:
            await db.commit()
            return {
                "status": "success",
                "updated_fields": updated_fields,
                "user_id": user.id
            }
        else:
            return {"status": "no_changes"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))