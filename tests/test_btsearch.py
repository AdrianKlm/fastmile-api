from fastmile_api.btsearch import BTSearchClient


def test_btsearch_builds_lte_query_from_router_identifiers():
    client = BTSearchClient("https://btsearch.pl/api/v1")

    queries = client._build_queries(291067, 13, 20)

    assert queries[0] == "lteCells: enbid: 291067"
    assert "lteCells: enbid: 291067 cells: band: 20" in queries


def test_btsearch_filters_exact_lte_matches():
    client = BTSearchClient("https://btsearch.pl/api/v1")

    stations = [
        {
            "station_id": "wrong",
            "cells": [{"enbid": 291067, "clid": 99, "band": {"value": 20}}],
        },
        {
            "station_id": "right",
            "cells": [{"enbid": 291067, "clid": 13, "band": {"value": 20}}],
        },
    ]

    matches = client._filter_exact_matches(stations, 291067, 13, 20)

    assert len(matches) == 1
    assert matches[0]["station_id"] == "right"
    assert matches[0]["cells"] == [{"enbid": 291067, "clid": 13, "band": {"value": 20}}]
