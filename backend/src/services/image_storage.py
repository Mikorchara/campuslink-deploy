"""Keep uploaded images off the ephemeral web-service filesystem."""
from pathlib import Path
import json
import urllib.error
import urllib.request

from src.config.settings import settings
from src.core.exceptions import AppError


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None  # Never forward a privileged key to a redirect destination.


def storage_request(method: str, route: str, content: bytes | None = None, content_type='image/webp') -> bytes:
    url = f'{settings.supabase_url.rstrip("/")}/storage/v1/{route}'
    key = settings.supabase_storage_key.get_secret_value()
    headers = {'apikey': key}
    # New sb_secret_* keys go only in apikey. Legacy service_role JWTs also
    # use Authorization. Neither kind is ever sent to the browser.
    if key.startswith('eyJ'):
        headers['Authorization'] = 'Bearer ' + key
    if content is not None:
        headers['Content-Type'] = content_type
        headers['x-upsert'] = 'false'
    request = urllib.request.Request(url, data=content, headers=headers, method=method)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
            if method != 'GET':
                return b''
            payload = response.read(8 * 1024 * 1024 + 1)
            if len(payload) > 8 * 1024 * 1024:
                raise AppError(502, '图片读取失败，请稍后重试')
            return payload
    except urllib.error.HTTPError as error:
        status = error.code
        # Storage REST can wrap a logical 404 inside an HTTP 400 response.
        # Read only a bounded JSON body; never log or return upstream text.
        missing = status == 404
        if status == 400 and method == 'GET':
            try:
                detail = json.loads(error.read(16384))
                missing = isinstance(detail, dict) and (
                    str(detail.get('statusCode')) == '404'
                    or detail.get('code') in ('NoSuchBucket', 'NoSuchKey'))
            except (ValueError, OSError):
                pass
        error.close()
        if method == 'GET' and missing:
            raise AppError(404, '图片不存在') from None
        failure = AppError(503, '图片存储暂时不可用，请稍后重试')
        failure.upstream_http_status = status
        raise failure from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise AppError(503, '图片存储暂时不可用，请稍后重试') from None


def save_image(filename: str, content: bytes) -> None:
    if settings.upload_storage == 'supabase':
        storage_request('POST', f'object/{settings.supabase_storage_bucket}/{filename}', content)
    else:
        folder = Path(settings.upload_dir).resolve()
        folder.mkdir(parents=True, exist_ok=True)
        (folder / filename).write_bytes(content)


def cloud_image(filename: str) -> bytes:
    return storage_request('GET', f'object/authenticated/{settings.supabase_storage_bucket}/{filename}')


def ensure_cloud_bucket() -> None:
    try:
        bucket = json.loads(storage_request('GET', 'bucket/' + settings.supabase_storage_bucket))
    except AppError as error:
        if error.status_code != 404:
            raise
        payload = json.dumps({'id': settings.supabase_storage_bucket, 'name': settings.supabase_storage_bucket,
                              'public': False, 'file_size_limit': 8 * 1024 * 1024,
                              'allowed_mime_types': ['image/webp']}).encode()
        storage_request('POST', 'bucket', payload, 'application/json')
        return
    if bucket.get('public') is not False:
        raise RuntimeError('Cloud image bucket must be private; no bucket access settings were changed')
