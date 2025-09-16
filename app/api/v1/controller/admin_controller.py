from typing import Optional

import fastapi
from fastapi import Depends, Form, UploadFile, File, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.service import admin_service
from data.db.db_config import get_async_db
from infrastructure.schema.admin_schema import AdminResponseSchema, TokenSchema

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


@router.post("/admin", response_model=AdminResponseSchema, tags=["admin"])
async def create_admin_endpoint(
        db: AsyncSession = Depends(get_async_db),
        user_name:str = Form(...),
        password: str = Form(...),
        role: str = Form(...),
        agency_name: str = Form(...),
        license_number: str = Form(...),
        mobile_no: str = Form(...),
        location: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        profile_pic: Optional[str] = Form(None),
        logo: Optional[UploadFile] = File(None),
        passport_copy: Optional[UploadFile] = File(None),

):
    # if current_user["role"] != "ADMIN":
    #     raise HTTPException(status_code=403, detail="Not authorized")
    try:
        response = await admin_service.create_admin(
            db=db,
            user_name=user_name,
            password=password,
            role=role,
            agency_name=agency_name,
            license_number=license_number,
            mobile_no=mobile_no,
            location=location,
            email=email,
            logo=logo,
            passport_copy=passport_copy
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
