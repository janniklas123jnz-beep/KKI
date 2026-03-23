"""
#537 StrafrechtsSenat — Strafrecht & Strafrechtstheorie

Cesare Beccaria (1764): Dei delitti e delle pene — Humanisierung des Strafrechts; Verhältnis-
  mäßigkeit von Tat und Strafe; Abschaffung der Folter und Todesstrafe; Prävention statt
  Vergeltung; Gleichheit vor dem Strafgesetz; Grundstein des modernen liberalen Strafrechts.
Paul Johann Anselm von Feuerbach (1801): Revision der Grundsätze und Grundbegriffe des positiven
  peinlichen Rechts — Nulla poena sine lege als Fundamentalprinzip; psychologische Zwangstheorie;
  Codex Juris Bavarici Criminalis; Strafrecht als rationaler Normenkatalog.
H.L.A. Hart (1968): Punishment and Responsibility — Trennung von Bestrafungszielen und
  Strafzumessung; Generalprävention und Schuldprinzip; Verteidigung des Utilitarismus im
  Strafrecht; Hart-Devlin-Debatte über Strafrecht und Moral.
Günther Jakobs (1991): Strafrecht, Allgemeiner Teil — Strafrecht als Normbestätigung;
  Funktionaler Verbrechensbegriff; Feindstrafrecht-Kontroverse; Täterschaft und Teilnahme;
  Strafrecht als Kommunikation normativer Erwartungen in der Gesellschaft.
Leitsterns StrafrechtsSenat: Pönale Normordnung — GESPERRT sichert strafrechtliche
Fundamentalnormen, STRAFRECHTLICH kodiert adaptive Sanktionsmechanismen,
GRUNDLEGEND_STRAFRECHTLICH synthetisiert souveräne Strafrechtsordnung. ⚖️
Parent: RechtssoziologiePakt (#536)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechtssoziologie_pakt import (
    RechtssoziologiePakt,
    RechtssoziologiePaktGeltung,
    build_rechtssoziologie_pakt,
)

_WEIGHT_DELTA: dict["StrafrechtsSenatGeltung", float] = {}
_TIER_DELTA: dict["StrafrechtsSenatGeltung", int] = {}
_TYP_MAP: dict["StrafrechtsSenatGeltung", "StrafrechtsSenatTyp"] = {}
_PROZEDUR_MAP: dict["StrafrechtsSenatGeltung", "StrafrechtsSenatProzedur"] = {}
_GELTUNG_MAP: dict[RechtssoziologiePaktGeltung, "StrafrechtsSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        StrafrechtsSenatGeltung.GESPERRT: 0.0,
        StrafrechtsSenatGeltung.STRAFRECHTLICH: 0.05,
        StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        StrafrechtsSenatGeltung.GESPERRT: 0,
        StrafrechtsSenatGeltung.STRAFRECHTLICH: 1,
        StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH: 2,
    })
    _TYP_MAP.update({
        StrafrechtsSenatGeltung.GESPERRT: StrafrechtsSenatTyp.SCHUTZ_STRAFRECHT,
        StrafrechtsSenatGeltung.STRAFRECHTLICH: StrafrechtsSenatTyp.ORDNUNGS_STRAFRECHT,
        StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH: StrafrechtsSenatTyp.SOUVERAENITAETS_STRAFRECHT,
    })
    _PROZEDUR_MAP.update({
        StrafrechtsSenatGeltung.GESPERRT: StrafrechtsSenatProzedur.NOTPROZEDUR,
        StrafrechtsSenatGeltung.STRAFRECHTLICH: StrafrechtsSenatProzedur.REGELPROTOKOLL,
        StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH: StrafrechtsSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RechtssoziologiePaktGeltung.GESPERRT: StrafrechtsSenatGeltung.GESPERRT,
        RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH: StrafrechtsSenatGeltung.STRAFRECHTLICH,
        RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH: StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH,
    })


class StrafrechtsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    STRAFRECHTLICH = "strafrechtlich"
    GRUNDLEGEND_STRAFRECHTLICH = "grundlegend-strafrechtlich"


class StrafrechtsSenatTyp(Enum):
    SCHUTZ_STRAFRECHT = "schutz-strafrecht"
    ORDNUNGS_STRAFRECHT = "ordnungs-strafrecht"
    SOUVERAENITAETS_STRAFRECHT = "souveraenitaets-strafrecht"


class StrafrechtsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class StrafrechtsSenatNorm:
    strafrechts_senat_id: str
    strafrechts_typ: StrafrechtsSenatTyp
    prozedur: StrafrechtsSenatProzedur
    geltung: StrafrechtsSenatGeltung
    strafrechts_weight: float
    strafrechts_tier: int
    canonical: bool
    strafrechts_ids: tuple[str, ...]
    strafrechts_tags: tuple[str, ...]


@dataclass(frozen=True)
class StrafrechtsSenat:
    senat_id: str
    rechtssoziologie_pakt: RechtssoziologiePakt
    normen: tuple[StrafrechtsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strafrechts_senat_id for n in self.normen if n.geltung is StrafrechtsSenatGeltung.GESPERRT)

    @property
    def strafrechtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strafrechts_senat_id for n in self.normen if n.geltung is StrafrechtsSenatGeltung.STRAFRECHTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strafrechts_senat_id for n in self.normen if n.geltung is StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH)

    @property
    def senat_signal(self):
        if any(n.geltung is StrafrechtsSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is StrafrechtsSenatGeltung.STRAFRECHTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-strafrechtlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-strafrechtlich")


_init_map()


def build_strafrechts_senat(
    rechtssoziologie_pakt: RechtssoziologiePakt | None = None,
    *,
    senat_id: str = "strafrechts-senat",
) -> StrafrechtsSenat:
    if rechtssoziologie_pakt is None:
        rechtssoziologie_pakt = build_rechtssoziologie_pakt(
            pakt_id=f"{senat_id}-pakt"
        )

    normen: list[StrafrechtsSenatNorm] = []
    for parent_norm in rechtssoziologie_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.rechtssoziologie_pakt_id.removeprefix(f'{rechtssoziologie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.rechtssoziologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rechtssoziologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH)
        normen.append(
            StrafrechtsSenatNorm(
                strafrechts_senat_id=new_id,
                strafrechts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                strafrechts_weight=new_weight,
                strafrechts_tier=new_tier,
                canonical=is_canonical,
                strafrechts_ids=parent_norm.rechtssoziologie_ids + (new_id,),
                strafrechts_tags=parent_norm.rechtssoziologie_tags + (f"strafrechts-senat:{new_geltung.value}",),
            )
        )
    return StrafrechtsSenat(
        senat_id=senat_id,
        rechtssoziologie_pakt=rechtssoziologie_pakt,
        normen=tuple(normen),
    )
