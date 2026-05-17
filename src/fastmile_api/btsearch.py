from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests


class BTSearchClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def search_lte_station_matches(self, enbid: int, cell_id: int, band: int | None = None) -> list[dict[str, Any]]:
        # BTSearch search is broad; exact matching happens after the response comes back.
        matches = self._search(f"lteCells: enbid: {enbid}")
        return self._filter_exact_matches(matches, enbid, cell_id, band)

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
        band: int | None,
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
                if band is not None and self._cell_band(cell) not in {None, band}:
                    continue
                exact_cells.append(cell)

            if exact_cells:
                filtered_station = dict(station)
                filtered_station["cells"] = exact_cells
                matches.append(filtered_station)

        return matches

    def _cell_band(self, cell: dict[str, Any]) -> int | None:
        band = cell.get("band")
        if isinstance(band, dict):
            value = band.get("value")
            if isinstance(value, int):
                return value
        return None
