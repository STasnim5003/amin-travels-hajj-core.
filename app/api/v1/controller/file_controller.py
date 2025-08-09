from typing import Optional

import fastapi
from dotenv import load_dotenv
from fastapi import Form, Query, UploadFile, File
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.service import file_service
from infrastructure.schema.file_schema import FileUploadResponseSchema, FileDownloadResponseSchema, \
    FileUpdateResponseSchema, FileDeleteResponsesSchema

load_dotenv()

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")




@router.post("/upload", response_model=FileUploadResponseSchema ,tags=["files"])
async def upload_file(
                        file: UploadFile = File(...),
                        name: Optional[str] = "default",
                      ):
    response = await file_service.upload_file(name=name, file=file)
    return JSONResponse(content=jsonable_encoder(response))



@router.get("/download-url", response_model=FileDownloadResponseSchema ,tags=["files"])
async def get_download_url(key: str):
    response = await file_service.get_download_url(key=key)
    return JSONResponse(content=jsonable_encoder(response))



@router.put("/update", response_model=FileUpdateResponseSchema ,tags=["files"])
async def update_file(
        new_file: upload_file = File(...),
        key: str = Form(...),
):
    response = await file_service.update_file(key=key, new_file=new_file)
    return JSONResponse(content=jsonable_encoder(response))



@router.delete("/delete" ,response_model=FileDeleteResponsesSchema,tags=["files"])
async def delete_image(key: str = Query(...)):
    response = await file_service.delete_file(key=key)
    return JSONResponse(content=jsonable_encoder(response))

