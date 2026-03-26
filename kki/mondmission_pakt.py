"""Mondmission-Pakt #986 — Pakt der Mondmissionen im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .raumstation_manifest import Raumstation, build_raumstation


class MondmissionTyp(Enum):
    APOLLO_ERBE = "APOLLO_ERBE"
    ARTEMIS = "ARTEMIS"
    MONDBASE = "MONDBASE"
    RESSOURCEN = "RESSOURCEN"
    WISSENSCHAFT = "WISSENSCHAFT"


class MondmissionProzedur(Enum):
    PLANUNG = "PLANUNG"
    TRAINING = "TRAINING"
    LANDUNG = "LANDUNG"
    EXPLORATION = "EXPLORATION"
    RUECKKEHR = "RUECKKEHR"


_WEIGHT_DELTA: dict[str, float] = {
    "APOLLO_ERBE": 0.15,
    "ARTEMIS": 0.2,
    "MONDBASE": 0.25,
    "RESSOURCEN": 0.18,
    "WISSENSCHAFT": 0.16,
}

_TYP_MAP: dict[MondmissionTyp, str] = {
    MondmissionTyp.APOLLO_ERBE: "Apollo-Erbe",
    MondmissionTyp.ARTEMIS: "Artemis-Programm",
    MondmissionTyp.MONDBASE: "Mondbasislager",
    MondmissionTyp.RESSOURCEN: "Mondressourcen",
    MondmissionTyp.WISSENSCHAFT: "Mondwissenschaft",
}

_PROZEDUR_MAP: dict[MondmissionProzedur, str] = {
    MondmissionProzedur.PLANUNG: "Planung",
    MondmissionProzedur.TRAINING: "Training",
    MondmissionProzedur.LANDUNG: "Landung",
    MondmissionProzedur.EXPLORATION: "Exploration",
    MondmissionProzedur.RUECKKEHR: "Rückkehr",
}


@dataclass(frozen=True)
class MondmissionEintrag:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class MondmissionPakt:
    eintraege: tuple[MondmissionEintrag, ...]


def build_mondmission_pakt(parent=None) -> MondmissionPakt:
    if parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].raumfahrt_weight
        tier_base = max(n.raumfahrt_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].raumfahrt_weight
        tier_base = max(e.raumfahrt_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(MondmissionTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(MondmissionEintrag(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return MondmissionPakt(eintraege=tuple(items))
