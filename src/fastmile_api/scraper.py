from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup, Comment, Tag

from fastmile_api.models import (
    ApnInfo,
    CaInfo,
    CellSignal,
    DeviceInfo,
    InterfaceData,
    LteInfo,
    Snapshot,
    SnapshotData,
    TrafficValue,
)


def _text(tag: Tag) -> str:
    return tag.get_text(strip=True)


def _first_text(soup: BeautifulSoup, element_id: str) -> str:
    tag = soup.find(id=element_id)
    if tag is None:
        raise ValueError(f"missing element: {element_id}")
    return _text(tag)


def _parse_int(value: str) -> int:
    match = re.search(r"-?\d+", value)
    if not match:
        raise ValueError(f"expected integer in: {value!r}")
    return int(match.group(0))


def _parse_ip(value: str) -> Optional[str]:
    value = value.strip()
    return None if value in {"", "::"} else value


def _parse_traffic(value: str) -> TrafficValue:
    cleaned = value.strip().upper()
    match = re.match(r"([0-9.]+)\s*([A-Z]+)", cleaned)
    if not match:
        raise ValueError(f"invalid traffic value: {value!r}")
    amount = float(match.group(1))
    unit = match.group(2)
    if unit == "MB":
        val_gb = amount / 1000
    elif unit == "GB":
        val_gb = amount
    elif unit == "KB":
        val_gb = amount / 1_000_000
    else:
        val_gb = amount
    return TrafficValue(val=amount, unit=unit, val_gb=val_gb)


def _find_comment_section(soup: BeautifulSoup, comment_text: str) -> Optional[Tag]:
    comment = soup.find(string=lambda text: isinstance(text, Comment) and text.strip() == comment_text)
    if comment is None:
        return None
    sibling = comment.find_next_sibling()
    while sibling is not None and not isinstance(sibling, Tag):
        sibling = sibling.find_next_sibling()
    return sibling


def _parse_apns(soup: BeautifulSoup) -> list[ApnInfo]:
    section = _find_comment_section(soup, "APNs card")
    if section is None:
        return []
    values = section.find_all("div", id=None)
    if len(values) < 3:
        return []
    result: list[ApnInfo] = []
    for index in range(2, len(values), 3):
        if index + 2 >= len(values):
            break
        result.append(
            ApnInfo(
                name=_text(values[index]),
                ipv4=_parse_ip(_text(values[index + 1])),
                ipv6=_parse_ip(_text(values[index + 2])),
            )
        )
    return result


def _parse_cell_group(section: Tag, cell_type: Optional[str]) -> list[CellSignal]:
    values = section.find_all(class_="name-of-value-in-card-bold")
    result: list[CellSignal] = []
    for index in range(0, len(values), 7):
        chunk = values[index : index + 7]
        if len(chunk) < 7:
            break
        result.append(
            CellSignal(
                pci=_parse_int(_text(chunk[0])),
                earfcn=_parse_int(_text(chunk[1])),
                cell_type=_text(chunk[2]) if cell_type is not None else None,
                rsrp=_parse_int(_text(chunk[3])),
                rsrq=_parse_int(_text(chunk[4])),
                rssi=_parse_int(_text(chunk[5])),
                sinr=_parse_int(_text(chunk[6])),
            )
        )
    return result


def _parse_available_cells(soup: BeautifulSoup) -> list[CellSignal]:
    result: list[CellSignal] = []
    index = 0
    while True:
        cell_id = soup.find(id=f"available-cell-id-{index}")
        if cell_id is None:
            break
        result.append(
            CellSignal(
                pci=_parse_int(_text(cell_id)),
                earfcn=_parse_int(_first_text(soup, f"available-earfcn-{index}")),
                cell_type=None,
                rsrp=_parse_int(_first_text(soup, f"rsrp-{index}")),
                rsrq=_parse_int(_first_text(soup, f"rsrq-{index}")),
                rssi=_parse_int(_first_text(soup, f"rssi-{index}")),
                sinr=_parse_int(_first_text(soup, f"sinr-{index}")),
            )
        )
        index += 1
    return result


def _parse_ca(soup: BeautifulSoup) -> CaInfo:
    attached = soup.find(id="attached-cell-val")
    if attached is None:
        raise ValueError("missing attached-cell-val")
    spans = attached.find_all("span")
    if len(spans) < 3:
        raise ValueError("missing carrier aggregation values")
    enb = _parse_int(_text(spans[0]))
    cid = _parse_int(_text(spans[1]))
    primary_band = _parse_int(_text(spans[2]))

    dl_text = _first_text(soup, "bandDL-val")
    ul_text = _first_text(soup, "bandUL-val")
    dl_bands = [primary_band]
    ul_bands = [primary_band]
    dl_match = re.findall(r"B(\d+)", dl_text)
    ul_match = re.findall(r"B(\d+)", ul_text)
    dl_bands.extend(int(value) for value in dl_match)
    ul_bands.extend(int(value) for value in ul_match)
    return CaInfo(enb=enb, cid=cid, dl_bands=dl_bands, ul_bands=ul_bands)


def _parse_interface_data(soup: BeautifulSoup, name: str) -> InterfaceData:
    section = soup.find(class_=name)
    if section is None:
        raise ValueError(f"missing traffic section: {name}")
    bytes_values = section.find_all(class_="bytes")
    if len(bytes_values) < 2:
        raise ValueError(f"missing traffic values for: {name}")
    return InterfaceData(
        download=_parse_traffic(_text(bytes_values[0])),
        upload=_parse_traffic(_text(bytes_values[1])),
    )


def parse_snapshot(html: str) -> Snapshot:
    soup = BeautifulSoup(html, "html.parser")

    device = DeviceInfo(
        model=_first_text(soup, "model-value"),
        software_version=_first_text(soup, "software-version-val"),
        serial_number=_first_text(soup, "sn-value"),
        imei=_first_text(soup, "imei-value"),
        imsi=_first_text(soup, "imsi-name-value"),
        mac=_first_text(soup, "eth-mac-value"),
        lock_status=_first_text(soup, "lockStatus-name-value"),
    )

    data = SnapshotData(
        eth=_parse_interface_data(soup, "Ethernet"),
        lte=_parse_interface_data(soup, "LTE"),
    )

    primary_section = _find_comment_section(soup, "Primary Cell information card")
    secondary_section = _find_comment_section(soup, "Secondary Cell information card")
    available_section = _find_comment_section(soup, "Available cells grid (*x6)")

    active: list[CellSignal] = []
    if primary_section is not None:
        active.extend(_parse_cell_group(primary_section, cell_type="primary"))
    if secondary_section is not None:
        active.extend(_parse_cell_group(secondary_section, cell_type="secondary"))

    available: list[CellSignal] = []
    if available_section is not None:
        available = _parse_available_cells(soup)

    lte = LteInfo(
        ca=_parse_ca(soup),
        active=active,
        available=available,
    )

    apns = _parse_apns(soup)

    return Snapshot(device=device, apns=apns, data=data, lte=lte)
