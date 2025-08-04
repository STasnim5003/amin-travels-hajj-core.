import os
from urllib.parse import urlparse
from uuid import uuid4

import boto3
from dotenv import load_dotenv
from fastapi import Query, UploadFile

from infrastructure.schema.file_schema import FileUploadResponseSchema, \
    FileDownloadResponseSchema, FileUpdateResponseSchema, FileDeleteResponsesSchema

load_dotenv()




# MinIO Configuration
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv('FILE_ENDPOINT_URL'),  # MinIO endpoint
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION_NAME'),
)

bucket_name = os.getenv('BUCKET_NAME')



async def upload_file(file: UploadFile, name:str = "default",):
    ext = file.filename.split('.')[-1]
    key = f"{name}/{uuid4()}.{ext}"

    s3.upload_fileobj(file.file, bucket_name, key)

    file_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{bucket_name}/{key}"

    return FileUploadResponseSchema(
        name=name,
        file_url=file_url,
    )



async def get_download_url(url: str):
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": url},
        ExpiresIn=3600
    )
    return FileDownloadResponseSchema(
        download_url=url,
    )



async def update_file(key, new_file: UploadFile):
    # Delete old image
    s3.delete_object(Bucket=bucket_name, Key=key)

    # Upload new one
    ext = new_file.filename.split('.')[-1]
    new_key = f"users/{uuid4()}.{ext}"
    s3.upload_fileobj(new_file.file, bucket_name, new_key)

    new_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{bucket_name}/{new_key}"

    return FileUpdateResponseSchema(
        message="files updated",
        new_file_url=new_url,
    )




async def delete_file(key: str = Query(...)):
        # If full URL is accidentally passed, extract key part
        if key.startswith("http"):
            parsed = urlparse(key)
            key = "/".join(parsed.path.split("/")[2:])  # remove bucket name

        s3.delete_object(Bucket=bucket_name, Key=key)

        return FileDeleteResponsesSchema(
            message=f"Image '{key}' deleted successfully"
        )


