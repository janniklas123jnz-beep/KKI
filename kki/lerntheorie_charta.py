"""
#583 LerntheorieCharta — Piaget/Vygotsky/Bruner Lerntheorie Charta

Jean Piaget (1952): The Origins of Intelligence in Children — kognitive Entwicklungsstufen
  als Lerntheorie; Assimilation und Akkommodation als Lernmechanismen; konstruktivistisches
  Weltbild des aktiv lernenden Kindes; Equilibration als Motor der kognitiven Entwicklung
  im Peta-Schwarm Leitstern.
Lev Vygotsky (1934): Zone der nächsten Entwicklung als didaktisches Grundprinzip;
  Scaffolding als strukturierte Lernunterstützung; soziale Interaktion als Voraussetzung
  kognitiver Entwicklung; kulturhistorische Theorie des Lernens; Sprache als Medium
  des Denkens im Peta-Schwarm Leitstern.
Jerome Bruner (1960): The Process of Education — Spiralcurriculum als Lernarchitektur;
  Entdeckendes Lernen als pädagogisches Prinzip; narrative Kognition als Wissensform;
  Repräsentationsmodi als Stufenmodell des Lernens; Scaffolding als Lehrkonzept
  im Peta-Schwarm Leitstern. 🧠📖
Parent: BildungstheorieRegister (#582)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bildungstheorie_register import (
    BildungstheorieRegister,
    BildungstheorieRegisterGeltung,
    build_bildungstheorie_register,
)

_WEIGHT_DELTA: dict["LerntheorieChartaGeltung", float] = {}
_TIER_DELTA: dict["LerntheorieChartaGeltung", int] = {}
_TYP_MAP: dict["LerntheorieChartaGeltung", "LerntheorieChartaTyp"] = {}
_PROZEDUR_MAP: dict["LerntheorieChartaGeltung", "LerntheorieChartaProzedur"] = {}
_GELTUNG_MAP: dict[BildungstheorieRegisterGeltung, "LerntheorieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LerntheorieChartaGeltung.GESPERRT: 0.0,
        LerntheorieChartaGeltung.LERNTHEORETISCH: 0.05,
        LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        LerntheorieChartaGeltung.GESPERRT: 0,
        LerntheorieChartaGeltung.LERNTHEORETISCH: 1,
        LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        LerntheorieChartaGeltung.GESPERRT: LerntheorieChartaTyp.SCHUTZ_LERNTHEORIE,
        LerntheorieChartaGeltung.LERNTHEORETISCH: LerntheorieChartaTyp.ORDNUNGS_LERNTHEORIE,
        LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH: LerntheorieChartaTyp.SOUVERAENITAETS_LERNTHEORIE,
    })
    _PROZEDUR_MAP.update({
        LerntheorieChartaGeltung.GESPERRT: LerntheorieChartaProzedur.NOTPROZEDUR,
        LerntheorieChartaGeltung.LERNTHEORETISCH: LerntheorieChartaProzedur.REGELPROTOKOLL,
        LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH: LerntheorieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        BildungstheorieRegisterGeltung.GESPERRT: LerntheorieChartaGeltung.GESPERRT,
        BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH: LerntheorieChartaGeltung.LERNTHEORETISCH,
        BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH: LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH,
    })


class LerntheorieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    LERNTHEORETISCH = "lerntheoretisch"
    GRUNDLEGEND_LERNTHEORETISCH = "grundlegend-lerntheoretisch"


class LerntheorieChartaTyp(Enum):
    SCHUTZ_LERNTHEORIE = "schutz-lerntheorie"
    ORDNUNGS_LERNTHEORIE = "ordnungs-lerntheorie"
    SOUVERAENITAETS_LERNTHEORIE = "souveraenitaets-lerntheorie"


class LerntheorieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class LerntheorieChartaNorm:
    lerntheorie_charta_id: str
    paedagogik_typ: LerntheorieChartaTyp
    prozedur: LerntheorieChartaProzedur
    geltung: LerntheorieChartaGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class LerntheorieCharta:
    charta_id: str
    bildungstheorie_register: BildungstheorieRegister
    normen: tuple[LerntheorieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.lerntheorie_charta_id for n in self.normen
            if n.geltung is LerntheorieChartaGeltung.GESPERRT
        )

    @property
    def lerntheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.lerntheorie_charta_id for n in self.normen
            if n.geltung is LerntheorieChartaGeltung.LERNTHEORETISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.lerntheorie_charta_id for n in self.normen
            if n.geltung is LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH
        )

    @property
    def charta_signal(self):
        if any(n.geltung is LerntheorieChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is LerntheorieChartaGeltung.LERNTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-lerntheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-lerntheoretisch")


_init_map()


def build_lerntheorie_charta(
    bildungstheorie_register: BildungstheorieRegister | None = None,
    *,
    charta_id: str = "lerntheorie-charta",
) -> LerntheorieCharta:
    if bildungstheorie_register is None:
        bildungstheorie_register = build_bildungstheorie_register(
            register_id=f"{charta_id}-register"
        )

    normen: list[LerntheorieChartaNorm] = []
    for parent_norm in bildungstheorie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.bildungstheorie_register_id.removeprefix(f'{bildungstheorie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH)
        normen.append(
            LerntheorieChartaNorm(
                lerntheorie_charta_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"lerntheorie-charta:{new_geltung.value}",),
            )
        )
    return LerntheorieCharta(
        charta_id=charta_id,
        bildungstheorie_register=bildungstheorie_register,
        normen=tuple(normen),
    )
