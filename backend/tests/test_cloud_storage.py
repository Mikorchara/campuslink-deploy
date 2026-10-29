from io import BytesIO
import urllib.error

import pytest
from pydantic import SecretStr, ValidationError

from src.config.settings import Settings, settings
from src.core.exceptions import AppError
from src.services import image_storage
from tests.test_uploads import image_bytes


@pytest.fixture
def remote(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, 'upload_storage', 'supabase')
    monkeypatch.setattr(settings, 'supabase_url', 'https://test-project.supabase.co')
    monkeypatch.setattr(settings, 'supabase_storage_key', SecretStr('sb_secret_test-only-key'))
    monkeypatch.setattr(settings, 'upload_dir', str(tmp_path / 'unused'))
    objects, calls = {}, []

    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            assert timeout == 20
            assert request.get_header('Apikey') == 'sb_secret_test-only-key'
            assert request.get_header('Authorization') is None
            assert 'sb_secret' not in request.full_url
            name = request.full_url.rsplit('/', 1)[-1]
            if request.method == 'POST':
                objects[name] = request.data
                return BytesIO(b'{}')
            assert '/object/authenticated/' in request.full_url
            return BytesIO(objects[name])

    monkeypatch.setattr(image_storage.urllib.request, 'build_opener', lambda *_: Opener())
    return objects, calls, tmp_path


def test_cloud_upload_survives_loss_of_local_files(client, auth_header, remote):
    objects, calls, tmp_path = remote
    uploaded = client.post('/api/uploads', headers=auth_header, files={'file': ('image.png', image_bytes(), 'image/png')})
    assert uploaded.status_code == 201
    url = uploaded.json()['data']['image_url']
    assert 'test-only-key' not in uploaded.text
    assert not (tmp_path / 'unused').exists()
    stored = client.get(url)
    assert stored.status_code == 200 and stored.headers['content-type'] == 'image/webp'
    assert stored.content == objects[url.rsplit('/', 1)[-1]]
    assert len(calls) == 2
    # Invalid filenames are rejected before calling remote storage.
    assert client.get('/api/uploads/invalid.webp').status_code == 404
    assert len(calls) == 2


def test_cloud_failure_is_not_a_success_or_local_fallback(client, auth_header, remote, monkeypatch):
    class Failure:
        def open(self, *_args, **_kwargs):
            raise urllib.error.URLError('private server diagnostics must not leak')
    monkeypatch.setattr(image_storage.urllib.request, 'build_opener', lambda *_: Failure())
    response = client.post('/api/uploads', headers=auth_header, files={'file': ('x.png', image_bytes())})
    assert response.status_code == 503
    assert 'private server' not in response.text and 'sb_secret' not in response.text
    assert not (remote[2] / 'unused').exists()


def test_remote_missing_image_returns_404(client, remote, monkeypatch):
    class Missing:
        def open(self, *_args, **_kwargs):
            raise urllib.error.HTTPError('https://example.invalid', 404, 'missing', {}, BytesIO())
    monkeypatch.setattr(image_storage.urllib.request, 'build_opener', lambda *_: Missing())
    assert client.get('/api/uploads/' + 'a' * 32 + '.webp').status_code == 404


def test_bucket_creation_is_private_and_does_not_change_existing_access(remote, monkeypatch):
    calls = []
    def missing(method, route, content=None, content_type=None):
        calls.append((method, route, content))
        if method == 'GET':
            raise AppError(404, 'missing')
        return b''
    monkeypatch.setattr(image_storage, 'storage_request', missing)
    image_storage.ensure_cloud_bucket()
    import json
    assert json.loads(calls[-1][2])['public'] is False
    monkeypatch.setattr(image_storage, 'storage_request', lambda *_: b'{"public":true}')
    with pytest.raises(RuntimeError): image_storage.ensure_cloud_bucket()


@pytest.mark.parametrize('overrides', [
    {'supabase_url': 'http://test-project.supabase.co'},
    {'supabase_url': 'https://example.com'},
    {'supabase_url': 'https://test-project.supabase.co/evil'},
    {'supabase_storage_key': None}, {'supabase_storage_key': 'sb_publishable_not-a-server-key'},
    {'supabase_storage_bucket': '../escape'},
])
def test_storage_configuration_validation(overrides):
    args = dict(upload_storage='supabase', supabase_url='https://test-project.supabase.co', supabase_storage_key='sb_secret_test-only-key')
    with pytest.raises(ValidationError): Settings(_env_file=None, **(args | overrides))


def test_redirect_does_not_forward_privileged_headers():
    assert image_storage.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example') is None


@pytest.mark.parametrize('body', [b'{"statusCode":"404","message":"private detail"}',
                                b'{"code":"NoSuchBucket"}'])
def test_http_400_wrapped_missing_bucket_is_created_privately(remote, monkeypatch, body):
    calls = []
    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            if request.method == 'GET':
                raise urllib.error.HTTPError('https://example.invalid', 400, 'bad request', {}, BytesIO(body))
            return BytesIO(b'{}')
    monkeypatch.setattr(image_storage.urllib.request, 'build_opener', lambda *_: Opener())
    image_storage.ensure_cloud_bucket()
    import json
    assert len(calls) == 2
    assert calls[1].method == 'POST' and json.loads(calls[1].data)['public'] is False


@pytest.mark.parametrize('status,body', [(401, b'{"statusCode":"404"}'),
                                      (403, b'private secret'), (400, b'not json'),
                                      (400, b'{"statusCode":"403"}')])
def test_storage_auth_or_invalid_response_never_creates_bucket(remote, monkeypatch, status, body):
    calls = []
    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            raise urllib.error.HTTPError('https://example.invalid', status, 'private diagnostic', {}, BytesIO(body))
    monkeypatch.setattr(image_storage.urllib.request, 'build_opener', lambda *_: Opener())
    with pytest.raises(AppError) as caught:
        image_storage.ensure_cloud_bucket()
    assert caught.value.status_code == 503
    assert caught.value.upstream_http_status == status
    assert 'private' not in str(caught.value)
    assert len(calls) == 1
