from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.utils import hash_password, verify_password, create_access_token_for_admin_user, \
    create_refresh_token_for_admin_user
from data.repository import admin_user_repository
from infrastructure.schema.admin_schema import AdminResponseSchema
from infrastructure.schema.admin_user_schema import AdminUserCreate, AdminUserResponse, GroupLeaderAssignSchema


async def list_users(db: AsyncSession, agency_name : str):
    return await admin_user_repository.get_all(db, agency_name)



async def get_user(db: AsyncSession, user_id: int, agency_name : str):
    user = await admin_user_repository.get_by_id(db, user_id, agency_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def create_user(db: AsyncSession, user_data: AdminUserCreate, agency_name:str):
    try:
        hashed_password = hash_password(user_data.password)
        main_password = user_data.password
        user_data.password = hashed_password

        role_code_map = {
            "GROUP_LEADER": "GL",
            "STAFF": "ST",
            "SAUDI_REPRESENTATIVE": "SR"
        }

        code_suffix = role_code_map.get(user_data.role, None)
        code = None
        if code_suffix:
            code = f"{agency_name}_{code_suffix}_{user_data.name.replace(' ', '').upper()}"

        existing_user = await admin_user_repository.get_by_mobile_passport(db, user_data)
        if existing_user:
            raise HTTPException(status_code=404, detail="User already exists")

        user_data_dict = user_data.model_dump(exclude_none=True)
        user_data_dict['agency_name'] = agency_name
        user_data_dict['code'] = code

        guide_data_dict = {}
        if user_data.role == "GUIDE":
            guide_data_dict.update({
                'name_en' : user_data.name,
                'tracking_id': user_data.tracking_id,
                'date_of_birth': user_data.dob,
                'mobile_no': user_data.mobile_no,
                'gender': user_data.gender,
                'nid': user_data.nid,
                'passport_no': user_data.passport_no,
                'group_name': agency_name,
                "total_payment": 0,
                "total_payable": 0,
                "total_due": 0,
                "total_available_amount": 0,
                "package_price_discount": 0,
                "actual_payable": 0,
                "is_package_assigned": False,
                "allocation_status": "ASSIGNED",
                "registration_status": "REGISTERED",
                "preliminary_password": main_password,
                "password": hashed_password,
                "is_assigned": True,
                "created_by": agency_name,
                "updated_by": agency_name,
                'passport_dob': user_data.passport_dob,
                'passport_expiry_date': user_data.passport_expiry_date,
            })
        result = await admin_user_repository.create_admin_user(db, user_data_dict, guide_data_dict)
        return AdminUserResponse.model_validate(result)
    except Exception as e:
        raise e

async def admin_user_login(db: AsyncSession, request_credential: OAuth2PasswordRequestForm):
    user = await admin_user_repository.get_admin_user_by_code(db, code=request_credential.username)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    if not verify_password(request_credential.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    access_token = create_access_token_for_admin_user(
        subject=user.code, role=user.role,
        mobile_no=user.mobile_no, email=user.email,
        code=user.code, agency_name= user.agency_name)
    refresh_token = create_refresh_token_for_admin_user(
        subject=user.code, role=user.role,
        mobile_no=user.mobile_no, email=user.email,
        code=user.code, agency_name= user.agency_name)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

async def get_admin_user_profile(db:AsyncSession, code:str):
    try:
        return await admin_user_repository.get_admin_user_by_code(db, code)
    except Exception as e:
        raise e

async def get_pilgrim_data_by_admin_user(db:AsyncSession, group_leader_code:str):
    try:
        result = await admin_user_repository.get_pilgrim_by_admin_user(db, group_leader_code)
        return result
    except Exception as e:
        raise e

async def assign_group_leader_to_pilgrims(db:AsyncSession, request: GroupLeaderAssignSchema, agency_name : str):
    try:
        return await admin_user_repository.assign_group_leader_to_pilgrims(db, request, agency_name)
    except Exception as e:
        raise e

async def get_group_leader_with_pilgrim_count(db:AsyncSession, agency_name : str):
    try:
        return await admin_user_repository.get_group_leader_with_pilgrim_count(db, agency_name)
    except Exception as e:
        raise e