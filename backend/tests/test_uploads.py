from io import BytesIO

from PIL import Image

from src.config.settings import settings


def image_bytes():
    output = BytesIO()
    Image.new("RGB", (24, 24), "green").save(output, "PNG")
    return output.getvalue()


def test_uploaded_cover_survives_product_reload(client, auth_header, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "images"))
    response = client.post("/api/uploads", headers=auth_header,
                           files={"file": ("../original.png", image_bytes(), "image/png")})
    assert response.status_code == 201
    url = response.json()["data"]["image_url"]
    assert url.startswith("/api/uploads/") and url.endswith(".webp")
    saved = client.get(url)
    assert saved.status_code == 200
    assert saved.headers["content-type"] == "image/webp"
    assert saved.content != image_bytes()
    product = client.post("/api/products", headers=auth_header, json={
        "title": "封面测试", "price": 12.50, "category": "教材", "image_url": url,
    }).json()["data"]
    assert client.get(f"/api/products/{product['id']}").json()["data"]["image_url"] == url
    assert len(list((tmp_path / "images").iterdir())) == 1


def test_upload_requires_login_and_valid_image(client, auth_header, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "images"))
    assert client.post("/api/uploads", files={"file": ("x.png", image_bytes())}).status_code == 401
    for content in (b"", b"<svg><script>alert(1)</script></svg>", b"x" * (5 * 1024 * 1024 + 1)):
        assert client.post("/api/uploads", headers=auth_header,
                           files={"file": ("fake.png", content, "image/png")}).status_code == 422
    assert not (tmp_path / "images").exists()
    assert client.get("/api/uploads/not-a-valid-name.webp").status_code == 404
