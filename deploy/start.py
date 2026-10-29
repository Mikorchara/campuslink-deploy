"""Render entry point. Never print environment values or raw database errors."""
from pathlib import Path
import os
import sys


def normalize_database_env(environment):
    from sqlalchemy.engine import make_url
    source = environment.get('CAMPUSLINK_DATABASE_URL', '')
    url = make_url(source)
    if url.get_backend_name() not in ('postgresql', 'postgres') or not url.host or not url.username:
        raise ValueError('A PostgreSQL session-pooler URI is required')
    password = environment.pop('CAMPUSLINK_DATABASE_PASSWORD', None)
    if password:
        url = url.set(password=password)
    if not url.password or '[' in url.password or 'YOUR-PASSWORD' in url.password:
        raise ValueError('A private database password is required')
    url = url.set(drivername='postgresql+psycopg').update_query_dict({'sslmode': 'require'})
    environment['CAMPUSLINK_DATABASE_URL'] = url.render_as_string(hide_password=False)


def main():
    print('Cloud startup: validating configuration.', flush=True)
    normalize_database_env(os.environ)
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / 'backend'))
    from src.config.settings import settings
    if settings.app_env != 'production' or settings.upload_storage != 'supabase':
        raise RuntimeError('Cloud deployment requires production settings and persistent Supabase images')
    if not settings.frontend_dist or not (Path(settings.frontend_dist) / 'index.html').is_file():
        raise RuntimeError('Compiled frontend is missing')
    from src.services.image_storage import ensure_cloud_bucket
    print('Cloud startup: checking private image storage.', flush=True)
    ensure_cloud_bucket()
    print('Cloud startup: private image storage ready.', flush=True)
    if os.environ.get('CAMPUSLINK_INITIALIZE_SCHEMA', '').lower() == 'true':
        from sqlalchemy import text
        from src.database.base import Base
        from src.database.session import engine
        import src.models
        print('Cloud startup: connecting to database and initializing schema.', flush=True)
        # Only adds absent model tables. Never seeds accounts or alters columns.
        with engine.begin() as connection:
            connection.execute(text("SELECT pg_advisory_xact_lock(729145820)"))
            Base.metadata.create_all(connection)
        print('Cloud schema initialization completed; no demo accounts seeded.', flush=True)
    port = int(os.environ.get('PORT', '10000'))
    if not 1 <= port <= 65535:
        raise ValueError('Invalid service port')
    import uvicorn
    uvicorn.run('src.main:app', host='0.0.0.0', port=port, log_level='warning',
                proxy_headers=True, forwarded_allow_ips=os.environ.get('FORWARDED_ALLOW_IPS', '127.0.0.1'))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Cloud startup failed (' + type(error).__name__ + '). Check private environment settings and service availability.', file=sys.stderr)
        status = getattr(error, 'upstream_http_status', None)
        if type(status) is int and 100 <= status <= 599:
            print('Image storage upstream HTTP status: ' + str(status) + '. No credentials or response body logged.', file=sys.stderr)
        sys.exit(1)
