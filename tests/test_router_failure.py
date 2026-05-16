from fastapi.testclient import TestClient

from fastmile_api.main import app
from fastmile_parser.router_client import RouterClient


def test_current_endpoint_returns_503_when_router_is_down(monkeypatch):
    def boom(self):
        raise ConnectionError("router down")

    monkeypatch.setattr(RouterClient, "fetch_status_html", boom)
    app.dependency_overrides.clear()

    client = TestClient(app)
    response = client.get("/api/v1/current")

    assert response.status_code == 503
    assert response.json()["detail"] == "router unavailable"
