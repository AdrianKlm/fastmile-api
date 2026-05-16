# fastmile-api

API and metrics exporter for Nokia FastMile / 4G05 routers.

## MVP

- poll `https://<router>/status.php`
- cache one raw snapshot in memory
- expose full JSON snapshot (`/api/v1/current`)
- expose flat JSON for Home Assistant (`/api/v1/ha`)
- expose Prometheus metrics for Grafana
- ship as a small Dockerized service

## Workflow

This project is built for vibe coding with strong docs, clean contracts, and low-friction iteration.
The goal is to keep the codebase easy to read, easy to extend, and easy to automate.

## Workspace Setup

From `fastmile-api/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .[dev]
```

## Docker

Build:

```bash
docker build -t fastmile-api -f fastmile-api/Dockerfile ..
```

Run:

```bash
docker run --rm -p 8002:8000 \
  -e FASTMILE_ROUTER_HOST=192.168.0.1 \
  -e FASTMILE_CACHE_TTL_SECONDS=15 \
  fastmile-api
```

Or from `fastmile-api/`:

```bash
docker compose up --build
```

## Full JSON Shape

`GET /api/v1/current`

```json
{
  "device": {
    "model": "ODU - Multiband - 4G05-B",
    "software_version": "FASTMILE2_...",
    "serial_number": "FSH**********",
    "imei": "35*************",
    "imsi": "26*************",
    "mac": "AA:BB:CC:DD:EE:FF",
    "lock_status": "Normal"
  },
  "apns": [
    {
      "name": "internet.example.gprs",
      "ipv4": "10.0.0.2",
      "ipv6": null
    }
  ],
  "data": {
    "eth": {
      "download": { "val": 53.64, "unit": "GB", "val_gb": 53.64 },
      "upload": { "val": 2.09, "unit": "GB", "val_gb": 2.09 }
    },
    "lte": {
      "download": { "val": 2.1, "unit": "GB", "val_gb": 2.1 },
      "upload": { "val": 52.97, "unit": "GB", "val_gb": 52.97 }
    }
  },
  "lte": {
    "ca": {
      "enb": 291067,
      "cid": 53,
      "dl_bands": [3, 1],
      "ul_bands": [3]
    },
    "active": [
      {
        "pci": 131,
        "earfcn": 1725,
        "cell_type": "CellPrimary",
        "rsrp": -106,
        "rsrq": -13,
        "rssi": -74,
        "sinr": 6
      }
    ],
    "available": []
  }
}
```

`GET /api/v1/ha` is optimized for Home Assistant sensors.
