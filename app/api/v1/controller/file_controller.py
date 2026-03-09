import fastapi
from dotenv import load_dotenv
from fastapi import Form, UploadFile, File, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.core.middleware.middleware import get_current_user
from app.core.utils.authorize_api import has_required_permissions
from app.service import file_service
from infrastructure.schema.file_schema import FileUploadResponseSchema, FileDownloadResponseSchema

load_dotenv()

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")
private_router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/private")


@private_router.post("/file/upload", response_model=FileUploadResponseSchema, tags=["files"])
async def upload_file(
        file: UploadFile = File(...),
        name: str = Form(...),
        current_user: dict = Depends(get_current_user)
):
    has_required_permissions(current_user=current_user, roles=["SUPER_ADMIN", "AGENCY", "STAFF"])

    response = await file_service.upload_file(name=name, file=file)
    return JSONResponse(content=jsonable_encoder(response))


@private_router.get("/download-url", response_model=FileDownloadResponseSchema, tags=["files"])
async def get_download_url(
        key: str,
        # current_user: dict = Depends(get_current_user)
):
    # if current_user["role"] not in ["SUPER_ADMIN", "AGENCY"]:
    #     raise HTTPException(status_code=403, detail="Not authorized")
    response = await file_service.get_download_url(key=key)
    return JSONResponse(content=jsonable_encoder(response))
