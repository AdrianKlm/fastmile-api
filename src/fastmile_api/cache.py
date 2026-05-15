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

    def _is_fresh(self, entry: CacheEntry[T]) -> bool:
        return (monotonic() - entry.fetched_at) <= self.ttl_seconds

    def get_or_refresh(self, loader: Callable[[], T]) -> T:
        entry = self._entry
        if entry is not None and self._is_fresh(entry):
            return entry.snapshot

        with self._lock:
            entry = self._entry
            if entry is not None and self._is_fresh(entry):
                return entry.snapshot

            snapshot = loader()
            self._entry = CacheEntry(snapshot=snapshot, fetched_at=monotonic())
            return snapshot
