from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse

from fastmile_api.config import Settings
from fastmile_api.service import FastMileService


app = FastAPI(title="FastMileApi")


def get_settings() -> Settings:
    return Settings()


def get_service(settings: Settings = Depends(get_settings)) -> FastMileService:
    return FastMileService(settings)


@app.get("/health")
def health(service: FastMileService = Depends(get_service)):
    return service.health()


@app.get("/api/v1/current")
def current(service: FastMileService = Depends(get_service)):
    return service.current_payload()


@app.get("/api/v1/ha")
def home_assistant(service: FastMileService = Depends(get_service)):
    return service.ha_payload()


@app.get("/metrics", response_class=PlainTextResponse)
def metrics(service: FastMileService = Depends(get_service)):
    return service.render_metrics()
