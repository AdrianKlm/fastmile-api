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


def test_snapshot_cache_reports_fresh_stale_and_expired_states():
    cache = SnapshotCache(ttl_seconds=10, stale_seconds=5)
    cache._entry = cache._make_entry({"value": "cached"}, fetched_at=100.0)

    original_monotonic = cache_module.monotonic
    try:
        cache_module.monotonic = lambda: 104.0
        assert cache.has_entry() is True
        assert cache.is_fresh() is True
        assert cache.is_stale() is False

        cache_module.monotonic = lambda: 112.0
        assert cache.is_fresh() is False
        assert cache.is_stale() is True

        cache_module.monotonic = lambda: 117.0
        assert cache.is_fresh() is False
        assert cache.is_stale() is False
    finally:
        cache_module.monotonic = original_monotonic
