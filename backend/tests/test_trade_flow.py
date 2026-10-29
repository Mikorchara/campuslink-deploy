from fastapi.testclient import TestClient

from tests.conftest import register_and_login
from tests.test_products import create_product


def test_favorite_contact_and_transaction_flow(
    client: TestClient, auth_header: dict[str, str]
) -> None:
    product = create_product(client, auth_header)
    buyer_token = register_and_login(client, "buyer", "buyer@example.com")
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

    favorite = client.post(
        f"/api/products/{product['id']}/favorite", headers=buyer_headers
    )
    assert favorite.status_code == 201
    assert favorite.json()["data"]["is_favorited"] is True

    favorite_list = client.get("/api/favorites", headers=buyer_headers)
    assert favorite_list.status_code == 200
    assert favorite_list.json()["data"][0]["product"]["id"] == product["id"]

    contact = client.get(
        f"/api/products/{product['id']}/contact", headers=buyer_headers
    )
    assert contact.status_code == 200
    assert contact.json()["data"]["email"] == "seller@example.com"

    transaction = client.post(
        f"/api/products/{product['id']}/transactions",
        headers=buyer_headers,
        json={"note": "今晚图书馆面交"},
    )
    assert transaction.status_code == 201
    transaction_id = transaction.json()["data"]["id"]

    accepted = client.patch(
        f"/api/transactions/{transaction_id}",
        headers=auth_header,
        json={"status": "ACCEPTED"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["data"]["status"] == "ACCEPTED"

    detail = client.get(f"/api/products/{product['id']}")
    assert detail.json()["data"]["status"] == "RESERVED"


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok", "database": "connected"}

