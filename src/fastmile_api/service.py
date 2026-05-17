from __future__ import annotations

from dataclasses import asdict

from fastapi import HTTPException

from fastmile_api.btsearch import BTSearchClient
from fastmile_api.cache import SnapshotCache
from fastmile_api.config import Settings
from fastmile_api.metrics import render_metrics
from fastmile_parser.router_client import RouterClient
from fastmile_parser.scraper import parse_snapshot
from requests import RequestException


class FastMileService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = RouterClient(settings.router_host, timeout=settings.router_timeout_seconds)
        self.cache = SnapshotCache(ttl_seconds=settings.cache_ttl_seconds, stale_seconds=settings.cache_stale_seconds)
        self.btsearch = BTSearchClient(settings.btsearch_base_url, timeout_seconds=settings.btsearch_timeout_seconds)

    def get_current_snapshot(self):
        return self.cache.get_or_refresh(self._load_snapshot)

    def _load_snapshot(self):
        try:
            html = self.client.fetch_status_html()
        except (RequestException, OSError) as exc:
            raise HTTPException(status_code=503, detail="router unavailable") from exc
        return parse_snapshot(html)

    def health(self) -> dict:
        return {
            "status": "ok",
            "cache": {
                "fresh": self.cache.is_fresh(),
                "stale": self.cache.is_stale(),
                "has_entry": self.cache.has_entry(),
            },
        }

    def current_payload(self) -> dict:
        return asdict(self.get_current_snapshot())

    def ha_payload(self) -> dict:
        snapshot = self.get_current_snapshot()
        primary = snapshot.lte.active[0] if snapshot.lte.active else None
        apn = snapshot.apns[0] if snapshot.apns else None
        return {
            "device_model": snapshot.device.model,
            "software_version": snapshot.device.software_version,
            "serial_number": snapshot.device.serial_number,
            "imei": snapshot.device.imei,
            "imsi": snapshot.device.imsi,
            "mac": snapshot.device.mac,
            "lock_status": snapshot.device.lock_status,
            "online": True,
            "signal_pci": primary.pci if primary is not None else None,
            "signal_earfcn": primary.earfcn if primary is not None else None,
            "signal_type": primary.cell_type if primary is not None else None,
            "signal_rsrp": primary.rsrp if primary is not None else None,
            "signal_rsrq": primary.rsrq if primary is not None else None,
            "signal_rssi": primary.rssi if primary is not None else None,
            "signal_sinr": primary.sinr if primary is not None else None,
            "traffic_eth_download_gb": snapshot.data.eth.download.val_gb,
            "traffic_eth_upload_gb": snapshot.data.eth.upload.val_gb,
            "traffic_lte_download_gb": snapshot.data.lte.download.val_gb,
            "traffic_lte_upload_gb": snapshot.data.lte.upload.val_gb,
            "ca_enb": snapshot.lte.ca.enb,
            "ca_cid": snapshot.lte.ca.cid,
            "ca_dl_bands": snapshot.lte.ca.dl_bands,
            "ca_ul_bands": snapshot.lte.ca.ul_bands,
            "apn_name": apn.name if apn is not None else None,
            "apn_ipv4": apn.ipv4 if apn is not None else None,
            "apn_ipv6": apn.ipv6 if apn is not None else None,
        }

    def radio_enrichment_payload(self) -> dict:
        snapshot = self.get_current_snapshot()
        band = snapshot.lte.ca.dl_bands[0] if snapshot.lte.ca.dl_bands else None
        try:
            matches = self.btsearch.search_lte_station_matches(snapshot.lte.ca.enb, snapshot.lte.ca.cid, band)
        except (RequestException, OSError, ValueError) as exc:
            raise HTTPException(status_code=502, detail="btsearch unavailable") from exc

        return {
            "source": {
                "enbid": snapshot.lte.ca.enb,
                "cell_id": snapshot.lte.ca.cid,
                "band": band,
            },
            "matches": matches,
            "match_count": len(matches),
        }

    def render_metrics(self) -> str:
        return render_metrics(self.get_current_snapshot())
