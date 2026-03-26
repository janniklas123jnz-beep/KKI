"""
#913 SensorikCharta — Sensorik: LiDAR, IMU & Sensorfusion für Roboter-Wahrnehmung.
Elfes (1989): Occupancy Grids — probabilistische Umgebungsrepräsentation aus Sensordaten.
Kalman (1960): Kalman-Filter — optimale Zustandsschätzung bei Messrauschen.
Thrun, Burgard & Fox (2005): Probabilistic Robotics — Sensorfusion als Bayes-Inferenz.
Velodyne (2007): LiDAR-Revolution — 3D-Punktwolken für Fahrzeugwahrnehmung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .kinematik_register import KinematikRegister, build_kinematik_register


class SensorikChartaTyp(Enum):
    LIDAR = auto()
    KAMERA = auto()
    IMU = auto()
    ULTRASCHALL = auto()
    TAKTIL = auto()


class SensorikChartaProzedur(Enum):
    KALIBRIERUNG = auto()
    DATENFUSION = auto()
    FILTERUNG = auto()
    KLASSIFIKATION = auto()
    LOKALISATION = auto()


_WEIGHT_DELTA = {
    SensorikChartaTyp.LIDAR: 0.0,
    SensorikChartaTyp.KAMERA: 1.7,
    SensorikChartaTyp.IMU: 3.4,
    SensorikChartaTyp.ULTRASCHALL: 5.1,
    SensorikChartaTyp.TAKTIL: 6.8,
}
_TYP_MAP = {
    SensorikChartaTyp.LIDAR: "lidar",
    SensorikChartaTyp.KAMERA: "kamera",
    SensorikChartaTyp.IMU: "imu",
    SensorikChartaTyp.ULTRASCHALL: "ultraschall",
    SensorikChartaTyp.TAKTIL: "taktil",
}
_PROZEDUR_MAP = {
    SensorikChartaProzedur.KALIBRIERUNG: "kalibrierung",
    SensorikChartaProzedur.DATENFUSION: "datenfusion",
    SensorikChartaProzedur.FILTERUNG: "filterung",
    SensorikChartaProzedur.KLASSIFIKATION: "klassifikation",
    SensorikChartaProzedur.LOKALISATION: "lokalisation",
}


@dataclass(frozen=True)
class SensorikChartaNorm:
    typ: SensorikChartaTyp
    prozedur: SensorikChartaProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SensorikCharta:
    normen: tuple[SensorikChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "sensorik-charta-913",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_sensorik_charta(parent: Optional[KinematikRegister] = None) -> SensorikCharta:
    if parent is None:
        parent = build_kinematik_register()
    base = sum(e.robotik_weight for e in parent.eintraege)
    normen = tuple(
        SensorikChartaNorm(
            typ=t,
            prozedur=list(SensorikChartaProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SensorikChartaTyp)
    )
    return SensorikCharta(normen=normen)
