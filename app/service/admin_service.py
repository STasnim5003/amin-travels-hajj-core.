import json
from typing import Optional

from fastapi import HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.utils.feature_flags import get_agency_features
from app.core.utils.file_downloadable_url import generate_downloadable_urls
from app.core.utils.get_current_time import get_current_time
from app.core.utils.utils import hash_password, verify_password, create_access_token, create_refresh_token
from data.repository import admin_repository, file_repository, admin_user_repository
from infrastructure.schema.admin_schema import AdminBaseSchema, AdminResponseSchema, AdminListResponseSchema, \
    AdminProfileUpdateResponseSchema, SubAgencyAmountUpdateSchema, LogoUpdateSchema, BillingContactSchema, \
    BankAccountSchema, PublicAgencySchema, clean_email, normalize_bank_accounts


async def create_admin(db: AsyncSession,
                       user_name: str,
                       password: str,
                       role: str,
                       agency_name: str,
                       license_number: str,
                       mobile_no: str,
                       email: Optional[str],
                       ) -> AdminResponseSchema:
    hashed_password = hash_password(password)

    new_admin = AdminBaseSchema(
        user_name=user_name,
        password=hashed_password,
        role=role,
        agency_name=agency_name,
        license_number=license_number,
        mobile_no=mobile_no,
        email=email,
        is_active=True,

    )
    try:
        response = await admin_repository.insert_admin(new_admin, db=db)
        return response

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def admin_login(db: AsyncSession, request_credential: OAuth2PasswordRequestForm):
    user = await admin_repository.get_admin_by_username(db, username=request_credential.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    if not verify_password(request_credential.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(subject=user.user_name, role=user.role, agency_name=user.agency_name)
    refresh_token = create_refresh_token(subject=user.user_name, role=user.role, agency_name=user.agency_name)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


async def get_all_admins(db: AsyncSession, page: int, limit: int) -> AdminListResponseSchema:
    offset = (page - 1) * limit
    try:
        admins, total = await admin_repository.get_all_admin(db, offset=offset, limit=limit)
        return AdminListResponseSchema(
            data=admins,
            total=total,
            page=page,
            size=limit
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error occurred while retrieving admin data.")


async def get_admin_by_id(db: AsyncSession, admin_id: int) -> AdminResponseSchema:
    try:
        admin = await admin_repository.get_admin_by_id(db, admin_id=admin_id)
        await sign_admin_files(admin)
        return AdminResponseSchema.model_validate(admin)
    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while fetching the admin.")


async def get_admin_by_username(db: AsyncSession, username: str) -> AdminResponseSchema:
    try:
        admin = await admin_repository.get_admin_by_username(db, username=username)
        await sign_admin_files(admin)

        return AdminResponseSchema.model_validate(admin)
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while fetching the admin.")


async def delete_admin_by_id(db: AsyncSession, admin_id: int) -> AdminProfileUpdateResponseSchema:
    try:
        message = await admin_repository.delete_admin_by_id(db, admin_id=admin_id)
        return AdminProfileUpdateResponseSchema(
            message=message["message"],
            status=204
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting the admin.")


# Profile text fields: a sent key with a blank value clears the column, a missing key leaves it unchanged.
PROFILE_TEXT_FIELDS = ["agency_name_bn", "umrah_license_number", "address", "office_phone", "office_email", "website",
                       "signatory_name", "signatory_designation"]
# Legacy fields keep their old rule (blank = no change), since the frontend may send them blank on every save.
PROFILE_LEGACY_TEXT_FIELDS = ["location", "google_map_location"]
# column -> R2 folder; images reject SVG (it can carry scripts and doesn't render in the PDFs)
PROFILE_FILE_FIELDS = {"logo": "logo", "passport_copy": "passport", "signature": "signature", "seal": "seal"}
IMAGE_FIELDS = {"logo", "signature", "seal"}
CLEARABLE_FILE_FIELDS = {"signature", "seal"}
SIGNED_FILE_FIELDS = ["logo", "passport_copy", "signature", "seal"]


def _validate_image(field: str, file: UploadFile):
    name = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()
    if name.endswith((".svg", ".svgz")) or "svg" in content_type:
        raise HTTPException(status_code=400, detail=f"{field}: SVG images are not allowed")
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"{field}: only image files are allowed")


def _parse_json_field(field: str, raw: str):
    try:
        return json.loads(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"{field} must be valid JSON")


async def sign_admin_files(admin):
    """Swap stored file URLs for presigned ones; works on a dict or a schema object."""
    for field in SIGNED_FILE_FIELDS:
        value = admin.get(field) if isinstance(admin, dict) else getattr(admin, field, None)
        if value:
            signed = await generate_downloadable_urls(value)
            if isinstance(admin, dict):
                admin[field] = signed
            else:
                setattr(admin, field, signed)
    return admin


async def update_admin_profile(db: AsyncSession, form, agency_name: str, username: str):
    values = {}
    try:
        for field in PROFILE_LEGACY_TEXT_FIELDS:
            value = form.get(field)
            if isinstance(value, str) and value.strip():
                values[field] = value.strip()
        for field in PROFILE_TEXT_FIELDS:
            if field in form and isinstance(form.get(field), str):
                values[field] = form.get(field).strip() or None
        if "office_email" in values:
            values["office_email"] = clean_email(values["office_email"])

        if "billing_contact" in form:
            raw = (form.get("billing_contact") or "").strip()
            if raw:
                contact = BillingContactSchema.model_validate(_parse_json_field("billing_contact", raw)).model_dump()
                values["billing_contact"] = contact if any(contact.values()) else None
            else:
                values["billing_contact"] = None

        if "bank_accounts" in form:
            raw = (form.get("bank_accounts") or "").strip()
            parsed = _parse_json_field("bank_accounts", raw) if raw else []
            if not isinstance(parsed, list):
                raise HTTPException(status_code=400, detail="bank_accounts must be a JSON list")
            accounts = [BankAccountSchema.model_validate(item) for item in parsed]
            values["bank_accounts"] = normalize_bank_accounts(accounts) or None
    except (ValueError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    for field, folder in PROFILE_FILE_FIELDS.items():
        if field not in form:
            continue
        file = form.get(field)
        if isinstance(file, str):
            # blank clears signature / seal; logo and passport keep the old rule (blank = keep)
            if not file.strip() and field in CLEARABLE_FILE_FIELDS:
                values[field] = None
            continue
        if field in IMAGE_FIELDS:
            _validate_image(field, file)
        try:
            uploaded = await file_repository.upload_file(file=file, name=folder)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        values[field] = [uploaded.model_dump()]

    values["updated_by"] = username
    values["updated_at"] = get_current_time()
    try:
        response = await admin_repository.update_admin_profile(db, values, agency_name)
        await sign_admin_files(response)
        response.features = get_agency_features(agency_name)
        return response

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_public_agency(db: AsyncSession, agency_name: str) -> Optional[dict]:
    """Issuing-agency block for the public (no-auth) PDF endpoints."""
    admin = await admin_repository.get_agency_by_agency_name(db, agency_name)
    if not admin:
        return None
    agency = PublicAgencySchema.model_validate(admin).model_dump()
    if agency["logo"]:
        agency["logo"] = await generate_downloadable_urls(agency["logo"])
    return agency


async def assign_lead_agency(db: AsyncSession, request: dict):
    try:

        fetched_agency = await admin_repository.get_agency_by_agency_name(db, request['agency_name'])
        lead_agency = await admin_repository.get_agency_by_agency_name(db, request['lead_agency_name'])

        if not fetched_agency or not lead_agency:
            raise HTTPException(status_code=400, detail="Agency Not found")

        result = await admin_repository.assign_lead_agency(db, request)
        if result:
            return {"message": "Lead agency assigned successfully"}
    except Exception as e:
        raise e


async def get_lead_agency_pilgrims(db: AsyncSession, lead_agency_name: str):
    try:
        records = await admin_repository.get_lead_agency_pilgrims(db, lead_agency_name)

        agencies = []
        for row in records:
            agencies.append({
                "agency_name": row["agency_name"],
                "total_pilgrims": row["total_pilgrims"],
                "name_en": None,
                "tracking_id": None,
                "serial_no": None,
                "voucher": None,
                "mobile_no": None,
                "passport_no": None,
                "passport_expiry_date": None,
                "date_of_birth": None,
                "nid": None,
                "gender": None,
                "passport_dob": None,
                "passport_type": None,
                "second_nationality": None,
                "pilgrims": row["pilgrims"]
            })

        return {
            "lead_agency_name": lead_agency_name,
            "agencies": agencies
        }
    except Exception as e:
        raise e


async def check_lead_agency_assignment(db, agency_name):
    try:
        result = await admin_repository.check_lead_agency_assignment(db, agency_name)
        return {
            "agency_name": agency_name,
            "lead_agency_name": result
        }
    except Exception as e:
        raise e


async def get_child_agencies(db: AsyncSession, lead_agency_name: str):
    try:
        agencies = await admin_repository.get_child_agencies(db, lead_agency_name)
        return agencies
    except Exception as e:
        raise e


async def update_sub_agency_amount(db: AsyncSession, agency_name: str,
                                   sub_agency_account_update: SubAgencyAmountUpdateSchema):
    try:
        agencies = await admin_repository.get_child_agencies(db, agency_name)
        if sub_agency_account_update.agency_name not in agencies:
            raise HTTPException(status_code=400, detail="It is not your sub agency")

        request_schema = sub_agency_account_update.model_dump()
        request_schema["updated_by"] = agency_name
        request_schema["updated_at"] = get_current_time()

        return await admin_repository.update_sub_agency_amount(db, request_schema)
    except Exception as e:
        raise e


async def get_sub_agencies_with_amount(db, agency_name):
    try:
        agencies = await admin_repository.get_sub_agencies_with_amount(db, agency_name)
        return agencies
    except Exception as e:
        raise e


async def get_agency_amount(db:AsyncSession, agency_name:str):
    try:
        agency_amount = await admin_repository.get_agency_amount(db, agency_name)
        return agency_amount
    except Exception as e:
        raise e


async def update_logo(db:AsyncSession, request:LogoUpdateSchema, agency_name:str, username:str):
    try:
        request_dict = request.model_dump(exclude_none=True)
        request_dict['agency_name'] = agency_name
        request_dict['updated_by'] = username
        request_dict['updated_at'] = get_current_time()
        request_dict['user_name'] = username

        await admin_repository.update_logo(db=db, request_dict=request_dict)
        return True
    except Exception as e:
        raise e


async def get_admin_profile(db:AsyncSession, username:str, agency_name:str):
    try:
        admin = await admin_user_repository.get_admin_profile(db=db, username=username, agency_name=agency_name)
        if not admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Admin profile not found')
        await sign_admin_files(admin)
        admin['features'] = get_agency_features(agency_name)
        return AdminResponseSchema.model_validate(admin)
    except Exception as e:
        raise e