"""
#582 BildungstheorieRegister — Pestalozzi/Herbart/Humboldt Bildungstheorie Register

Johann Heinrich Pestalozzi (1801): Wie Gertrud ihre Kinder lehrt — Anschauung als
  Grundprinzip; sinnliche Erfahrung als Basis aller Erkenntnis; Elementarbildung als
  systematischer Aufbau vom Einfachen zum Komplexen; Herz, Hand und Kopf als ganzheitliches
  Bildungsideal im Peta-Schwarm Leitstern.
Johann Friedrich Herbart (1806): Allgemeine Pädagogik — Erziehender Unterricht als
  Systemkonzept; Vielseitigkeit des Interesses als Bildungsziel; Vorstellungsmassen als
  Grundlage des Lernens; Pädagogik als Wissenschaft mit psychologischer Fundierung
  im Peta-Schwarm Leitstern.
Wilhelm von Humboldt (1810): Über die innere und äußere Organisation der höheren
  wissenschaftlichen Anstalten — Bildungsideal der Einheit von Lehre und Forschung;
  Bildung als Selbstvervollkommnung; Lernfreiheit als universitäres Grundprinzip;
  allgemeine Menschenbildung als Ziel des Bildungswesens im Peta-Schwarm Leitstern. 📚🏫
Parent: PaedagogikFeld (#581)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .paedagogik_feld import (
    PaedagogikFeld,
    PaedagogikFeldGeltung,
    build_paedagogik_feld,
)

_WEIGHT_DELTA: dict["BildungstheorieRegisterGeltung", float] = {}
_TIER_DELTA: dict["BildungstheorieRegisterGeltung", int] = {}
_TYP_MAP: dict["BildungstheorieRegisterGeltung", "BildungstheorieRegisterTyp"] = {}
_PROZEDUR_MAP: dict["BildungstheorieRegisterGeltung", "BildungstheorieRegisterProzedur"] = {}
_GELTUNG_MAP: dict[PaedagogikFeldGeltung, "BildungstheorieRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BildungstheorieRegisterGeltung.GESPERRT: 0.0,
        BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH: 0.05,
        BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        BildungstheorieRegisterGeltung.GESPERRT: 0,
        BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH: 1,
        BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        BildungstheorieRegisterGeltung.GESPERRT: BildungstheorieRegisterTyp.SCHUTZ_BILDUNGSTHEORIE,
        BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH: BildungstheorieRegisterTyp.ORDNUNGS_BILDUNGSTHEORIE,
        BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH: BildungstheorieRegisterTyp.SOUVERAENITAETS_BILDUNGSTHEORIE,
    })
    _PROZEDUR_MAP.update({
        BildungstheorieRegisterGeltung.GESPERRT: BildungstheorieRegisterProzedur.NOTPROZEDUR,
        BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH: BildungstheorieRegisterProzedur.REGELPROTOKOLL,
        BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH: BildungstheorieRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        PaedagogikFeldGeltung.GESPERRT: BildungstheorieRegisterGeltung.GESPERRT,
        PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN: BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH,
        PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN: BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH,
    })


class BildungstheorieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    BILDUNGSTHEORETISCH = "bildungstheoretisch"
    GRUNDLEGEND_BILDUNGSTHEORETISCH = "grundlegend-bildungstheoretisch"


class BildungstheorieRegisterTyp(Enum):
    SCHUTZ_BILDUNGSTHEORIE = "schutz-bildungstheorie"
    ORDNUNGS_BILDUNGSTHEORIE = "ordnungs-bildungstheorie"
    SOUVERAENITAETS_BILDUNGSTHEORIE = "souveraenitaets-bildungstheorie"


class BildungstheorieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class BildungstheorieRegisterNorm:
    bildungstheorie_register_id: str
    paedagogik_typ: BildungstheorieRegisterTyp
    prozedur: BildungstheorieRegisterProzedur
    geltung: BildungstheorieRegisterGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class BildungstheorieRegister:
    register_id: str
    paedagogik_feld: PaedagogikFeld
    normen: tuple[BildungstheorieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.bildungstheorie_register_id for n in self.normen
            if n.geltung is BildungstheorieRegisterGeltung.GESPERRT
        )

    @property
    def bildungstheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.bildungstheorie_register_id for n in self.normen
            if n.geltung is BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.bildungstheorie_register_id for n in self.normen
            if n.geltung is BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH
        )

    @property
    def register_signal(self):
        if any(n.geltung is BildungstheorieRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is BildungstheorieRegisterGeltung.BILDUNGSTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-bildungstheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-bildungstheoretisch")


_init_map()


def build_bildungstheorie_register(
    paedagogik_feld: PaedagogikFeld | None = None,
    *,
    register_id: str = "bildungstheorie-register",
) -> BildungstheorieRegister:
    if paedagogik_feld is None:
        paedagogik_feld = build_paedagogik_feld(feld_id=f"{register_id}-feld")

    normen: list[BildungstheorieRegisterNorm] = []
    for parent_norm in paedagogik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.paedagogik_feld_id.removeprefix(f'{paedagogik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BildungstheorieRegisterGeltung.GRUNDLEGEND_BILDUNGSTHEORETISCH)
        normen.append(
            BildungstheorieRegisterNorm(
                bildungstheorie_register_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"bildungstheorie-register:{new_geltung.value}",),
            )
        )
    return BildungstheorieRegister(
        register_id=register_id,
        paedagogik_feld=paedagogik_feld,
        normen=tuple(normen),
    )
