# AGENTS.md

Project rules for future work on `fastmile-api`.

## Goal

Build a small, professional FastAPI service that:

- reads Nokia FastMile router status pages
- keeps one in-memory source-of-truth snapshot
- serves JSON for Home Assistant
- serves `/metrics` for Prometheus
- stays easy to containerize and extend

## Core architecture

- Router scrape is the only source of raw truth.
- Cache stores the latest parsed snapshot in memory.
- `GET /api/v1/current` renders JSON from cache.
- `GET /metrics` renders Prometheus text from the same cache.
- No database in MVP.
- Prometheus pulls metrics; the service does not push.

## Implementation constraints

- Prefer minimal, focused files.
- Reuse the FastMileScraper parsing approach where practical.
- Keep router I/O behind a single client/service boundary.
- Avoid duplicate router fetches with a single-flight lock.
- Prefer explicit configuration via environment variables.
- Use ASCII only unless a file already contains Unicode.

## Likely environment variables

- `FASTMILE_ROUTER_HOST`
- `FASTMILE_ROUTER_USERNAME`
- `FASTMILE_ROUTER_PASSWORD`
- `FASTMILE_ROUTER_TIMEOUT_SECONDS`
- `FASTMILE_CACHE_TTL_SECONDS`
- `FASTMILE_CACHE_STALE_SECONDS`
- `FASTMILE_LOG_LEVEL`

## Public API shape

- `GET /health`
- `GET /api/v1/current`
- `GET /metrics`

## HA integration strategy

- Use Home Assistant `REST sensor` against `/api/v1/current` for the MVP.
- Only promote a custom integration later if the project outgrows REST sensors.

## Quality bar

- add tests for cache behavior, parsing, and output formatting
- keep the API documented
- keep Docker build simple and reproducible
