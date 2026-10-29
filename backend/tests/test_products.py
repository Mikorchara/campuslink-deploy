from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def create_product(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "title": "高等数学教材",
            "description": "九成新",
            "price": 20,
            "category": "教材",
            "image_url": "/assets/images/goods_math_book.png",
            "location": "图书馆",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_product_crud_matches_frontend_contract(
    client: TestClient, auth_header: dict[str, str]
) -> None:
    product = create_product(client, auth_header)
    assert product["seller"]["name"] == "seller"
    assert product["status"] == "AVAILABLE"
    assert isinstance(product["time_ago"], str)
    assert product["price"] == 20.0

    listing = client.get("/api/products?category=教材&keyword=数学")
    assert listing.status_code == 200
    assert len(listing.json()["data"]) == 1

    detail = client.get(f"/api/products/{product['id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["location"] == "图书馆"

    updated = client.put(
        f"/api/products/{product['id']}",
        headers=auth_header,
        json={"price": 18.5},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["price"] == 18.5

    status_response = client.patch(
        f"/api/products/{product['id']}/status",
        headers=auth_header,
        json={"status": "RESERVED"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["data"]["status"] == "RESERVED"

    deleted = client.delete(
        f"/api/products/{product['id']}", headers=auth_header
    )
    assert deleted.status_code == 200
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_product_write_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/products",
        json={"title": "教材", "price": 10, "category": "教材"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == 401


def test_only_owner_can_update_product(
    client: TestClient, auth_header: dict[str, str]
) -> None:
    product = create_product(client, auth_header)
    other_token = register_and_login(client, "buyer", "buyer@example.com")
    response = client.put(
        f"/api/products/{product['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"price": 1},
    )
    assert response.status_code == 403

