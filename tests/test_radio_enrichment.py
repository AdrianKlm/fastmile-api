from types import SimpleNamespace

from fastmile_api.config import Settings
from fastmile_api.service import FastMileService


def test_radio_enrichment_payload_uses_router_lte_identifiers(monkeypatch):
    service = FastMileService(Settings())
    snapshot = SimpleNamespace(
        lte=SimpleNamespace(
            ca=SimpleNamespace(enb=291067, cid=13, dl_bands=[20, 3]),
            active=[],
        )
    )

    monkeypatch.setattr(service, "get_current_snapshot", lambda: snapshot)

    calls = {}

    def fake_search(enbid, cell_id, band):
        calls["args"] = (enbid, cell_id, band)
        return [{"station_id": "BTS-1", "cells": [{"enbid": enbid, "clid": cell_id, "band_id": 4}]}]

    monkeypatch.setattr(service.btsearch, "search_lte_station_matches", fake_search)
    service.btsearch._bands_by_value = {800: [{"id": 4, "duplex": "FDD", "name": "LTE 800 (FDD)"}]}

    payload = service.radio_enrichment_payload()

    assert calls["args"] == (291067, 13, 20)
    assert payload["source"] == {"enbid": 291067, "cell_id": 13, "band": 20, "band_value": 800, "band_id": 4}
    assert payload["match_count"] == 1
    assert payload["matches"] == [{"station_id": "BTS-1", "cells": [{"enbid": 291067, "clid": 13, "band_id": 4}]}]
