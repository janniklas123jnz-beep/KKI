"""
#497 KommunikationsSenat — Habermas: Kommunikatives Handeln; Luhmann: Kommunikation als Sozialoperation

Jürgen Habermas (1981): Theorie des kommunikativen Handelns — kommunikatives vs.
  strategisches Handeln; Lebenswelt als symbolisch reproduzierter Hintergrundkonsens;
  Systemkolonisierung der Lebenswelt als Pathologie der Moderne; Diskursethik als
  prozedurale Grundlage normativer Geltungsansprüche.
Jürgen Habermas (1992): Faktizität und Geltung — deliberative Demokratie als
  Vermittlung von Faktizität (Recht) und Geltung (Moral); kommunikative Macht als
  Gegenmacht zu administrativer Steuerung.
Niklas Luhmann (1984): Soziale Systeme — Kommunikation (nicht Handlung) als basale
  soziale Operation; Kommunikation als Synthese von Information, Mitteilung und
  Verstehen; Anschlusskommunikation als Reproduktionsmodus sozialer Systeme.
Leitsterns Terra-Schwarm senatorisiert Kommunikationsordnung: GESPERRT sichert
kommunikative Normkerne, KOMMUNIKATIV ermöglicht diskursive Koordination zwischen
Lebenswelt und System, GRUNDLEGEND_KOMMUNIKATIV synthetisiert reflexive Verständigung
als Grundlage kollektiver Willensbildung für den Weg zur Peta-Schwarmgröße.
Parent: StrukturierungsPakt (#496)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .strukturierungs_pakt import (
    StrukturierungsPakt,
    StrukturierungsPaktGeltung,
    build_strukturierungs_pakt,
)

_GELTUNG_MAP: dict[StrukturierungsPaktGeltung, "KommunikationsSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[StrukturierungsPaktGeltung.GESPERRT] = KommunikationsSenatGeltung.GESPERRT
    _GELTUNG_MAP[StrukturierungsPaktGeltung.STRUKTURIEREND] = KommunikationsSenatGeltung.KOMMUNIKATIV
    _GELTUNG_MAP[StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND] = KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV


class KommunikationsSenatTyp(Enum):
    SCHUTZ_KOMMUNIKATION = "schutz-kommunikation"
    ORDNUNGS_KOMMUNIKATION = "ordnungs-kommunikation"
    SOUVERAENITAETS_KOMMUNIKATION = "souveraenitaets-kommunikation"


class KommunikationsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KommunikationsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMMUNIKATIV = "kommunikativ"
    GRUNDLEGEND_KOMMUNIKATIV = "grundlegend-kommunikativ"


_init_map()

_TYP_MAP: dict[KommunikationsSenatGeltung, KommunikationsSenatTyp] = {
    KommunikationsSenatGeltung.GESPERRT: KommunikationsSenatTyp.SCHUTZ_KOMMUNIKATION,
    KommunikationsSenatGeltung.KOMMUNIKATIV: KommunikationsSenatTyp.ORDNUNGS_KOMMUNIKATION,
    KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV: KommunikationsSenatTyp.SOUVERAENITAETS_KOMMUNIKATION,
}

_PROZEDUR_MAP: dict[KommunikationsSenatGeltung, KommunikationsSenatProzedur] = {
    KommunikationsSenatGeltung.GESPERRT: KommunikationsSenatProzedur.NOTPROZEDUR,
    KommunikationsSenatGeltung.KOMMUNIKATIV: KommunikationsSenatProzedur.REGELPROTOKOLL,
    KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV: KommunikationsSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KommunikationsSenatGeltung, float] = {
    KommunikationsSenatGeltung.GESPERRT: 0.0,
    KommunikationsSenatGeltung.KOMMUNIKATIV: 0.04,
    KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV: 0.08,
}

_TIER_DELTA: dict[KommunikationsSenatGeltung, int] = {
    KommunikationsSenatGeltung.GESPERRT: 0,
    KommunikationsSenatGeltung.KOMMUNIKATIV: 1,
    KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV: 2,
}


@dataclass(frozen=True)
class KommunikationsSenatNorm:
    kommunikations_senat_id: str
    kommunikations_typ: KommunikationsSenatTyp
    prozedur: KommunikationsSenatProzedur
    geltung: KommunikationsSenatGeltung
    kommunikations_weight: float
    kommunikations_tier: int
    canonical: bool
    kommunikations_ids: tuple[str, ...]
    kommunikations_tags: tuple[str, ...]


@dataclass(frozen=True)
class KommunikationsSenat:
    senat_id: str
    strukturierungs_pakt: StrukturierungsPakt
    normen: tuple[KommunikationsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikations_senat_id for n in self.normen if n.geltung is KommunikationsSenatGeltung.GESPERRT)

    @property
    def kommunikativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikations_senat_id for n in self.normen if n.geltung is KommunikationsSenatGeltung.KOMMUNIKATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikations_senat_id for n in self.normen if n.geltung is KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV)

    @property
    def senat_signal(self):
        if any(n.geltung is KommunikationsSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is KommunikationsSenatGeltung.KOMMUNIKATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-kommunikativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-kommunikativ")


def build_kommunikations_senat(
    strukturierungs_pakt: StrukturierungsPakt | None = None,
    *,
    senat_id: str = "kommunikations-senat",
) -> KommunikationsSenat:
    if strukturierungs_pakt is None:
        strukturierungs_pakt = build_strukturierungs_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[KommunikationsSenatNorm] = []
    for parent_norm in strukturierungs_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.strukturierungs_pakt_id.removeprefix(f'{strukturierungs_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.strukturierungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.strukturierungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV)
        normen.append(
            KommunikationsSenatNorm(
                kommunikations_senat_id=new_id,
                kommunikations_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kommunikations_weight=new_weight,
                kommunikations_tier=new_tier,
                canonical=is_canonical,
                kommunikations_ids=parent_norm.strukturierungs_ids + (new_id,),
                kommunikations_tags=parent_norm.strukturierungs_tags + (f"kommunikations-senat:{new_geltung.value}",),
            )
        )
    return KommunikationsSenat(
        senat_id=senat_id,
        strukturierungs_pakt=strukturierungs_pakt,
        normen=tuple(normen),
    )
