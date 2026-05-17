from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests


class BTSearchClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def search_lte_station_matches(self, enbid: int, cell_id: int, band: int | None = None) -> list[dict[str, Any]]:
        for query in self._build_queries(enbid, cell_id, band):
            matches = self._search(query)
            if matches:
                return matches
        return []

    def _build_queries(self, enbid: int, cell_id: int, band: int | None) -> list[str]:
        queries: list[str] = []

        strict_parts = [f"lteCells: enbid: {enbid}", f"lteCells: lte_clid: {cell_id}"]
        if band is not None:
            strict_parts.append(f"cells: band: {band}")
        queries.append(" ".join(strict_parts))

        if band is not None:
            queries.append(f"lteCells: enbid: {enbid} cells: band: {band}")

        queries.append(f"lteCells: enbid: {enbid}")
        queries.append(" ".join(str(value) for value in (enbid, cell_id, band) if value is not None))

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
