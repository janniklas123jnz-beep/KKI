from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .edelmineral_charta import EdelmineralCharta, build_edelmineral_charta


class MineralogieVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGIE_SOUVERAEN = auto()
    MINERALOGIE_SOUVERAEN = auto()
    MINERALOGIE_SOUVERAEN_AKTIV = auto()
    MINERALOGIE_SOUVERAEN_ABSOLUT = auto()


class MineralogieVerfassungTyp(Enum):
    MINERALOGIEVERFASSUNG = auto()
    MINERALOGIESOUVERAENITAET = auto()
    MINERALOGIEKONSTITUTION = auto()


class MineralogieVerfassungProzedur(Enum):
    MINERALOGIEVERFASSUNGSANALYSE = auto()
    MINERALOGIEVERFASSUNGSSYNTHESE = auto()
    MINERALOGIEVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MineralogieVerfassungGeltung, float] = {
    MineralogieVerfassungGeltung.GESPERRT: 0.0,
    MineralogieVerfassungGeltung.GRUNDLEGEND_MINERALOGIE_SOUVERAEN: 2.1,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN: 4.2,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN_AKTIV: 6.3,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    MineralogieVerfassungGeltung.GESPERRT: MineralogieVerfassungTyp.MINERALOGIEVERFASSUNG,
    MineralogieVerfassungGeltung.GRUNDLEGEND_MINERALOGIE_SOUVERAEN: MineralogieVerfassungTyp.MINERALOGIEKONSTITUTION,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN: MineralogieVerfassungTyp.MINERALOGIEKONSTITUTION,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN_AKTIV: MineralogieVerfassungTyp.MINERALOGIESOUVERAENITAET,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN_ABSOLUT: MineralogieVerfassungTyp.MINERALOGIESOUVERAENITAET,
}

_PROZEDUR_MAP = {
    MineralogieVerfassungGeltung.GESPERRT: MineralogieVerfassungProzedur.MINERALOGIEVERFASSUNGSANALYSE,
    MineralogieVerfassungGeltung.GRUNDLEGEND_MINERALOGIE_SOUVERAEN: MineralogieVerfassungProzedur.MINERALOGIEVERFASSUNGSANALYSE,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN: MineralogieVerfassungProzedur.MINERALOGIEVERFASSUNGSSYNTHESE,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN_AKTIV: MineralogieVerfassungProzedur.MINERALOGIEVERFASSUNGSSYNTHESE,
    MineralogieVerfassungGeltung.MINERALOGIE_SOUVERAEN_ABSOLUT: MineralogieVerfassungProzedur.MINERALOGIEVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class MineralogieVerfassungsNorm:
    geltung: MineralogieVerfassungGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: MineralogieVerfassungTyp
    prozedur: MineralogieVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MineralogieVerfassung:
    normen: tuple[MineralogieVerfassungsNorm, ...]
    parent: Optional[EdelmineralCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "mineralogie-verfassung-830",
            "total_weight": round(sum(n.mineralogie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_mineralogie_verfassung(parent: Optional[EdelmineralCharta] = None) -> MineralogieVerfassung:
    if parent is None:
        parent = build_edelmineral_charta()
    base = sum(n.mineralogie_weight for n in parent.normen)
    tier_base = max(n.mineralogie_tier for n in parent.normen)
    normen = tuple(
        MineralogieVerfassungsNorm(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=tier_base + i + 1,
            mineralogie_ids=(f"mineralogie-verfassung-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MineralogieVerfassungGeltung)
    )
    return MineralogieVerfassung(normen=normen, parent=parent)
