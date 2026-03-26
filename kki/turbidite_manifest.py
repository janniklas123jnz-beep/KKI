from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .diagenese_kodex import DiageneseKodex, build_diagenese_kodex


class TurbiditeManifestTyp(Enum):
    BOUMA_A = auto()
    BOUMA_B = auto()
    BOUMA_C = auto()
    BOUMA_D = auto()
    BOUMA_E = auto()


class TurbiditeManifestProzedur(Enum):
    TRUEBESTROEMUNG = auto()
    ABLAGERUNG = auto()
    EROSION = auto()
    TRANSPORT = auto()
    DEFORMATION = auto()


_WEIGHT_DELTA = {
    TurbiditeManifestTyp.BOUMA_A: 0.0,
    TurbiditeManifestTyp.BOUMA_B: 1.6,
    TurbiditeManifestTyp.BOUMA_C: 3.2,
    TurbiditeManifestTyp.BOUMA_D: 4.8,
    TurbiditeManifestTyp.BOUMA_E: 6.4,
}
_TYP_MAP = {
    TurbiditeManifestTyp.BOUMA_A: "bouma_a",
    TurbiditeManifestTyp.BOUMA_B: "bouma_b",
    TurbiditeManifestTyp.BOUMA_C: "bouma_c",
    TurbiditeManifestTyp.BOUMA_D: "bouma_d",
    TurbiditeManifestTyp.BOUMA_E: "bouma_e",
}
_PROZEDUR_MAP = {
    TurbiditeManifestProzedur.TRUEBESTROEMUNG: "truebestroemung",
    TurbiditeManifestProzedur.ABLAGERUNG: "ablagerung",
    TurbiditeManifestProzedur.EROSION: "erosion",
    TurbiditeManifestProzedur.TRANSPORT: "transport",
    TurbiditeManifestProzedur.DEFORMATION: "deformation",
}


@dataclass(frozen=True)
class TurbiditeManifestNorm:
    typ: TurbiditeManifestTyp
    prozedur: TurbiditeManifestProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class TurbiditeManifest:
    normen: tuple[TurbiditeManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "turbidite-manifest-865",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_turbidite_manifest(parent: Optional[DiageneseKodex] = None) -> TurbiditeManifest:
    if parent is None:
        parent = build_diagenese_kodex()
    base = sum(e.sedimentologie_weight for e in parent.eintraege)
    normen = tuple(
        TurbiditeManifestNorm(
            typ=t,
            prozedur=list(TurbiditeManifestProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(TurbiditeManifestTyp)
    )
    return TurbiditeManifest(normen=normen)
