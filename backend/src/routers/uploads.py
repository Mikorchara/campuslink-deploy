from io import BytesIO
from pathlib import Path
import re
from uuid import uuid4
import warnings

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import Response
from PIL import Image, ImageOps, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from src.config.settings import settings
from src.core.exceptions import AppError
from src.dependencies.auth import CurrentUser
from src.schemas.common import success
from src.services.image_storage import save_image, cloud_image

router = APIRouter(prefix="/uploads", tags=["Uploads"])
MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 20_000_000


def store_image(content: bytes) -> str:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise AppError(422, "请上传 JPEG、PNG 或 WebP 图片")
                if source.width * source.height > MAX_PIXELS:
                    raise AppError(422, "图片像素过大，请缩小后上传")
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((2048, 2048))
                filename = f"{uuid4().hex}.webp"
                # Re-encode pixels and discard user-supplied names and metadata.
                encoded = BytesIO()
                image.save(encoded, "WEBP", quality=85)
                save_image(filename, encoded.getvalue())
                return filename
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise AppError(422, "图片无效或已损坏，请重新选择") from None


@router.post("", status_code=201)
async def upload_image(file: UploadFile, _current_user: CurrentUser):
    try:
        content = await file.read(MAX_BYTES + 1)
    finally:
        await file.close()
    if not content or len(content) > MAX_BYTES:
        raise AppError(422, "图片不能为空，且不能超过 5 MB")
    filename = await run_in_threadpool(store_image, content)
    return success({"image_url": f"{settings.api_prefix}/uploads/{filename}"}, code=201)


@router.get("/{filename}")
def read_image(filename: str):
    if not re.fullmatch(r"[0-9a-f]{32}\.webp", filename):
        raise AppError(404, "图片不存在")
    if settings.upload_storage == 'supabase':
        return Response(cloud_image(filename), media_type='image/webp', headers={'X-Content-Type-Options': 'nosniff'})
    path = Path(settings.upload_dir).resolve() / filename
    if not path.is_file():
        raise AppError(404, "图片不存在")
    return FileResponse(path, media_type="image/webp", headers={"X-Content-Type-Options": "nosniff"})
