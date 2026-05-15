from fastapi.testclient import TestClient

from fastmile_api.main import app, get_service


class FakeService:
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def get_current_snapshot(self):
        return self._snapshot

    def current_payload(self):
        return {"device": {"model": self._snapshot.device.model}, "apns": self._snapshot.apns}

    def ha_payload(self):
        return {
            "device_model": self._snapshot.device.model,
            "signal_rsrp": -106,
            "signal_rsrq": -13,
            "signal_rssi": -74,
            "signal_sinr": 6,
            "traffic_lte_download_gb": 1.5,
            "traffic_lte_upload_gb": 0.256,
            "online": True,
        }

    def render_metrics(self):
        return "fastmile_router_up 1\nfastmile_router_signal_rsrp -106\n"

    def health(self):
        return {"status": "ok", "cache": {"fresh": True}}


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_current_endpoint_returns_snapshot_json():
    from types import SimpleNamespace

    snapshot = SimpleNamespace(device=SimpleNamespace(model="ODU"), apns=[])
    app.dependency_overrides.clear()
    app.dependency_overrides[get_service] = lambda: FakeService(snapshot)
    client = TestClient(app)

    response = client.get("/api/v1/current")
    assert response.status_code == 200
    assert response.json()["device"]["model"] == "ODU"


def test_metrics_endpoint_returns_prometheus_text():
    from types import SimpleNamespace

    snapshot = SimpleNamespace(device=SimpleNamespace(model="ODU"), apns=[])
    app.dependency_overrides.clear()
    app.dependency_overrides[get_service] = lambda: FakeService(snapshot)
    client = TestClient(app)

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "fastmile_router_up 1" in response.text


def test_ha_endpoint_returns_flat_json():
    from types import SimpleNamespace

    snapshot = SimpleNamespace(device=SimpleNamespace(model="ODU"), apns=[])
    app.dependency_overrides.clear()
    app.dependency_overrides[get_service] = lambda: FakeService(snapshot)
    client = TestClient(app)

    response = client.get("/api/v1/ha")
    assert response.status_code == 200
    body = response.json()
    assert body["device_model"] == "ODU"
    assert body["signal_rsrp"] == -106
    assert body["online"] is True
    assert "device" not in body
