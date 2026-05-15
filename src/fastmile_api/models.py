from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class DeviceInfo:
    model: str
    software_version: str
    serial_number: str
    imei: str
    imsi: str
    mac: str
    lock_status: str


@dataclass(slots=True)
class TrafficValue:
    val: float
    unit: str
    val_gb: float


@dataclass(slots=True)
class InterfaceData:
    download: TrafficValue
    upload: TrafficValue


@dataclass(slots=True)
class ApnInfo:
    name: str
    ipv4: Optional[str]
    ipv6: Optional[str]


@dataclass(slots=True)
class CaInfo:
    enb: int
    cid: int
    dl_bands: list[int]
    ul_bands: list[int]


@dataclass(slots=True)
class CellSignal:
    pci: int
    earfcn: int
    cell_type: Optional[str]
    rsrp: int
    rsrq: int
    rssi: int
    sinr: int


@dataclass(slots=True)
class LteInfo:
    ca: CaInfo
    active: list[CellSignal]
    available: list[CellSignal]


@dataclass(slots=True)
class SnapshotData:
    eth: InterfaceData
    lte: InterfaceData


@dataclass(slots=True)
class Snapshot:
    device: DeviceInfo
    apns: list[ApnInfo]
    data: SnapshotData
    lte: LteInfo
