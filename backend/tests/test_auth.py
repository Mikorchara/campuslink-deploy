from fastapi.testclient import TestClient


def test_register_login_and_get_profile(client: TestClient) -> None:
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "Tom",
            "email": "tom@example.com",
            "password": "123456",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["data"]["username"] == "Tom"

    login_response = client.post(
        "/api/auth/login",
        json={"username": "Tom", "password": "123456"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["token"]

    profile_response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["data"]["email"] == "tom@example.com"


def test_duplicate_user_and_wrong_password_return_standard_error(
    client: TestClient,
) -> None:
    payload = {
        "username": "Tom",
        "email": "tom@example.com",
        "password": "123456",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201

    duplicate = client.post("/api/auth/register", json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json() == {
        "code": 409,
        "message": "用户名已被使用",
        "data": None,
    }

    wrong_password = client.post(
        "/api/auth/login", json={"username": "Tom", "password": "wrong"}
    )
    assert wrong_password.status_code == 401
    assert wrong_password.json()["code"] == 401


def test_validation_error_uses_api_envelope(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"username": "T", "email": "invalid", "password": "1"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == 422
    assert body["message"] == "请求参数校验失败"
    assert isinstance(body["data"], list)

