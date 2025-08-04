from typing import Optional

from pydantic import BaseModel


# class FileUploadRequestSchema(BaseModel):
#     name: Optional[str] = Field(None)
#     file: UploadFile = File(...)

class FileUploadResponseSchema(BaseModel):
    name: Optional[str]
    file_url: str

class FileDownloadResponseSchema(BaseModel):
    download_url: str
#
# class FileUpdateRequestSchema(BaseModel):
#     new_file: UploadFile = File(...)


class FileUpdateResponseSchema(BaseModel):
    message: str
    new_file_url: str

class FileDeleteResponsesSchema(BaseModel):
    message: str