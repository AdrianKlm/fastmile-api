from __future__ import annotations

from fastmile_parser.models import Snapshot


def _escape_label_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _format_labels(labels: dict[str, str] | None) -> str:
    if not labels:
        return ""
    parts = [f'{key}="{_escape_label_value(value)}"' for key, value in labels.items()]
    return "{" + ",".join(parts) + "}"


def _add_gauge(lines: list[str], name: str, value: object, labels: dict[str, str] | None = None, help_text: str | None = None) -> None:
    if help_text is not None:
        lines.append(f"# HELP {name} {help_text}")
    lines.append(f"# TYPE {name} gauge")
    lines.append(f"{name}{_format_labels(labels)} {value}")


def render_metrics(snapshot: Snapshot) -> str:
    primary = snapshot.lte.active[0] if snapshot.lte.active else None
    secondary_cells = snapshot.lte.active[1:] if len(snapshot.lte.active) > 1 else []
    lines: list[str] = []

    _add_gauge(lines, "fastmile_router_up", 1, help_text="Router scrape status")
    _add_gauge(
        lines,
        "fastmile_router_device_info",
        1,
        labels={
            "model": snapshot.device.model,
            "software_version": snapshot.device.software_version,
            "lock_status": snapshot.device.lock_status,
        },
        help_text="Static device identifiers and firmware metadata",
    )

    _add_gauge(lines, "fastmile_router_online", 1, help_text="Router online status")

    for interface_name, interface in (("eth", snapshot.data.eth), ("lte", snapshot.data.lte)):
        _add_gauge(
            lines,
            "fastmile_router_traffic_gb",
            interface.download.val_gb,
            labels={"interface": interface_name, "direction": "download"},
            help_text="Traffic usage in gigabytes",
        )
        _add_gauge(
            lines,
            "fastmile_router_traffic_gb",
            interface.upload.val_gb,
            labels={"interface": interface_name, "direction": "upload"},
        )

    _add_gauge(lines, "fastmile_router_ca_enb", snapshot.lte.ca.enb, help_text="Current eNodeB identifier")
    _add_gauge(lines, "fastmile_router_ca_cid", snapshot.lte.ca.cid, help_text="Current cell identifier")
    for band in snapshot.lte.ca.dl_bands:
        _add_gauge(lines, "fastmile_router_ca_band", 1, labels={"direction": "dl", "band": str(band)}, help_text="Carrier aggregation band membership")
    for band in snapshot.lte.ca.ul_bands:
        _add_gauge(lines, "fastmile_router_ca_band", 1, labels={"direction": "ul", "band": str(band)})

    if primary is not None:
        _add_gauge(lines, "fastmile_router_primary_cell_pci", primary.pci, help_text="Primary cell PCI")
        _add_gauge(lines, "fastmile_router_primary_cell_earfcn", primary.earfcn, help_text="Primary cell EARFCN")
        _add_gauge(lines, "fastmile_router_primary_cell_rsrp", primary.rsrp, help_text="Primary cell RSRP")
        _add_gauge(lines, "fastmile_router_primary_cell_rsrq", primary.rsrq, help_text="Primary cell RSRQ")
        _add_gauge(lines, "fastmile_router_primary_cell_rssi", primary.rssi, help_text="Primary cell RSSI")
        _add_gauge(lines, "fastmile_router_primary_cell_sinr", primary.sinr, help_text="Primary cell SINR")

    for index, cell in enumerate(secondary_cells):
        labels = {"index": str(index)}
        _add_gauge(lines, "fastmile_router_secondary_cell_pci", cell.pci, labels=labels, help_text="Secondary cell PCI")
        _add_gauge(lines, "fastmile_router_secondary_cell_earfcn", cell.earfcn, labels=labels, help_text="Secondary cell EARFCN")
        _add_gauge(lines, "fastmile_router_secondary_cell_rsrp", cell.rsrp, labels=labels, help_text="Secondary cell RSRP")
        _add_gauge(lines, "fastmile_router_secondary_cell_rsrq", cell.rsrq, labels=labels, help_text="Secondary cell RSRQ")
        _add_gauge(lines, "fastmile_router_secondary_cell_rssi", cell.rssi, labels=labels, help_text="Secondary cell RSSI")
        _add_gauge(lines, "fastmile_router_secondary_cell_sinr", cell.sinr, labels=labels, help_text="Secondary cell SINR")

    for index, cell in enumerate(snapshot.lte.available):
        labels = {"index": str(index)}
        _add_gauge(lines, "fastmile_router_available_cell_pci", cell.pci, labels=labels, help_text="Available cell PCI")
        _add_gauge(lines, "fastmile_router_available_cell_earfcn", cell.earfcn, labels=labels, help_text="Available cell EARFCN")
        _add_gauge(lines, "fastmile_router_available_cell_rsrp", cell.rsrp, labels=labels, help_text="Available cell RSRP")
        _add_gauge(lines, "fastmile_router_available_cell_rsrq", cell.rsrq, labels=labels, help_text="Available cell RSRQ")
        _add_gauge(lines, "fastmile_router_available_cell_rssi", cell.rssi, labels=labels, help_text="Available cell RSSI")
        _add_gauge(lines, "fastmile_router_available_cell_sinr", cell.sinr, labels=labels, help_text="Available cell SINR")

    return "\n".join(lines) + "\n"
