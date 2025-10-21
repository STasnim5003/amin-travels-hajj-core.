from typing import List

import fastapi

from fastapi import Depends, HTTPException, File, UploadFile, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.core.middleware.middleware import get_current_user
from app.service import user_service
from data.db.db_config import get_async_db
from infrastructure.schema.user_schema import UserResponseSchema, UserBaseSchema, UsersResponseSchema, \
    UpdateUserRequestSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


from fastapi import Form
from pydantic import parse_obj_as
import json

@router.post("/users", response_model=UserResponseSchema, tags=["users"])
async def create_user_endpoint(
    user: str = Form(...),  # Accept as string
    nid: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        # Parse the stringified JSON into a Pydantic model
        user_dict = json.loads(user)
        user_obj = UserBaseSchema(**user_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user JSON: {e}")

    response = await user_service.create_user(user_request_schema=user_obj, nid=nid, db=db)
    return JSONResponse(content=jsonable_encoder(response))


# @router.post("/users", response_model=UserResponseSchema, tags=["users"])
# async def create_user_endpoint(
#         user: UserBaseSchema,
#         db: AsyncSession = Depends(get_async_db),
#         nid: List[UploadFile] = File(...),
# ):
#     response = await user_service.create_user(user_request_schema=user,nid=nid, db=db)
#     return JSONResponse(content=jsonable_encoder(response))



@private_router.get("/users", response_model=UsersResponseSchema, tags=["users"])
async def get_users_endpoint(
        name:str =None,
        whats_app_no: str=None,
        search: str=None,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN" and current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    response = await user_service.get_users(name=name, whats_app_no=whats_app_no, search=search,page=page, limit=limit, db=db)
    return JSONResponse(content=jsonable_encoder(response))


@private_router.put("/users/{id}", response_model=UserResponseSchema, tags=["users"])
async def update_user_status(
        id: int,
        payment_status: str ,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "ADMIN" and current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    response = await user_service.update_user(id=id, payment_status=payment_status, db=db)
    return JSONResponse(content=jsonable_encoder(response))

# @private_router.put("/users", tags=["users"])
# async def create_user_credentials(
#     password: str = Form(...),
#     db: AsyncSession = Depends(get_async_db),
# ):
#     response = await user_service.create_credentials(password=password, db=db)
#     return JSONResponse(content=jsonable_encoder(response))

@router.post("/users/login", response_model=UserResponseSchema, tags=["users"])
async def create_user_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    response = await user_service.user_login(request_credential=form_data, db=db)
    return JSONResponse(content=jsonable_encoder(response))


@router.post("/users/refresh", response_model=dict, tags=["users"])
async def get_access_token_using_refresh(
        refresh_token: str = Form(...),
        db: AsyncSession = Depends(get_async_db)
):
    response = await user_service.fetch_access_token_using_refresh_token(refresh_token=refresh_token)
    return JSONResponse(content=jsonable_encoder(response))


@private_router.put("/users/{id}/reset-password", response_model=UserResponseSchema, tags=["users"])
async def update_user_password(
        id: int,
        username: str = Form(...),
        old_password: str = Form(...),
        new_password: str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    response = await user_service.update_user_password(id=id, username=username, old_password=old_password, new_password=new_password, db=db, current_user=current_user)
    return JSONResponse(content=jsonable_encoder(response))

@private_router.put("/users/{id}/register",  tags=["users"])
async def update_user_registration(
        id: int,
        user_update: str = Form(...),
        passport: List[UploadFile] = File(...),
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
):
    user_dict = json.loads(user_update)
    user_obj = UpdateUserRequestSchema(**user_dict)
    response = await user_service.update_user_registration(id=id, user_update=user_obj, passport=passport, db=db, current_user=current_user)
    return JSONResponse(content=jsonable_encoder(response))




