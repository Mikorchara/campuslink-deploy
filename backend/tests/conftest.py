from collections.abc import Generator
import os
from uuid import uuid4

# Test startup must never create, seed, or connect to the developer's database.
# These values must be set before importing application settings or the engine.
os.environ["CAMPUSLINK_DATABASE_URL"] = "sqlite://"
os.environ["CAMPUSLINK_AUTO_CREATE_TABLES"] = "false"
os.environ["CAMPUSLINK_SEED_DEMO_DATA"] = "false"
os.environ["CAMPUSLINK_APP_ENV"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from src.database.base import Base
from src.database.session import get_db, configure_sqlite_engine
from src.main import app


@pytest.fixture
def client(tmp_path) -> Generator[TestClient, None, None]:
    postgres_url = os.environ.get("CAMPUSLINK_TEST_DATABASE_URL")
    schema = None
    admin_engine = None
    if postgres_url:
        parsed = make_url(postgres_url)
        if parsed.get_backend_name() != "postgresql" or not (parsed.database or '').startswith('campuslink_test_'):
            raise RuntimeError('Tests require a separate campuslink_test_* PostgreSQL database')
        schema = f"campuslink_test_{uuid4().hex}"
        admin_engine = create_engine(postgres_url, hide_parameters=True)
        with admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        test_engine = create_engine(postgres_url, hide_parameters=True,
                                    connect_args={"options": f"-csearch_path={schema}"})
    else:
        database_path = tmp_path / "test.db"
        test_engine = create_engine(
            f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
        )
        configure_sqlite_engine(test_engine)
    testing_session = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()
        if schema:
            # Only remove the UUID schema created by this fixture, never shared tables.
            with admin_engine.begin() as connection:
                connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            admin_engine.dispose()


def register_and_login(
    client: TestClient,
    username: str,
    email: str,
    password: str = "123456",
) -> str:
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["data"]["token"]


@pytest.fixture
def auth_header(client: TestClient) -> dict[str, str]:
    token = register_and_login(client, "seller", "seller@example.com")
    return {"Authorization": f"Bearer {token}"}

