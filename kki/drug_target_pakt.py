from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wirkstoff_manifest import WirkstoffManifest, build_wirkstoff_manifest


class DrugTargetPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_DRUG_TARGET = auto()
    DRUG_TARGET = auto()
    DRUG_TARGET_AKTIV = auto()
    DRUG_TARGET_SOUVERAEN = auto()


class DrugTargetPaktTyp(Enum):
    DRUGTARGETPAKT = auto()
    TARGETIDENTIFIKATION = auto()
    BINDUNGSMODELL = auto()


class DrugTargetPaktProzedur(Enum):
    TARGETSCREENING = auto()
    BINDUNGSANALYSE = auto()
    SELEKTIVITAETSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[DrugTargetPaktGeltung, float] = {
    DrugTargetPaktGeltung.GESPERRT: 0.0,
    DrugTargetPaktGeltung.GRUNDLEGEND_DRUG_TARGET: 1.8,
    DrugTargetPaktGeltung.DRUG_TARGET: 3.6,
    DrugTargetPaktGeltung.DRUG_TARGET_AKTIV: 5.4,
    DrugTargetPaktGeltung.DRUG_TARGET_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    DrugTargetPaktGeltung.GESPERRT: DrugTargetPaktTyp.DRUGTARGETPAKT,
    DrugTargetPaktGeltung.GRUNDLEGEND_DRUG_TARGET: DrugTargetPaktTyp.TARGETIDENTIFIKATION,
    DrugTargetPaktGeltung.DRUG_TARGET: DrugTargetPaktTyp.TARGETIDENTIFIKATION,
    DrugTargetPaktGeltung.DRUG_TARGET_AKTIV: DrugTargetPaktTyp.BINDUNGSMODELL,
    DrugTargetPaktGeltung.DRUG_TARGET_SOUVERAEN: DrugTargetPaktTyp.BINDUNGSMODELL,
}

_PROZEDUR_MAP = {
    DrugTargetPaktGeltung.GESPERRT: DrugTargetPaktProzedur.TARGETSCREENING,
    DrugTargetPaktGeltung.GRUNDLEGEND_DRUG_TARGET: DrugTargetPaktProzedur.TARGETSCREENING,
    DrugTargetPaktGeltung.DRUG_TARGET: DrugTargetPaktProzedur.BINDUNGSANALYSE,
    DrugTargetPaktGeltung.DRUG_TARGET_AKTIV: DrugTargetPaktProzedur.BINDUNGSANALYSE,
    DrugTargetPaktGeltung.DRUG_TARGET_SOUVERAEN: DrugTargetPaktProzedur.SELEKTIVITAETSBEWERTUNG,
}


@dataclass(frozen=True)
class DrugTargetPaktEintrag:
    geltung: DrugTargetPaktGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: DrugTargetPaktTyp
    prozedur: DrugTargetPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class DrugTargetPakt:
    eintraege: tuple[DrugTargetPaktEintrag, ...]
    parent: Optional[WirkstoffManifest] = None


def build_drug_target_pakt(parent: Optional[WirkstoffManifest] = None) -> DrugTargetPakt:
    if parent is None:
        parent = build_wirkstoff_manifest()
    base = sum(n.pharma_weight for n in parent.normen)
    eintraege = tuple(
        DrugTargetPaktEintrag(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"drug-target-{g.name.lower()}-001",),
            pharma_tags=("drug-target", "pakt", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(DrugTargetPaktGeltung)
    )
    return DrugTargetPakt(eintraege=eintraege, parent=parent)
