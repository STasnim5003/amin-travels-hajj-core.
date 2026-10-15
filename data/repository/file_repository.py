import io
import os
from urllib.parse import urlparse
from uuid import uuid4

import boto3
from dotenv import load_dotenv
from fastapi import Query, UploadFile, HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

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



# Upload rules. The type comes from the file's first bytes, never from the client's filename or content_type.
MAX_BYTES = 10 * 1024 * 1024
ALLOWED_MAGIC = {b"\xff\xd8\xff": ("jpg", "image/jpeg"), b"\x89PNG": ("png", "image/png"),
                 b"%PDF-": ("pdf", "application/pdf")}
# Same numbers as the frontend (lib/imageCompression.ts)
MAX_EDGE, JPEG_QUALITY = 2000, 82
SKIP_BYTES = 1024 * 1024  # frontend output (<= 2000 px, no EXIF) under this size is stored as-is
MAX_PIXELS = 60_000_000  # rejects decompression bombs before decoding


def _detect_type(head: bytes):
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp", "image/webp"
    for magic, kind in ALLOWED_MAGIC.items():
        if head.startswith(magic):
            return kind
    raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP or PDF files are allowed")


def _shrink_image(data: bytes):
    """(bytes, ext, content_type) to store instead of the upload, or None to store it unchanged.
    Images the frontend already compressed (<= 2000 px, under 1 MB, no EXIF) are not re-encoded.
    Anything else is, which drops EXIF (phone GPS) and anything hidden after the pixel data.
    Transparent images (signatures, seals, logos) stay PNG and are never flattened onto a background."""
    try:
        img = Image.open(io.BytesIO(data))
        if img.width * img.height > MAX_PIXELS:
            raise HTTPException(status_code=400, detail="Image dimensions are too large")
        has_exif = bool(img.getexif())
        if not has_exif and len(data) < SKIP_BYTES and max(img.size) <= MAX_EDGE:
            return None
        if "transparency" in img.info or img.mode in ("P", "PA"):
            img = img.convert("RGBA")
        has_alpha = img.mode in ("RGBA", "LA") and img.getchannel("A").getextrema()[0] < 255
        img = ImageOps.exif_transpose(img).convert("RGBA" if has_alpha else "RGB")
        img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
        out = io.BytesIO()
        if has_alpha:
            img.save(out, "PNG", optimize=True)
            result = (out.getvalue(), "png", "image/png")
        else:
            img.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True)
            result = (out.getvalue(), "jpg", "image/jpeg")
    except HTTPException:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="Image file is damaged or unreadable")
    # with EXIF the re-encoded copy is kept even if larger, so the metadata never reaches storage
    return result if has_exif or len(result[0]) < len(data) else None


async def upload_file(file: UploadFile, name: str = "default"):
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 10 MB")
    ext, content_type = _detect_type(data[:16])
    if content_type.startswith("image/"):
        shrunk = await run_in_threadpool(_shrink_image, data)
        if shrunk:
            data, ext, content_type = shrunk
    key = f"{name}/{uuid4()}.{ext}"

    # Upload file to Cloudflare R2
    await run_in_threadpool(s3.put_object, Bucket=R2_BUCKET_NAME, Key=key,
                            Body=data, ContentType=content_type)

    # Public URL depends on your custom domain / bucket settings
    file_url = f"{os.getenv('FILE_ENDPOINT_URL')}/{key}"

    return FileUploadResponseSchema(
        name=name,
        file_url=file_url,
    )


def get_object_key(file_url: str) -> str:
    path_parts = urlparse(file_url).path.lstrip("/").split("/", 1)
    if len(path_parts) < 2 or not path_parts[1]:
        raise HTTPException(status_code=400, detail="Invalid file URL")
    return path_parts[1]  # everything after the bucket folder (hajj/...)


# Tables whose JSON columns hold uploaded file URLs, with the column naming the owning agency
AGENCY_FILE_COLUMNS = {
    "admin": ("agency_name", ["logo", "passport_copy", "signature", "seal"]),
    "admin_user": ("agency_name", ["ekama_file"]),
    "payment": ("agency_name", ["receipt"]),
    "umrah_customer_billing": ("agency_name", ["receipt"]),
    "hotel_request": ("agency_name", ["document", "tasria_copy"]),
    "payment_request_b2b": ("agency_name", ["money_receipt_payment_slip_file"]),
    "flight_purchase": ("agency_name", ["ticket_file"]),
    "hotel_purchase": ("agency_name", ["booking_file"]),
    "food_purchase": ("agency_name", ["booking_file"]),
    "route_purchase": ("agency_name", ["booking_file"]),
    "pilgrim_data": ("group_name", ["passport_copy"]),
}

_AGENCY_FILE_SQL = text(" UNION ".join(
    f"SELECT LOWER(BTRIM({owner})) AS agency FROM core.{table} WHERE "
    + " OR ".join(f"{col}::text LIKE :pattern" for col in cols)
    for table, (owner, cols) in AGENCY_FILE_COLUMNS.items()
))

# Records a pilgrim token may download from: their own passport copy and their own payment receipts
_PILGRIM_FILE_SQL = text("""
    SELECT 1 FROM core.pilgrim_data
        WHERE tracking_id = :tracking_id AND passport_copy::text LIKE :pattern
    UNION ALL
    SELECT 1 FROM core.payment
        WHERE (tracking_id = :tracking_id OR pilgrims_tracking_id::text LIKE :tracking_pattern)
          AND receipt::text LIKE :pattern
    LIMIT 1
""")


def _like_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _stored_url_pattern(object_key: str) -> str:
    # matches the whole stored URL ending in this key, e.g. "https://host/bucket/receipt/<uuid>.jpg"
    return f'%/{_like_escape(object_key)}"%'


async def get_file_agencies(db: AsyncSession, object_key: str) -> set:
    """Lower-cased agency names whose records hold this file; empty if no known record does."""
    result = await db.execute(_AGENCY_FILE_SQL, {"pattern": _stored_url_pattern(object_key)})
    return {row.agency for row in result if row.agency}


async def is_pilgrim_file(db: AsyncSession, tracking_id: str, object_key: str) -> bool:
    result = await db.execute(_PILGRIM_FILE_SQL, {
        "tracking_id": tracking_id,
        "tracking_pattern": f'%"{_like_escape(tracking_id)}"%',
        "pattern": _stored_url_pattern(object_key),
    })
    return result.first() is not None


async def get_download_url(file_url: str):
    try:
        object_key = get_object_key(file_url)

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
