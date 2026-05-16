# fastmile-api PyPI Docker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `fastmile-api` consume `fastmile-parser` from PyPI everywhere and rebuild the container cleanly on port `8002`.

**Architecture:** The API package keeps owning HTTP, cache, health, and metrics. The parser becomes an external dependency resolved from PyPI during local installs and image builds, so the Docker image no longer needs the sibling parser repo in its build context.

**Tech Stack:** Python, FastAPI, setuptools, Docker, pip, uvicorn.

---

### Task 1: Switch API docs and package flow to PyPI

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`

- [ ] **Step 1: Update the local install instructions**

```bash
python3 -m venv .venv
.venv/bin/pip install -e .[dev]
```

- [ ] **Step 2: Remove the sibling-repo parser install from the docs**

```bash
sed -n '1,80p' README.md
```

- [ ] **Step 3: Keep `fastmile-parser>=0.1.0` in the project dependencies**

```toml
[project]
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "pydantic-settings>=2.6",
  "prometheus-client>=0.20",
  "fastmile-parser>=0.1.0",
]
```

- [ ] **Step 4: Run the API tests through the venv Python**

```bash
./.venv/bin/python -m pytest
```

Expected: all tests pass.

### Task 2: Rebuild the Docker image from PyPI

**Files:**
- Modify: `Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Remove the parser repo copy from the image build**

```dockerfile
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY fastmile-api/pyproject.toml fastmile-api/README.md ./fastmile-api/
COPY fastmile-api/src ./fastmile-api/src

RUN pip install --no-cache-dir -e ./fastmile-api

EXPOSE 8000

CMD ["sh", "-c", "uvicorn fastmile_api.main:app --host 0.0.0.0 --port 8000"]
```

- [ ] **Step 2: Keep compose pointing at the API Dockerfile**

```yaml
services:
  fastmile-api:
    build:
      context: ..
      dockerfile: fastmile-api/Dockerfile
    ports:
      - "8002:8000"
```

- [ ] **Step 3: Build the image from the repo root context**

```bash
docker build -t fastmile-api -f fastmile-api/Dockerfile ..
```

Expected: image builds without needing `fastmile-parser` in the build context.

- [ ] **Step 4: Run the container on port 8002**

```bash
docker run --rm -p 8002:8000 \
  -e FASTMILE_ROUTER_HOST=192.168.0.1 \
  -e FASTMILE_CACHE_TTL_SECONDS=15 \
  fastmile-api
```

Expected: `GET http://localhost:8002/health` responds successfully.
