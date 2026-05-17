from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests


LTE_BAND_VALUE_BY_NUMBER: dict[int, int] = {
    1: 2100,
    2: 1900,
    3: 1800,
    4: 1700,
    5: 850,
    7: 2600,
    8: 900,
    12: 700,
    13: 700,
    14: 700,
    17: 700,
    18: 850,
    19: 850,
    20: 800,
    25: 1900,
    26: 850,
    28: 700,
    29: 700,
    30: 2300,
    31: 450,
    32: 1500,
    38: 2600,
    39: 1900,
    40: 2300,
    41: 2500,
    42: 3500,
    43: 3700,
    46: 5200,
    48: 3500,
    66: 1700,
    71: 600,
}


class BTSearchClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._band_id_by_value: dict[int, int] | None = None

    def search_lte_station_matches(self, enbid: int, cell_id: int, band: int | None = None) -> list[dict[str, Any]]:
        # BTSearch search is broad; exact matching happens after the response comes back.
        matches = self._search(f"enbid: {enbid}")
        return self._filter_exact_matches(matches, enbid, cell_id, self._btsearch_band_id(band))

    def _build_queries(self, enbid: int, cell_id: int, band: int | None) -> list[str]:
        queries: list[str] = [f"lteCells: enbid: {enbid}"]
        if band is not None:
            queries.append(f"lteCells: enbid: {enbid} cells: band: {band}")
        return self._dedupe(queries)

    def _dedupe(self, queries: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for query in queries:
            normalized = query.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    def _search(self, query: str) -> list[dict[str, Any]]:
        response = requests.post(
            f"{self.base_url}/search",
            json={"query": query},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ValueError("invalid BTSearch response")
        return data

    def _filter_exact_matches(
        self,
        stations: list[dict[str, Any]],
        enbid: int,
        cell_id: int,
        band_id: int | None,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []

        for station in stations:
            cells = station.get("cells")
            if not isinstance(cells, list):
                continue

            exact_cells = []
            for cell in cells:
                if not isinstance(cell, dict):
                    continue
                cell_enbid = cell.get("enbid")
                cell_clid = cell.get("clid")
                if cell_enbid != enbid or cell_clid != cell_id:
                    continue
                if band_id is not None and self._cell_band_id(cell) not in {None, band_id}:
                    continue
                exact_cells.append(cell)

            if exact_cells:
                filtered_station = dict(station)
                filtered_station["cells"] = exact_cells
                matches.append(filtered_station)

        return matches

    def _cell_band_id(self, cell: dict[str, Any]) -> int | None:
        band_id = cell.get("band_id")
        if isinstance(band_id, int):
            return band_id
        return None

    def _btsearch_band_value(self, router_band: int | None) -> int | None:
        if router_band is None:
            return None
        return LTE_BAND_VALUE_BY_NUMBER.get(router_band)

    def _btsearch_band_id(self, router_band: int | None) -> int | None:
        band_value = self._btsearch_band_value(router_band)
        if band_value is None:
            return None
        return self._load_band_id_by_value().get(band_value)

    def _load_band_id_by_value(self) -> dict[int, int]:
        if self._band_id_by_value is None:
            response = requests.get(f"{self.base_url}/bands", timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", [])
            if not isinstance(data, list):
                raise ValueError("invalid BTSearch bands response")
            band_ids: dict[int, int] = {}
            for band in data:
                if not isinstance(band, dict):
                    continue
                value = band.get("value")
                band_id = band.get("id")
                if isinstance(value, int) and isinstance(band_id, int):
                    band_ids[value] = band_id
            self._band_id_by_value = band_ids
        return self._band_id_by_value
