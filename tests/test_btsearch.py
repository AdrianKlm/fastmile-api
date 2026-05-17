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
            "cells": [{"enbid": 291067, "clid": 99, "band_id": 4}],
        },
        {
            "station_id": "right",
            "cells": [{"enbid": 291067, "clid": 13, "band_id": 4}],
        },
    ]

    matches = client._filter_exact_matches(stations, 291067, 13, 4)

    assert len(matches) == 1
    assert matches[0]["station_id"] == "right"
    assert matches[0]["cells"] == [{"enbid": 291067, "clid": 13, "band_id": 4}]


def test_btsearch_maps_router_band_to_btsearch_band_value():
    client = BTSearchClient("https://btsearch.pl/api/v1")

    assert client._btsearch_band_value(20) == 800
    client._band_id_by_value = {800: 4}
    assert client._btsearch_band_id(20) == 4
