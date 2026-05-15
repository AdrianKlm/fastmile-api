# fastmile-api

API and metrics exporter for Nokia FastMile / 4G05 routers.

## MVP

- poll `https://<router>/status.php`
- cache one raw snapshot in memory
- expose JSON for Home Assistant
- expose flat JSON for Home Assistant (`/api/v1/ha`)
- expose Prometheus metrics for Grafana
- ship as a small Dockerized service

## Docs

- `AGENTS.md` - working rules for future code generation
- `docs/superpowers/specs/2026-05-15-fastmile-api-design.md`
- `docs/superpowers/plans/2026-05-15-fastmile-api.md`

## Docker

Build:

```bash
docker build -t fastmile-api .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e FASTMILE_ROUTER_HOST=192.168.0.1 \
  -e FASTMILE_CACHE_TTL_SECONDS=15 \
  fastmile-api
```
