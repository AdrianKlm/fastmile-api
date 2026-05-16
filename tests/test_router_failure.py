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


def test_current_endpoint_reuses_cached_snapshot(monkeypatch):
    calls = {"count": 0}

    def fake_fetch(self):
        calls["count"] += 1
        return """
        <html>
          <div id="model-value">ODU - Multiband - 4G05-B</div>
          <div id="software-version-val">FASTMILE2_D020110B83T0101M01E0153S</div>
          <div id="sn-value">FSH22010081D</div>
          <div id="imei-value">356088101152952</div>
          <div id="imsi-name-value">260032773115333</div>
          <div id="eth-mac-value">AA:BB:CC:DD:EE:FF</div>
          <div id="lockStatus-name-value">Normal</div>
          <div id="attached-cell-val">eNBID: <span>291067</span> Cell ID: <span>53</span> Band: <span>3</span></div>
          <div id="bandDL-val">B1</div>
          <div id="bandUL-val">CA Not Available</div>
          <!-- Primary Cell information card -->
          <div class="card-sevencol-grid">
            <div class="name-of-value-in-card-bold">131</div>
            <div class="name-of-value-in-card-bold">1725</div>
            <div class="name-of-value-in-card-bold">CellPrimary</div>
            <div class="name-of-value-in-card-bold">-106</div>
            <div class="name-of-value-in-card-bold">-13</div>
            <div class="name-of-value-in-card-bold">-74</div>
            <div class="name-of-value-in-card-bold">6</div>
          </div>
          <!-- LTE stats -->
          <div class="LTE"><div class="bytes">1.5 GB</div><div class="bytes">256 MB</div></div>
          <div class="Ethernet"><div class="bytes">256 MB</div><div class="bytes">1.5 GB</div></div>
          <!-- APNs card -->
          <div class="apns-section">
            <div></div><div></div>
            <div>internet</div><div>10.0.0.2</div><div>::</div>
          </div>
        </html>
        """

    monkeypatch.setattr(RouterClient, "fetch_status_html", fake_fetch)
    app.dependency_overrides.clear()

    client = TestClient(app)
    first = client.get("/api/v1/current")
    second = client.get("/api/v1/current")

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["count"] == 1
