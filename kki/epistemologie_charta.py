"""
#473 EpistemologieCharta — Locke/Hume/Berkeley: Empirismus, tabula rasa, Kausalinduktion.
Der britische Empirismus erklärt Erkenntnis aus sinnlicher Erfahrung: Lockes tabula rasa
verwirft angeborene Ideen, Humes Kausalinduktion zeigt die Grenzen empirischer Schlüsse,
Berkeleys Immaterialismus reduziert Sein auf Wahrgenommenwerden (esse est percipi).
Phänomenalistisches Wissen beruht auf Impressionen und Ideen. Leitsterns Terra-Schwarm
kalibriert epistemische Quellen: GESPERRT sichert Datenbasis, EPISTEMISCH ermöglicht
induktive Generalisierung, GRUNDLEGEND_EPISTEMISCH synthetisiert Wissensarchitektur.
Parent: OntologieRegister (#472)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ontologie_register import (
    OntologieRegister,
    OntologieRegisterGeltung,
    build_ontologie_register,
)

_GELTUNG_MAP: dict[OntologieRegisterGeltung, "EpistemologieChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[OntologieRegisterGeltung.GESPERRT] = EpistemologieChartaGeltung.GESPERRT
    _GELTUNG_MAP[OntologieRegisterGeltung.ONTOLOGISCH] = EpistemologieChartaGeltung.EPISTEMISCH
    _GELTUNG_MAP[OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH] = EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH


class EpistemologieChartaTyp(Enum):
    SCHUTZ_EPISTEMOLOGIE = "schutz-epistemologie"
    ORDNUNGS_EPISTEMOLOGIE = "ordnungs-epistemologie"
    SOUVERAENITAETS_EPISTEMOLOGIE = "souveraenitaets-epistemologie"


class EpistemologieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EpistemologieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    EPISTEMISCH = "epistemisch"
    GRUNDLEGEND_EPISTEMISCH = "grundlegend-epistemisch"


_init_map()

_TYP_MAP = {
    EpistemologieChartaGeltung.GESPERRT: EpistemologieChartaTyp.SCHUTZ_EPISTEMOLOGIE,
    EpistemologieChartaGeltung.EPISTEMISCH: EpistemologieChartaTyp.ORDNUNGS_EPISTEMOLOGIE,
    EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH: EpistemologieChartaTyp.SOUVERAENITAETS_EPISTEMOLOGIE,
}
_PROZEDUR_MAP = {
    EpistemologieChartaGeltung.GESPERRT: EpistemologieChartaProzedur.NOTPROZEDUR,
    EpistemologieChartaGeltung.EPISTEMISCH: EpistemologieChartaProzedur.REGELPROTOKOLL,
    EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH: EpistemologieChartaProzedur.PLENARPROTOKOLL,
}
_WEIGHT_DELTA = {
    EpistemologieChartaGeltung.GESPERRT: 0.0,
    EpistemologieChartaGeltung.EPISTEMISCH: 0.04,
    EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH: 0.08,
}
_TIER_DELTA = {
    EpistemologieChartaGeltung.GESPERRT: 0,
    EpistemologieChartaGeltung.EPISTEMISCH: 1,
    EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH: 2,
}


@dataclass(frozen=True)
class EpistemologieChartaNorm:
    epistemologie_charta_id: str
    epistemologie_typ: EpistemologieChartaTyp
    prozedur: EpistemologieChartaProzedur
    geltung: EpistemologieChartaGeltung
    epistemologie_weight: float
    epistemologie_tier: int
    canonical: bool
    epistemologie_ids: tuple[str, ...]
    epistemologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class EpistemologieCharta:
    charta_id: str
    ontologie_register: OntologieRegister
    normen: tuple[EpistemologieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.epistemologie_charta_id for n in self.normen if n.geltung is EpistemologieChartaGeltung.GESPERRT)

    @property
    def epistemisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.epistemologie_charta_id for n in self.normen if n.geltung is EpistemologieChartaGeltung.EPISTEMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.epistemologie_charta_id for n in self.normen if n.geltung is EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH)

    @property
    def charta_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is EpistemologieChartaGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is EpistemologieChartaGeltung.EPISTEMISCH for n in self.normen):
            return SimpleNamespace(status="charta-epistemisch")
        return SimpleNamespace(status="charta-grundlegend-epistemisch")


def build_epistemologie_charta(
    ontologie_register: OntologieRegister | None = None,
    *,
    charta_id: str = "epistemologie-charta",
) -> EpistemologieCharta:
    if ontologie_register is None:
        ontologie_register = build_ontologie_register(register_id=f"{charta_id}-register")
    normen: list[EpistemologieChartaNorm] = []
    for parent_norm in ontologie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.ontologie_register_id.removeprefix(f'{ontologie_register.register_id}-')}"
        is_canonical = parent_norm.canonical and (new_geltung is EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH)
        normen.append(EpistemologieChartaNorm(
            epistemologie_charta_id=new_id,
            epistemologie_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            epistemologie_weight=round(min(1.0, parent_norm.ontologie_weight + _WEIGHT_DELTA[new_geltung]), 3),
            epistemologie_tier=parent_norm.ontologie_tier + _TIER_DELTA[new_geltung],
            canonical=is_canonical,
            epistemologie_ids=parent_norm.ontologie_ids + (new_id,),
            epistemologie_tags=parent_norm.ontologie_tags + (f"epistemologie-charta:{new_geltung.value}",),
        ))
    return EpistemologieCharta(charta_id=charta_id, ontologie_register=ontologie_register, normen=tuple(normen))
