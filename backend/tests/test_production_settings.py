import pytest
from pydantic import ValidationError
from src.config.settings import Settings


def production(**overrides):
    values = dict(app_env='production', database_url='postgresql+psycopg://localhost/example',
                  jwt_secret_key='a-private-test-key-of-at-least-thirty-two-characters',
                  debug=False, seed_demo_data=False, auto_create_tables=False)
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.mark.parametrize('overrides', [
    {'database_url': 'sqlite://'}, {'jwt_secret_key': 'replace-with-a-placeholder'},
    {'debug': True}, {'seed_demo_data': True}, {'auto_create_tables': True},
])
def test_production_rejects_development_defaults(overrides):
    with pytest.raises(ValidationError): production(**overrides)


def test_production_accepts_explicit_postgres_settings():
    assert production().app_env == 'production'
