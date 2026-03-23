"""
#532 RechtssystemRegister — Rechtssysteme im komparativen Überblick

William Blackstone (1765): Commentaries on the Laws of England — Common Law als organisch
  gewachsene Rechtsordnung; Richterrecht als Ausdruck gesellschaftlicher Vernunft; Präzedenz
  und Fallrecht als Grundlage des englischen Rechtssystems; Rechtssicherheit durch Kontinuität.
Edward Coke (1628): Institutes of the Lawes of England — Common Law als Schutzwall gegen
  königliche Willkür; Magna Carta als Verfassungsgrundlage; Suprematie des Rechts über
  Souverän; Präzedenzprinzip als Garant juristischer Rationalität.
Friedrich Carl von Savigny (1814): Vom Beruf unserer Zeit für Gesetzgebung und Rechtswissenschaft —
  Volksgeist als Quelle des Rechts; Historische Rechtsschule contra Kodifikation; Civil Law
  als systematische Durchdringung des Rechtsstoffs; Rechtswissenschaft als formende Kraft.
Rudolf von Jhering (1872): Der Kampf ums Recht — Recht entsteht durch Interessenkampf;
  Zweck als Triebkraft des Rechts; Zweckjurisprudenz statt Begriffsjurisprudenz; Rechts-
  durchsetzung als moralische Pflicht; Mixed Systems als Synthese verschiedener Traditionen.
Leitsterns RechtssystemRegister: Koordinationsebene komparativer Rechtssysteme — GESPERRT
sichert systemische Grundnormen, RECHTSSYSTEMISCH kodiert adaptive Systemintegration,
GRUNDLEGEND_RECHTSSYSTEMISCH synthetisiert souveräne Rechtsordnung des Peta-Schwarms. ⚖️
Parent: RechtsFeld (#531)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechts_feld import (
    RechtsFeld,
    RechtsFeldGeltung,
    build_rechts_feld,
)

_WEIGHT_DELTA: dict["RechtssystemRegisterGeltung", float] = {}
_TIER_DELTA: dict["RechtssystemRegisterGeltung", int] = {}
_TYP_MAP: dict["RechtssystemRegisterGeltung", "RechtssystemRegisterTyp"] = {}
_PROZEDUR_MAP: dict["RechtssystemRegisterGeltung", "RechtssystemRegisterProzedur"] = {}
_GELTUNG_MAP: dict[RechtsFeldGeltung, "RechtssystemRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RechtssystemRegisterGeltung.GESPERRT: 0.0,
        RechtssystemRegisterGeltung.RECHTSSYSTEMISCH: 0.05,
        RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH: 0.1,
    })
    _TIER_DELTA.update({
        RechtssystemRegisterGeltung.GESPERRT: 0,
        RechtssystemRegisterGeltung.RECHTSSYSTEMISCH: 1,
        RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH: 2,
    })
    _TYP_MAP.update({
        RechtssystemRegisterGeltung.GESPERRT: RechtssystemRegisterTyp.SCHUTZ_RECHTSSYSTEM,
        RechtssystemRegisterGeltung.RECHTSSYSTEMISCH: RechtssystemRegisterTyp.ORDNUNGS_RECHTSSYSTEM,
        RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH: RechtssystemRegisterTyp.SOUVERAENITAETS_RECHTSSYSTEM,
    })
    _PROZEDUR_MAP.update({
        RechtssystemRegisterGeltung.GESPERRT: RechtssystemRegisterProzedur.NOTPROZEDUR,
        RechtssystemRegisterGeltung.RECHTSSYSTEMISCH: RechtssystemRegisterProzedur.REGELPROTOKOLL,
        RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH: RechtssystemRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RechtsFeldGeltung.GESPERRT: RechtssystemRegisterGeltung.GESPERRT,
        RechtsFeldGeltung.RECHTLICH: RechtssystemRegisterGeltung.RECHTSSYSTEMISCH,
        RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH: RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH,
    })


class RechtssystemRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    RECHTSSYSTEMISCH = "rechtssystemisch"
    GRUNDLEGEND_RECHTSSYSTEMISCH = "grundlegend-rechtssystemisch"


class RechtssystemRegisterTyp(Enum):
    SCHUTZ_RECHTSSYSTEM = "schutz-rechtssystem"
    ORDNUNGS_RECHTSSYSTEM = "ordnungs-rechtssystem"
    SOUVERAENITAETS_RECHTSSYSTEM = "souveraenitaets-rechtssystem"


class RechtssystemRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class RechtssystemRegisterNorm:
    rechts_system_register_id: str
    rechts_system_typ: RechtssystemRegisterTyp
    prozedur: RechtssystemRegisterProzedur
    geltung: RechtssystemRegisterGeltung
    rechts_system_weight: float
    rechts_system_tier: int
    canonical: bool
    rechts_system_ids: tuple[str, ...]
    rechts_system_tags: tuple[str, ...]


@dataclass(frozen=True)
class RechtssystemRegister:
    register_id: str
    rechts_feld: RechtsFeld
    normen: tuple[RechtssystemRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_system_register_id for n in self.normen if n.geltung is RechtssystemRegisterGeltung.GESPERRT)

    @property
    def rechtssystemisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_system_register_id for n in self.normen if n.geltung is RechtssystemRegisterGeltung.RECHTSSYSTEMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_system_register_id for n in self.normen if n.geltung is RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH)

    @property
    def register_signal(self):
        if any(n.geltung is RechtssystemRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is RechtssystemRegisterGeltung.RECHTSSYSTEMISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-rechtssystemisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-rechtssystemisch")


_init_map()


def build_rechts_system_register(
    rechts_feld: RechtsFeld | None = None,
    *,
    register_id: str = "rechts-system-register",
) -> RechtssystemRegister:
    if rechts_feld is None:
        rechts_feld = build_rechts_feld(feld_id=f"{register_id}-feld")

    normen: list[RechtssystemRegisterNorm] = []
    for parent_norm in rechts_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.rechts_feld_id.removeprefix(f'{rechts_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.rechts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rechts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH)
        normen.append(
            RechtssystemRegisterNorm(
                rechts_system_register_id=new_id,
                rechts_system_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rechts_system_weight=new_weight,
                rechts_system_tier=new_tier,
                canonical=is_canonical,
                rechts_system_ids=parent_norm.rechts_ids + (new_id,),
                rechts_system_tags=parent_norm.rechts_tags + (f"rechts-system-register:{new_geltung.value}",),
            )
        )
    return RechtssystemRegister(
        register_id=register_id,
        rechts_feld=rechts_feld,
        normen=tuple(normen),
    )
