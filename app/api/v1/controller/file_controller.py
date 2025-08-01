import os
from urllib.parse import urlparse
from uuid import uuid4

import boto3
import fastapi
from dotenv import load_dotenv
from fastapi import UploadFile, File, Form, Query, HTTPException

load_dotenv()

router = fastapi.APIRouter(prefix="/amin-travels-hajj-core/api/v1/public")


# MinIO Configuration
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv('FILE_ENDPOINT_URL'),  # MinIO endpoint
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION_NAME'),
)

bucket_name = os.getenv('BUCKET_NAME')


@router.post("/upload" ,tags=["files"])
async def upload_image(name: str = "", image: UploadFile = File(...)):
    ext = image.filename.split('.')[-1]
    key = f"users/{uuid4()}.{ext}"

    s3.upload_fileobj(image.file, bucket_name, key)

    image_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{bucket_name}/{key}"

    return {"name": name, "image_url": image_url}


@router.get("/download-url" ,tags=["files"])
def get_download_url(url: str):
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": url},
        ExpiresIn=3600
    )
    return {"download_url": url}


@router.put("/update" ,tags=["files"])
async def update_image(old_url: str = Form(...), new_image: UploadFile = File(...)):
    # Delete old image
    s3.delete_object(Bucket=bucket_name, Key=old_url)

    # Upload new one
    ext = new_image.filename.split('.')[-1]
    new_key = f"users/{uuid4()}.{ext}"
    s3.upload_fileobj(new_image.file, bucket_name, new_key)

    new_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{bucket_name}/{new_key}"

    return {"message": "Image updated", "image_url": new_url, "key": new_key}



@router.delete("/delete" ,tags=["files"])
def delete_image(key: str = Query(...)):
    try:
        # If full URL is accidentally passed, extract key part
        if key.startswith("http"):
            parsed = urlparse(key)
            key = "/".join(parsed.path.split("/")[2:])  # remove bucket name

        s3.delete_object(Bucket=bucket_name, Key=key)
        return {"message": f"Image '{key}' deleted successfully"}

    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
