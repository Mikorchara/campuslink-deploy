"""Back up, migrate and restore without overwriting a populated destination."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from uuid import uuid4

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import URL, make_url

from src.config.settings import settings
from src.database.base import Base
import src.models  # register every model with Base


def engine():
    return create_engine(settings.database_url, hide_parameters=True)


def digest(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def normalized(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc).isoformat(timespec='microseconds') if value.tzinfo is None else value.astimezone(timezone.utc).isoformat(timespec='microseconds')
    if isinstance(value, Decimal): return format(value, '.2f')
    if isinstance(value, Enum): return value.value
    return value


def snapshot(connection, *, missing_as_empty=False):
    result = {}
    existing = set(inspect(connection).get_table_names())
    for table in Base.metadata.sorted_tables:
        if table.name not in existing and not missing_as_empty:
            continue
        rows = connection.execute(select(table).order_by(table.c.id)).mappings().all() if table.name in existing else []
        payload = [{k: normalized(v) for k, v in row.items()} for row in rows]
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        result[table.name] = {'rows': len(rows), 'sha256': hashlib.sha256(encoded).hexdigest()}
    return result


def ensure_empty(connection):
    names = inspect(connection).get_table_names()
    if any(name not in Base.metadata.tables for name in names):
        raise RuntimeError('Destination contains unrelated tables; refusing to change it')
    for name in names:
        table = Base.metadata.tables[name]
        if connection.execute(select(table.c.id).limit(1)).first():
            raise RuntimeError('Destination database contains data; refusing to overwrite it')


def sqlite_migrate(source, backup_root):
    target = engine()
    if target.dialect.name != 'postgresql': raise RuntimeError('Migration destination must be PostgreSQL')
    with target.connect() as connection: ensure_empty(connection)
    source = Path(source).resolve()
    if not source.is_file(): raise RuntimeError('SQLite source does not exist')
    output = Path(backup_root).resolve() / f'sqlite-before-postgres-{uuid4().hex}'
    output.mkdir(parents=True, exist_ok=False)
    saved = output / 'campuslink.sqlite3'
    source_hash = digest(source)
    with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original:
        with sqlite3.connect(saved) as backup:
            original.backup(backup)
    copied = create_engine(URL.create('sqlite', database=str(saved)), hide_parameters=True)
    with copied.connect() as source_connection, target.begin() as destination:
        before = snapshot(source_connection, missing_as_empty=True)
        source_tables = set(inspect(source_connection).get_table_names())
        Base.metadata.create_all(bind=destination)
        for table in Base.metadata.sorted_tables:
            # SQLite CURRENT_TIMESTAMP is UTC but has no offset. PostgreSQL must
            # not interpret these values in the server's local timezone.
            rows = [{key: value.replace(tzinfo=timezone.utc) if isinstance(value, datetime) and value.tzinfo is None else value
                     for key, value in row.items()}
                    for row in source_connection.execute(select(table)).mappings()] if table.name in source_tables else []
            if rows: destination.execute(table.insert(), rows)
            quoted = destination.dialect.identifier_preparer.quote(table.name)
            destination.execute(text(
                f"SELECT setval(pg_get_serial_sequence(:table, 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {quoted}), 1), EXISTS(SELECT 1 FROM {quoted}))"
            ), {'table': table.name})
        if snapshot(destination) != before:
            raise RuntimeError('Migrated data verification failed; destination transaction rolled back')
    copied.dispose(); target.dispose()
    manifest = {'source_file_sha256_before': source_hash, 'source_file_sha256_after': digest(source),
                'sqlite_backup_sha256': digest(saved), 'tables': before}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('SQLite migration verified; row IDs, password hashes, timestamps, amounts and sequences preserved.')
    print('Row counts: ' + ', '.join(f'{name}={data["rows"]}' for name, data in before.items()))
    print(f'Original SQLite remains at {source}; snapshot saved under {output.name}.')


def pg_command(program, *args):
    parsed = make_url(settings.database_url)
    if parsed.get_backend_name() != 'postgresql': raise RuntimeError('This command requires PostgreSQL')
    env = dict(os.environ)
    if parsed.password: env['PGPASSWORD'] = parsed.password
    env['PGCLIENTENCODING'] = 'UTF8'
    binary = Path(os.environ.get('CAMPUSLINK_PG_BIN', '')) / (program + ('.exe' if os.name == 'nt' else ''))
    command = [str(binary), '--host', parsed.host or 'localhost', '--port', str(parsed.port or 5432),
               '--username', parsed.username or 'postgres', '--dbname', parsed.database, *map(str, args)]
    result = subprocess.run(command, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace',
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if result.returncode: raise RuntimeError(f'{program} failed; destination remains separate from the active database')


def file_manifest(folder):
    folder = Path(folder)
    if not folder.exists(): return {}
    result = {}
    for item in sorted(folder.rglob('*')):
        if item.is_symlink(): raise RuntimeError('Upload directory contains a symlink; refusing to follow it')
        if item.is_file():
            item.resolve().relative_to(folder.resolve())
            result[item.relative_to(folder).as_posix()] = digest(item)
    return result


def backup(output):
    if settings.upload_storage != 'local':
        raise RuntimeError('Cloud uploads require a separate storage backup; refusing to produce an incomplete local backup')
    target = engine()
    if target.dialect.name != 'postgresql': raise RuntimeError('This backup command requires PostgreSQL')
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    with target.connect().execution_options(isolation_level='REPEATABLE READ') as connection:
        with connection.begin():
            exported = connection.execute(text('SELECT pg_export_snapshot()')).scalar_one()
            data = snapshot(connection)
            pg_command('pg_dump', '--format=custom', '--no-owner', '--no-acl', f'--snapshot={exported}', '--file', output / 'database.dump')
            source_uploads = Path(settings.upload_dir).resolve()
            file_manifest(source_uploads)  # reject links before copying
            if source_uploads.exists(): shutil.copytree(source_uploads, output / 'uploads')
            else: (output / 'uploads').mkdir()
    manifest = {'format': 1, 'created_at_utc': datetime.now(timezone.utc).isoformat(), 'tables': data,
                'database_sha256': digest(output / 'database.dump'), 'uploads': file_manifest(output / 'uploads')}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    target.dispose()
    print(f'Backup saved to {output.name}: database and {len(manifest["uploads"])} uploaded files.')


def checked_manifest(folder):
    folder = Path(folder).resolve()
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format') != 1 or digest(folder / 'database.dump') != manifest['database_sha256']:
        raise RuntimeError('Backup format or database checksum is invalid')
    if file_manifest(folder / 'uploads') != manifest['uploads']:
        raise RuntimeError('Backup image checksums are invalid')
    return folder, manifest


def restore(folder):
    folder, _ = checked_manifest(folder)
    destination = engine()
    if destination.dialect.name != 'postgresql': raise RuntimeError('Restore destination must be PostgreSQL')
    with destination.connect() as connection:
        if inspect(connection).get_table_names():
            raise RuntimeError('Restore requires a brand-new empty database; refusing to overwrite tables')
    uploads = Path(settings.upload_dir).resolve()
    if uploads.exists(): raise RuntimeError('Restore upload directory already exists; refusing to overwrite files')
    pg_command('pg_restore', '--no-owner', '--no-acl', '--single-transaction', '--exit-on-error', folder / 'database.dump')
    shutil.copytree(folder / 'uploads', uploads)
    destination.dispose()
    verify(folder)


def verify(folder):
    _, manifest = checked_manifest(folder)
    destination = engine()
    with destination.connect() as connection:
        if snapshot(connection) != manifest['tables']: raise RuntimeError('Restored database differs from the backup')
    if file_manifest(Path(settings.upload_dir).resolve()) != manifest['uploads']:
        raise RuntimeError('Restored covers differ from the backup')
    destination.dispose()
    print(f'RESTORE VERIFIED: all {len(manifest["tables"])} table fingerprints and every uploaded file match the backup.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['init', 'migrate-sqlite', 'backup', 'restore', 'verify'])
    parser.add_argument('--source')
    parser.add_argument('--backup-root', default='./.backups')
    parser.add_argument('--output')
    parser.add_argument('--backup')
    args = parser.parse_args()
    if args.action == 'init':
        target = engine()
        with target.begin() as connection: Base.metadata.create_all(bind=connection)
        target.dispose(); print('Database schema initialized; existing rows were not changed.')
    elif args.action == 'migrate-sqlite':
        if not args.source: parser.error('--source is required')
        sqlite_migrate(args.source, args.backup_root)
    elif args.action == 'backup':
        if not args.output: parser.error('--output is required')
        backup(args.output)
    else:
        if not args.backup: parser.error('--backup is required')
        if args.action == 'restore': restore(args.backup)
        else: verify(args.backup)


if __name__ == '__main__':
    try: main()
    except Exception as error:
        message = str(error) if isinstance(error, RuntimeError) else 'Check database settings and backup paths; no credentials are printed.'
        print(f'Database operation failed ({type(error).__name__}): {message}', file=sys.stderr)
        sys.exit(1)
