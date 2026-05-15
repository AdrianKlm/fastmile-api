# FastMileApi Design

**Goal:** Build a Dockerized FastAPI microservice that reads Nokia FastMile router status data, keeps a single in-memory snapshot, and exposes clean JSON plus Prometheus metrics.

**Architecture:** The service scrapes `status.php` on demand, parses the page into a normalized raw snapshot, and stores that snapshot in memory with a TTL. Both public outputs are derived from the same cached snapshot: JSON for Home Assistant and Prometheus text format for Grafana/Prometheus. A single-flight lock prevents duplicate router fetches when multiple requests arrive at once.

**Tech Stack:** Python, FastAPI, Uvicorn, Prometheus client library, Docker, pytest.

---

## Scope

### In scope

- router scrape from `https://<router>/status.php`
- in-memory cache with TTL and stale grace
- JSON endpoint for current status
- Prometheus metrics endpoint
- health endpoint
- Dockerized deployment
- documentation for Home Assistant REST sensor usage

### Out of scope

- database persistence
- historical storage inside the app
- custom Home Assistant integration
- login-protected router actions
- band lock / APN edits / reboot control

## Data model

The service should normalize router data into a raw snapshot containing:

- device info
- APNs and IPs
- traffic counters
- carrier aggregation state
- active cell signal data
- available cell measurements when present

The raw snapshot is the source of truth for all other responses.

## Cache behavior

- Cache stores one raw snapshot.
- Requests read from cache when it is fresh.
- If cache is stale or empty, the next request refreshes it.
- Concurrent refreshes must collapse into one router fetch.
- If refresh fails but a stale snapshot exists, serve stale data within the grace window.

## API surface

- `GET /health` returns service health and cache state.
- `GET /api/v1/current` returns the normalized snapshot as JSON.
- `GET /metrics` returns Prometheus metrics derived from the snapshot.

## Prometheus mapping

Expose numeric metrics for:

- signal quality: `rsrp`, `rsrq`, `rssi`, `sinr`
- cell data: `pci`, `earfcn`
- traffic counters: bytes or gigabytes as gauges/counters
- online state: `up` / `down`

Prefer stable metric names and labels over verbose payloads.

## Home Assistant integration

For MVP, Home Assistant should consume `/api/v1/current` via `REST sensor` or template sensors. This keeps the project simple while still supporting notifications and automations.

## Observability

- structured logs for router fetch success/failure
- `/health` for container checks
- Prometheus scrape endpoint for metrics
