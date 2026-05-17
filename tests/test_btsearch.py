from fastmile_api.btsearch import BTSearchClient


def test_btsearch_builds_lte_query_from_router_identifiers():
    client = BTSearchClient("https://btsearch.pl/api/v1")

    queries = client._build_queries(291067, 13, 20)

    assert queries[0] == "lteCells: enbid: 291067 lteCells: lte_clid: 13 cells: band: 20"
    assert "lteCells: enbid: 291067 cells: band: 20" in queries
    assert "lteCells: enbid: 291067" in queries
