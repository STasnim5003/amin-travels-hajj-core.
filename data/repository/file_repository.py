import os
from urllib.parse import urlparse
from uuid import uuid4

import boto3
from dotenv import load_dotenv
from fastapi import Query, UploadFile, HTTPException

from infrastructure.schema.file_schema import FileUploadResponseSchema, \
    FileDownloadResponseSchema, FileUpdateResponseSchema, FileDeleteResponsesSchema

load_dotenv()



# R2 config
R2_ACCESS_KEY = os.getenv("CLOUDFLARE_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("CLOUDFLARE_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT_URL = os.getenv("CLOUDFLARE_URL")
R2_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")


s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name="auto",
)
# # MinIO Configuration
# s3 = boto3.client(
#     "s3",
#     endpoint_url=os.getenv('FILE_ENDPOINT_URL'),  # MinIO endpoint
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#     region_name=os.getenv('AWS_REGION_NAME'),
#     config=boto3.session.Config(signature_version='s3v4')
# )



async def upload_file(file: UploadFile, name: str = "default"):
    ext = file.filename.split(".")[-1]
    key = f"{name}/{uuid4()}.{ext}"

    # Upload file to Cloudflare R2
    s3.upload_fileobj(file.file, R2_BUCKET_NAME, key)

    # Public URL depends on your custom domain / bucket settings
    file_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{key}"

    return FileUploadResponseSchema(
        name=name,
        file_url=file_url,
    )


async def get_download_url(file_url: str):
    try:
        # Parse the URL
        parsed = urlparse(file_url)

        path_parts = parsed.path.lstrip("/").split("/", 1)
        if len(path_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid file URL")

        object_key = path_parts[1]  # everything after the bucket folder (hajj/...)

        # Generate presigned URL for R2
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": R2_BUCKET_NAME, "Key": object_key},
            ExpiresIn=3600  # 1 hour
        )

        # return FileDownloadResponseSchema(download_url=presigned_url)
        return presigned_url

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")
# async def get_download_url(url: str):
#     parsed = urlparse(url)
#
#     # If it's a full URL, strip to just the path
#     if parsed.scheme in ("http", "https"):
#         # EXTRACT key from full URL
#         object_key = parsed.path.replace(f"/{bucket_name}/", "").lstrip("/")
#     else:
#         # Treat as direct object key (safe fallback)
#         object_key = url.strip("/")
#
#     # Generate presigned URL
#     presigned_url = s3.generate_presigned_url(
#         "get_object",
#         Params={"Bucket": bucket_name, "Key": object_key},
#         ExpiresIn=3600
#     )
#
#     return FileDownloadResponseSchema(download_url=presigned_url)
#
#
#
# async def update_file(key, new_file: UploadFile):
#     # Delete old image
#     s3.delete_object(Bucket=bucket_name, Key=key)
#
#     # Upload new one
#     ext = new_file.filename.split('.')[-1]
#     new_key = f"users/{uuid4()}.{ext}"
#     s3.upload_fileobj(new_file.file, bucket_name, new_key)
#
#     new_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{bucket_name}/{new_key}"
#
#     return FileUpdateResponseSchema(
#         message="files updated",
#         new_file_url=new_url,
#     )
#
#
#
#
# async def delete_file(key: str = Query(...)):
#         # If full URL is accidentally passed, extract key part
#         if key.startswith("http"):
#             parsed = urlparse(key)
#             key = "/".join(parsed.path.split("/")[2:])  # remove bucket name
#
#         s3.delete_object(Bucket=bucket_name, Key=key)
#
#         return FileDeleteResponsesSchema(
#             message=f"Image '{key}' deleted successfully"
#         )
#
#
