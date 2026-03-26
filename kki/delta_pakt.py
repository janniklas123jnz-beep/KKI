from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .turbidite_manifest import TurbiditeManifest, build_turbidite_manifest


class DeltaPaktTyp(Enum):
    FLUSSDELTA = auto()
    GEZEITENDELTA = auto()
    WAVENDELTA = auto()
    SUBMARINDELTA = auto()
    LACUSTRINDELTA = auto()


class DeltaPaktProzedur(Enum):
    AUFSCHUETTUNG = auto()
    VERTEILUNG = auto()
    EROSION = auto()
    SUBSIDENZ = auto()
    PROGRADATION = auto()


_WEIGHT_DELTA = {
    DeltaPaktTyp.FLUSSDELTA: 0.0,
    DeltaPaktTyp.GEZEITENDELTA: 1.7,
    DeltaPaktTyp.WAVENDELTA: 3.4,
    DeltaPaktTyp.SUBMARINDELTA: 5.1,
    DeltaPaktTyp.LACUSTRINDELTA: 6.8,
}
_TYP_MAP = {
    DeltaPaktTyp.FLUSSDELTA: "flussdelta",
    DeltaPaktTyp.GEZEITENDELTA: "gezeitendelta",
    DeltaPaktTyp.WAVENDELTA: "wavendelta",
    DeltaPaktTyp.SUBMARINDELTA: "submarindelta",
    DeltaPaktTyp.LACUSTRINDELTA: "lacustrindelta",
}
_PROZEDUR_MAP = {
    DeltaPaktProzedur.AUFSCHUETTUNG: "aufschuettung",
    DeltaPaktProzedur.VERTEILUNG: "verteilung",
    DeltaPaktProzedur.EROSION: "erosion",
    DeltaPaktProzedur.SUBSIDENZ: "subsidenz",
    DeltaPaktProzedur.PROGRADATION: "progradation",
}


@dataclass(frozen=True)
class DeltaPaktEintrag:
    typ: DeltaPaktTyp
    prozedur: DeltaPaktProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class DeltaPakt:
    eintraege: tuple[DeltaPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "delta-pakt-866",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_delta_pakt(parent: Optional[TurbiditeManifest] = None) -> DeltaPakt:
    if parent is None:
        parent = build_turbidite_manifest()
    base = sum(n.sedimentologie_weight for n in parent.normen)
    eintraege = tuple(
        DeltaPaktEintrag(
            typ=t,
            prozedur=list(DeltaPaktProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(DeltaPaktTyp)
    )
    return DeltaPakt(eintraege=eintraege)
