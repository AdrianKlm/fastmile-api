from threading import Thread

from fastmile_api.cache import SnapshotCache


def test_snapshot_cache_collapses_concurrent_refreshes():
    cache = SnapshotCache(ttl_seconds=60, stale_seconds=10)
    calls = {"count": 0}

    def loader():
        calls["count"] += 1
        return {"value": "fresh"}

    results: list[object] = []

    def worker():
        results.append(cache.get_or_refresh(loader))

    first = Thread(target=worker)
    second = Thread(target=worker)
    first.start()
    second.start()
    first.join()
    second.join()

    assert calls["count"] == 1
    assert results == [{"value": "fresh"}, {"value": "fresh"}]
