from fastapi.testclient import TestClient

from app.main import app, _serialized_catalog


def test_catalog_compression_etag_and_locale_isolation():
    with TestClient(app) as client:
        english = client.get("/api/data/all?locale=en", headers={"Accept-Encoding": "gzip"})
        assert english.status_code == 200
        assert english.headers["content-encoding"] == "gzip"
        assert english.json()["locale"] == "en"
        assert english.json()["artian_rules"]["element_rolls"]["Great Sword"] == [80, 90, 110]
        cached = client.get("/api/data/all?locale=en", headers={"If-None-Match": english.headers["etag"]})
        assert cached.status_code == 304
        assert not cached.content
        portuguese = client.get("/api/data/all?locale=pt", headers={"If-None-Match": english.headers["etag"]})
        assert portuguese.status_code == 200
        assert portuguese.json()["locale"] == "pt"
        assert portuguese.headers["etag"] != english.headers["etag"]
        assert _serialized_catalog.cache_info().hits > 0


def test_frontend_assets_are_revalidated_after_updates():
    with TestClient(app) as client:
        for path in ["/", "/static/js/app.js", "/static/js/planner.js", "/static/css/app.css"]:
            response = client.get(path)
            assert response.status_code == 200
            assert response.headers["cache-control"] == "no-cache"
