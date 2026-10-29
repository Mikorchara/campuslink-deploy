from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.frontend import SPAStaticFiles


def test_production_spa_routes_do_not_hide_missing_api_or_assets(tmp_path):
    (tmp_path / 'index.html').write_text('<html><body>CampusLink</body></html>', encoding='utf-8')
    (tmp_path / 'app.js').write_text('console.log("ok")', encoding='utf-8')
    app = FastAPI()
    app.mount('/', SPAStaticFiles(directory=tmp_path, html=True))
    with TestClient(app) as browser:
        for path in ['/', '/idle', '/product/123', '/my-products']:
            assert browser.get(path).status_code == 200
            assert 'CampusLink' in browser.get(path).text
        assert browser.get('/app.js').status_code == 200
        assert browser.get('/api/not-real').status_code == 404
        assert browser.get('/missing.js').status_code == 404
