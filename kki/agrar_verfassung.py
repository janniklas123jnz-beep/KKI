from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .lebensmittel_charta import LebensmittelCharta, build_lebensmittel_charta


class AgrarVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_AGRAR_SOUVERAEN = auto()
    AGRAR_SOUVERAEN = auto()
    AGRAR_SOUVERAEN_AKTIV = auto()
    AGRAR_SOUVERAEN_ABSOLUT = auto()


class AgrarVerfassungTyp(Enum):
    AGRARVERFASSUNG = auto()
    AGRARSOUVERAENITAET = auto()
    AGRARKONSTITUTION = auto()


class AgrarVerfassungProzedur(Enum):
    AGRARVERFASSUNGSANALYSE = auto()
    AGRARVERFASSUNGSSYNTHESE = auto()
    AGRARVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[AgrarVerfassungGeltung, float] = {
    AgrarVerfassungGeltung.GESPERRT: 0.0,
    AgrarVerfassungGeltung.GRUNDLEGEND_AGRAR_SOUVERAEN: 2.1,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN: 4.2,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN_AKTIV: 6.3,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    AgrarVerfassungGeltung.GESPERRT: AgrarVerfassungTyp.AGRARVERFASSUNG,
    AgrarVerfassungGeltung.GRUNDLEGEND_AGRAR_SOUVERAEN: AgrarVerfassungTyp.AGRARKONSTITUTION,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN: AgrarVerfassungTyp.AGRARKONSTITUTION,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN_AKTIV: AgrarVerfassungTyp.AGRARSOUVERAENITAET,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN_ABSOLUT: AgrarVerfassungTyp.AGRARSOUVERAENITAET,
}

_PROZEDUR_MAP = {
    AgrarVerfassungGeltung.GESPERRT: AgrarVerfassungProzedur.AGRARVERFASSUNGSANALYSE,
    AgrarVerfassungGeltung.GRUNDLEGEND_AGRAR_SOUVERAEN: AgrarVerfassungProzedur.AGRARVERFASSUNGSANALYSE,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN: AgrarVerfassungProzedur.AGRARVERFASSUNGSSYNTHESE,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN_AKTIV: AgrarVerfassungProzedur.AGRARVERFASSUNGSSYNTHESE,
    AgrarVerfassungGeltung.AGRAR_SOUVERAEN_ABSOLUT: AgrarVerfassungProzedur.AGRARVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class AgrarVerfassungsNorm:
    geltung: AgrarVerfassungGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: AgrarVerfassungTyp
    prozedur: AgrarVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class AgrarVerfassung:
    normen: tuple[AgrarVerfassungsNorm, ...]
    parent: Optional[LebensmittelCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "agrar-verfassung-790",
            "total_weight": round(sum(n.agrar_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_agrar_verfassung(parent: Optional[LebensmittelCharta] = None) -> AgrarVerfassung:
    if parent is None:
        parent = build_lebensmittel_charta()
    base = sum(n.agrar_weight for n in parent.normen)
    tier_base = max(n.agrar_tier for n in parent.normen)
    normen = tuple(
        AgrarVerfassungsNorm(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=tier_base + i + 1,
            agrar_ids=(f"agrar-verfassung-{g.name.lower()}-001",),
            agrar_tags=("agrar", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(AgrarVerfassungGeltung)
    )
    return AgrarVerfassung(normen=normen, parent=parent)
