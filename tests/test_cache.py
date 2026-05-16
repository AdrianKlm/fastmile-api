from fastmile_api import cache as cache_module
from fastmile_api.cache import SnapshotCache


def test_snapshot_cache_returns_stale_snapshot_when_refresh_fails():
    cache = SnapshotCache(ttl_seconds=10, stale_seconds=5)
    cache._entry = cache._make_entry({"value": "stale"}, fetched_at=100.0)

    original_monotonic = cache_module.monotonic
    cache_module.monotonic = lambda: 112.0

    def loader():
        raise RuntimeError("router down")

    try:
        assert cache.get_or_refresh(loader) == {"value": "stale"}
    finally:
        cache_module.monotonic = original_monotonic
