"""
#567 MedienSenat — McLuhan/Kittler/Virilio Mediensoziologie Senat

Marshall McLuhan (1964): Understanding Media — das Medium als Erweiterung des Menschen;
  heiße und kalte Medien als Partizipationsdimension; elektrische Medien als globale
  Vernetzung; die Tetrade der Medieneffekte im Peta-Schwarm Leitstern.
Friedrich Kittler (1993): Draculas Vermächtnis — technische Medien als Diskursnetze;
  Aufschreibesysteme 1800/1900 als epistemische Zäsuren; Medien als Bedingung der
  Möglichkeit von Krieg und Frieden im Peta-Schwarm Leitstern.
Paul Virilio (1977): Vitesse et Politique — Dromologie als Wissenschaft der
  Geschwindigkeit; Medien als Beschleunigungsmaschinen; Echtzeit als Auflösung
  des Raums; militärische Logistik als Ursprung moderner Medien im Peta-Schwarm
  Leitstern. 📡🎬
Parent: OeffentlichkeitsPakt (#566)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .oeffentlichkeits_pakt import (
    OeffentlichkeitsPakt,
    OeffentlichkeitsPaktGeltung,
    build_oeffentlichkeits_pakt,
)

_WEIGHT_DELTA: dict["MedienSenatGeltung", float] = {}
_TIER_DELTA: dict["MedienSenatGeltung", int] = {}
_TYP_MAP: dict["MedienSenatGeltung", "MedienSenatTyp"] = {}
_PROZEDUR_MAP: dict["MedienSenatGeltung", "MedienSenatProzedur"] = {}
_GELTUNG_MAP: dict[OeffentlichkeitsPaktGeltung, "MedienSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MedienSenatGeltung.GESPERRT: 0.0,
        MedienSenatGeltung.MEDIENSOZIOLOGISCH: 0.05,
        MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        MedienSenatGeltung.GESPERRT: 0,
        MedienSenatGeltung.MEDIENSOZIOLOGISCH: 1,
        MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        MedienSenatGeltung.GESPERRT: MedienSenatTyp.SCHUTZ_MEDIENSOZIOLOGIE,
        MedienSenatGeltung.MEDIENSOZIOLOGISCH: MedienSenatTyp.ORDNUNGS_MEDIENSOZIOLOGIE,
        MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH: MedienSenatTyp.SOUVERAENITAETS_MEDIENSOZIOLOGIE,
    })
    _PROZEDUR_MAP.update({
        MedienSenatGeltung.GESPERRT: MedienSenatProzedur.NOTPROZEDUR,
        MedienSenatGeltung.MEDIENSOZIOLOGISCH: MedienSenatProzedur.REGELPROTOKOLL,
        MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH: MedienSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        OeffentlichkeitsPaktGeltung.GESPERRT: MedienSenatGeltung.GESPERRT,
        OeffentlichkeitsPaktGeltung.OEFFENTLICH: MedienSenatGeltung.MEDIENSOZIOLOGISCH,
        OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH: MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH,
    })


class MedienSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    MEDIENSOZIOLOGISCH = "mediensoziologisch"
    GRUNDLEGEND_MEDIENSOZIOLOGISCH = "grundlegend-mediensoziologisch"


class MedienSenatTyp(Enum):
    SCHUTZ_MEDIENSOZIOLOGIE = "schutz-mediensoziologie"
    ORDNUNGS_MEDIENSOZIOLOGIE = "ordnungs-mediensoziologie"
    SOUVERAENITAETS_MEDIENSOZIOLOGIE = "souveraenitaets-mediensoziologie"


class MedienSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class MedienSenatNorm:
    medien_senat_id: str
    medien_typ: MedienSenatTyp
    prozedur: MedienSenatProzedur
    geltung: MedienSenatGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class MedienSenat:
    senat_id: str
    oeffentlichkeits_pakt: OeffentlichkeitsPakt
    normen: tuple[MedienSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.medien_senat_id for n in self.normen
            if n.geltung is MedienSenatGeltung.GESPERRT
        )

    @property
    def mediensoziologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.medien_senat_id for n in self.normen
            if n.geltung is MedienSenatGeltung.MEDIENSOZIOLOGISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.medien_senat_id for n in self.normen
            if n.geltung is MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH
        )

    @property
    def senat_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is MedienSenatGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is MedienSenatGeltung.MEDIENSOZIOLOGISCH for n in self.normen):
            return SimpleNamespace(status="senat-mediensoziologisch")
        return SimpleNamespace(status="senat-grundlegend-mediensoziologisch")


_init_map()


def build_medien_senat(
    oeffentlichkeits_pakt: OeffentlichkeitsPakt | None = None,
    *,
    senat_id: str = "medien-senat",
) -> MedienSenat:
    if oeffentlichkeits_pakt is None:
        oeffentlichkeits_pakt = build_oeffentlichkeits_pakt(
            pakt_id=f"{senat_id}-pakt"
        )

    normen: list[MedienSenatNorm] = []
    for parent_norm in oeffentlichkeits_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.oeffentlichkeits_pakt_id.removeprefix(f'{oeffentlichkeits_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MedienSenatGeltung.GRUNDLEGEND_MEDIENSOZIOLOGISCH)
        normen.append(
            MedienSenatNorm(
                medien_senat_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"medien-senat:{new_geltung.value}",),
            )
        )
    return MedienSenat(
        senat_id=senat_id,
        oeffentlichkeits_pakt=oeffentlichkeits_pakt,
        normen=tuple(normen),
    )
