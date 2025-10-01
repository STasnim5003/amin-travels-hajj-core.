from typing import Optional

import fastapi
from fastapi import Depends, Form, UploadFile, File, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.service import admin_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_schema import AdminResponseSchema, TokenSchema, AdminListResponseSchema, \
    AdminProfileUpdateResponseSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/admin", response_model=AdminResponseSchema, tags=["admin"])
async def create_admin_endpoint(
        db: AsyncSession = Depends(get_async_db),
        user_name: str = Form(...),
        password: str = Form(...),
        role: str = Form(...),
        agency_name: str = Form(...),
        license_number: str = Form(...),
        mobile_no: str = Form(...),
        email: Optional[str] = Form(...),
        # current_user: dict = Depends(get_current_user)

):
    # if current_user["role"] != "SUPER_ADMIN":
    #     raise HTTPException(status_code=403, detail="Unauthorized")
    try:
        response = await admin_service.create_admin(
            db=db,
            user_name=user_name,
            password=password,
            role=role,
            agency_name=agency_name,
            license_number=license_number,
            mobile_no=mobile_no,
            email=email
        )
        return JSONResponse(content=jsonable_encoder(response))

    except HTTPException as http_exc:
        return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@router.post("/login", summary="Admin login", response_model=TokenSchema, tags=["admin"])
async def create_admin_login_endpoint(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    return await admin_service.admin_login(db, form_data)


@private_router.get("/admin", response_model=AdminListResponseSchema, tags=["admin"])
async def get_all_admins(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        return await admin_service.get_all_admins(db=db, page=page, limit=limit)

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")


@private_router.get("/admin/profile", response_model=AdminResponseSchema, tags=["admin"])
async def get_admin_profile(
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminResponseSchema:
    username = current_user["username"]
    try:
        return await admin_service.get_admin_by_username(db, username)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")


@private_router.get("/admin/{admin_id}", response_model=AdminResponseSchema, tags=["admin"])
async def get_admin_by_id(
        admin_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminResponseSchema:
    if current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        return await admin_service.get_admin_by_id(db, admin_id)
    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")


@private_router.delete("/admin/{admin_id}", response_model=AdminProfileUpdateResponseSchema, tags=["admin"])
async def delete_admin_by_id(
        admin_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminProfileUpdateResponseSchema:
    if current_user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Unauthorized")
    try:
        return await admin_service.delete_admin_by_id(db, admin_id)
    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")

@private_router.put("/admin/profile", response_model=AdminProfileUpdateResponseSchema, tags=["admin"])
async def update_admin_profile(
        location : str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
) -> AdminProfileUpdateResponseSchema: