# FastMileApi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Dockerized FastAPI service that scrapes Nokia FastMile status data, caches one raw snapshot in memory, and exposes JSON plus Prometheus metrics.

**Architecture:** Implement a small core parser/client layer, then wrap it in a cache-aware service, then expose HTTP endpoints on top. Both JSON and metrics must render from the same cached raw snapshot so the router is only queried once per refresh cycle. Keep deployment simple with a single Docker image for now.

**Tech Stack:** Python, FastAPI, Uvicorn, requests/httpx, BeautifulSoup or existing FastMileScraper logic, prometheus-client, pytest, Docker.

---

### Task 1: Bootstrap project skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/fastmile_api/__init__.py`
- Create: `src/fastmile_api/main.py`
- Create: `src/fastmile_api/config.py`
- Create: `src/fastmile_api/models.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Write the failing test**

```python
from fastmile_api.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.router_host == "192.168.0.1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests -q`
Expected: import or attribute failure because the package does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    router_host: str = "192.168.0.1"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests -q`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src tests
git commit -m "feat: bootstrap fastmile-api skeleton"
```

### Task 2: Add router snapshot parser

**Files:**
- Create: `src/fastmile_api/router_client.py`
- Create: `src/fastmile_api/scraper.py`
- Create: `tests/test_scraper.py`

- [ ] **Step 1: Write the failing test**

```python
from fastmile_api.scraper import parse_snapshot


def test_parse_snapshot_extracts_signal_fields():
    html = "<div id='model-value'>M</div><div id='software-version-val'>1</div>"
    snapshot = parse_snapshot(html)
    assert snapshot.device.model == "M"
    assert snapshot.device.software_version == "1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scraper.py -q`
Expected: module/function not found.

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class DeviceInfo:
    model: str
    software_version: str


@dataclass
class Snapshot:
    device: DeviceInfo


def parse_snapshot(html: str) -> Snapshot:
    soup = BeautifulSoup(html, "html.parser")
    return Snapshot(
        device=DeviceInfo(
            model=soup.find(id="model-value").get_text(strip=True),
            software_version=soup.find(id="software-version-val").get_text(strip=True),
        )
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scraper.py -q`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add src/fastmile_api/scraper.py src/fastmile_api/router_client.py tests/test_scraper.py
git commit -m "feat: add router status parser"
```

### Task 3: Implement in-memory cache with single-flight refresh

**Files:**
- Create: `src/fastmile_api/cache.py`
- Create: `tests/test_cache.py`

- [ ] **Step 1: Write the failing test**

```python
from fastmile_api.cache import SnapshotCache


def test_cache_returns_stale_snapshot_until_refresh():
    cache = SnapshotCache(ttl_seconds=10, stale_seconds=5)
    assert cache.get() is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache.py -q`
Expected: module missing.

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass
class CacheEntry:
    snapshot: object
    fetched_at: float


class SnapshotCache:
    def __init__(self, ttl_seconds: int, stale_seconds: int):
        self.ttl_seconds = ttl_seconds
        self.stale_seconds = stale_seconds
        self._entry: CacheEntry | None = None
        self._lock = Lock()

    def get(self):
        return self._entry
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cache.py -q`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add src/fastmile_api/cache.py tests/test_cache.py
git commit -m "feat: add in-memory snapshot cache"
```

### Task 4: Expose JSON and metrics endpoints

**Files:**
- Modify: `src/fastmile_api/main.py`
- Create: `src/fastmile_api/api.py`
- Create: `src/fastmile_api/metrics.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from fastmile_api.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api.py -q`
Expected: app import or route missing.

- [ ] **Step 3: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_api.py -q`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add src/fastmile_api/main.py src/fastmile_api/api.py src/fastmile_api/metrics.py tests/test_api.py
git commit -m "feat: expose api and metrics endpoints"
```

### Task 5: Add Dockerfile and operational docs

**Files:**
- Create: `Dockerfile`
- Create: `docs/README.md`
- Create: `tests/test_deploy_files.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_repository_includes_docker_artifacts():
    assert Path("Dockerfile").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_deploy_files.py -q`
Expected: fail because `Dockerfile` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
```

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      FASTMILE_ROUTER_HOST: ${FASTMILE_ROUTER_HOST}
      FASTMILE_CACHE_TTL_SECONDS: ${FASTMILE_CACHE_TTL_SECONDS:-15}
```

- [ ] **Step 4: Run build smoke test**

Run: `docker build -t fastmile-api .`
Expected: Docker image builds successfully and the container can serve `/health` when started.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile docs/README.md
git commit -m "feat: add container deployment docs"
```
