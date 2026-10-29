import importlib.util
from pathlib import Path

import pytest
from sqlalchemy.engine import make_url

spec = importlib.util.spec_from_file_location('cloud_entry', Path(__file__).with_name('start.py'))
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)


def test_password_is_encoded_without_manual_uri_edits():
    password = 'test-only:p@ss/#word?%'
    env = {'CAMPUSLINK_DATABASE_URL': 'postgresql://postgres.project:[YOUR-PASSWORD]@pooler.example:5432/postgres',
           'CAMPUSLINK_DATABASE_PASSWORD': password}
    entry.normalize_database_env(env)
    url = make_url(env['CAMPUSLINK_DATABASE_URL'])
    assert url.password == password and url.drivername == 'postgresql+psycopg'
    assert url.query['sslmode'] == 'require'
    assert 'CAMPUSLINK_DATABASE_PASSWORD' not in env


@pytest.mark.parametrize('value', ['', 'sqlite://', 'postgresql://user:[YOUR-PASSWORD]@pooler.example/postgres'])
def test_incomplete_database_configuration_is_rejected(value):
    with pytest.raises(Exception): entry.normalize_database_env({'CAMPUSLINK_DATABASE_URL': value})
