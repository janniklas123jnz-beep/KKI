"""
#564 InformationsKodex — Shannon/Wiener/Bateson Informationstheorie Kodex

Claude Shannon (1948): A Mathematical Theory of Communication — Informationsentropie
  als Maß der Unbestimmtheit; Kanalkapazität und Shannons Theorem; Quellencodierung
  und Kanalcodierung als Grundprinzipien; bit als universelle Informationseinheit im
  Peta-Schwarm Leitstern.
Norbert Wiener (1948): Cybernetics — Rückkopplung als Steuerungsprinzip; Kybernetik
  als allgemeine Theorie der Kontrolle und Kommunikation; Entropie als Maß der
  Unordnung; Homeostase als Systemziel im Peta-Schwarm Leitstern.
Gregory Bateson (1972): Steps to an Ecology of Mind — Information als Unterschied,
  der einen Unterschied macht; Doppelbindung als kommunikationstheoretisches Paradox;
  Metalog als epistemologische Reflexionsform im Peta-Schwarm Leitstern. 🔢📊
Parent: MedientheorieCharta (#563)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .medientheorie_charta import (
    MedientheorieCharta,
    MedientheorieChartaGeltung,
    build_medientheorie_charta,
)

_WEIGHT_DELTA: dict["InformationsKodexGeltung", float] = {}
_TIER_DELTA: dict["InformationsKodexGeltung", int] = {}
_TYP_MAP: dict["InformationsKodexGeltung", "InformationsKodexTyp"] = {}
_PROZEDUR_MAP: dict["InformationsKodexGeltung", "InformationsKodexProzedur"] = {}
_GELTUNG_MAP: dict[MedientheorieChartaGeltung, "InformationsKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InformationsKodexGeltung.GESPERRT: 0.0,
        InformationsKodexGeltung.INFORMATIONELL: 0.05,
        InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL: 0.1,
    })
    _TIER_DELTA.update({
        InformationsKodexGeltung.GESPERRT: 0,
        InformationsKodexGeltung.INFORMATIONELL: 1,
        InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL: 2,
    })
    _TYP_MAP.update({
        InformationsKodexGeltung.GESPERRT: InformationsKodexTyp.SCHUTZ_INFORMATION,
        InformationsKodexGeltung.INFORMATIONELL: InformationsKodexTyp.ORDNUNGS_INFORMATION,
        InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL: InformationsKodexTyp.SOUVERAENITAETS_INFORMATION,
    })
    _PROZEDUR_MAP.update({
        InformationsKodexGeltung.GESPERRT: InformationsKodexProzedur.NOTPROZEDUR,
        InformationsKodexGeltung.INFORMATIONELL: InformationsKodexProzedur.REGELPROTOKOLL,
        InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL: InformationsKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        MedientheorieChartaGeltung.GESPERRT: InformationsKodexGeltung.GESPERRT,
        MedientheorieChartaGeltung.MEDIENTHEORETISCH: InformationsKodexGeltung.INFORMATIONELL,
        MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH: InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL,
    })


class InformationsKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    INFORMATIONELL = "informationell"
    GRUNDLEGEND_INFORMATIONELL = "grundlegend-informationell"


class InformationsKodexTyp(Enum):
    SCHUTZ_INFORMATION = "schutz-information"
    ORDNUNGS_INFORMATION = "ordnungs-information"
    SOUVERAENITAETS_INFORMATION = "souveraenitaets-information"


class InformationsKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class InformationsKodexNorm:
    informations_kodex_id: str
    medien_typ: InformationsKodexTyp
    prozedur: InformationsKodexProzedur
    geltung: InformationsKodexGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class InformationsKodex:
    kodex_id: str
    medientheorie_charta: MedientheorieCharta
    normen: tuple[InformationsKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.informations_kodex_id for n in self.normen
            if n.geltung is InformationsKodexGeltung.GESPERRT
        )

    @property
    def informationell_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.informations_kodex_id for n in self.normen
            if n.geltung is InformationsKodexGeltung.INFORMATIONELL
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.informations_kodex_id for n in self.normen
            if n.geltung is InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL
        )

    @property
    def kodex_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is InformationsKodexGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is InformationsKodexGeltung.INFORMATIONELL for n in self.normen):
            return SimpleNamespace(status="kodex-informationell")
        return SimpleNamespace(status="kodex-grundlegend-informationell")


_init_map()


def build_informations_kodex(
    medientheorie_charta: MedientheorieCharta | None = None,
    *,
    kodex_id: str = "informations-kodex",
) -> InformationsKodex:
    if medientheorie_charta is None:
        medientheorie_charta = build_medientheorie_charta(
            charta_id=f"{kodex_id}-charta"
        )

    normen: list[InformationsKodexNorm] = []
    for parent_norm in medientheorie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.medientheorie_charta_id.removeprefix(f'{medientheorie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL)
        normen.append(
            InformationsKodexNorm(
                informations_kodex_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"informations-kodex:{new_geltung.value}",),
            )
        )
    return InformationsKodex(
        kodex_id=kodex_id,
        medientheorie_charta=medientheorie_charta,
        normen=tuple(normen),
    )
