from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import monotonic
from typing import Callable, Generic, TypeVar


T = TypeVar("T")


@dataclass(slots=True)
class CacheEntry(Generic[T]):
    snapshot: T
    fetched_at: float


class SnapshotCache(Generic[T]):
    def __init__(self, ttl_seconds: int, stale_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self.stale_seconds = stale_seconds
        self._entry: CacheEntry[T] | None = None
        self._lock = Lock()

    def _make_entry(self, snapshot: T, fetched_at: float | None = None) -> CacheEntry[T]:
        return CacheEntry(snapshot=snapshot, fetched_at=monotonic() if fetched_at is None else fetched_at)

    def _is_fresh(self, entry: CacheEntry[T]) -> bool:
        return (monotonic() - entry.fetched_at) <= self.ttl_seconds

    def _is_within_stale_window(self, entry: CacheEntry[T]) -> bool:
        return (monotonic() - entry.fetched_at) <= (self.ttl_seconds + self.stale_seconds)

    def has_entry(self) -> bool:
        return self._entry is not None

    def is_fresh(self) -> bool:
        entry = self._entry
        return entry is not None and self._is_fresh(entry)

    def is_stale(self) -> bool:
        entry = self._entry
        return entry is not None and not self._is_fresh(entry) and self._is_within_stale_window(entry)

    def get_or_refresh(self, loader: Callable[[], T]) -> T:
        entry = self._entry
        if entry is not None and self._is_fresh(entry):
            return entry.snapshot

        with self._lock:
            entry = self._entry
            if entry is not None and self._is_fresh(entry):
                return entry.snapshot

            try:
                snapshot = loader()
            except Exception:
                if entry is not None and self._is_within_stale_window(entry):
                    return entry.snapshot
                raise

            self._entry = self._make_entry(snapshot)
            return snapshot
