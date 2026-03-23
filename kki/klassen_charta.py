"""
#493 KlassenCharta — Marx: Produktionsverhältnisse/Klassen; Engels: Dialektik; Bourdieu: Klassenhabitus

Karl Marx (1867): Das Kapital — Produktionsverhältnisse als Basis gesellschaftlicher
  Überbaustrukturen; Klassenantagonismus als Motor historischer Transformation;
  Mehrwert und Ausbeutung als strukturelle Merkmale kapitalistischer Produktion.
Friedrich Engels (1845): Die Lage der arbeitenden Klasse in England — empirische
  Fundierung des dialektischen Materialismus; Klassenbewusstsein als Voraussetzung
  politischer Emanzipation.
Pierre Bourdieu (Vorgriff, 1979): Die feinen Unterschiede — Klassenhabitus als
  inkorporierte Klassenlage; soziale Reproduktion durch kulturelle Praxis.
Leitsterns Terra-Schwarm kartiert Klassenverhältnisse: GESPERRT sichert strukturelle
Normkerne, KLASSENSTRUKTURELL ermöglicht dialektische Klassenanalyse,
GRUNDLEGEND_KLASSENSTRUKTURELL synthetisiert materielle Reproduktionslogik für den
Weg zur Peta-Schwarmgröße.
Parent: GesellschaftsRegister (#492)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gesellschafts_register import (
    GesellschaftsRegister,
    GesellschaftsRegisterGeltung,
    build_gesellschafts_register,
)

_GELTUNG_MAP: dict[GesellschaftsRegisterGeltung, "KlassenChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GesellschaftsRegisterGeltung.GESPERRT] = KlassenChartaGeltung.GESPERRT
    _GELTUNG_MAP[GesellschaftsRegisterGeltung.GESELLSCHAFTLICH] = KlassenChartaGeltung.KLASSENSTRUKTURELL
    _GELTUNG_MAP[GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH] = KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL


class KlassenChartaTyp(Enum):
    SCHUTZ_KLASSE = "schutz-klasse"
    ORDNUNGS_KLASSE = "ordnungs-klasse"
    SOUVERAENITAETS_KLASSE = "souveraenitaets-klasse"


class KlassenChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KlassenChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KLASSENSTRUKTURELL = "klassenstrukturell"
    GRUNDLEGEND_KLASSENSTRUKTURELL = "grundlegend-klassenstrukturell"


_init_map()

_TYP_MAP: dict[KlassenChartaGeltung, KlassenChartaTyp] = {
    KlassenChartaGeltung.GESPERRT: KlassenChartaTyp.SCHUTZ_KLASSE,
    KlassenChartaGeltung.KLASSENSTRUKTURELL: KlassenChartaTyp.ORDNUNGS_KLASSE,
    KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL: KlassenChartaTyp.SOUVERAENITAETS_KLASSE,
}

_PROZEDUR_MAP: dict[KlassenChartaGeltung, KlassenChartaProzedur] = {
    KlassenChartaGeltung.GESPERRT: KlassenChartaProzedur.NOTPROZEDUR,
    KlassenChartaGeltung.KLASSENSTRUKTURELL: KlassenChartaProzedur.REGELPROTOKOLL,
    KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL: KlassenChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KlassenChartaGeltung, float] = {
    KlassenChartaGeltung.GESPERRT: 0.0,
    KlassenChartaGeltung.KLASSENSTRUKTURELL: 0.04,
    KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL: 0.08,
}

_TIER_DELTA: dict[KlassenChartaGeltung, int] = {
    KlassenChartaGeltung.GESPERRT: 0,
    KlassenChartaGeltung.KLASSENSTRUKTURELL: 1,
    KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL: 2,
}


@dataclass(frozen=True)
class KlassenChartaNorm:
    klassen_charta_id: str
    klassen_typ: KlassenChartaTyp
    prozedur: KlassenChartaProzedur
    geltung: KlassenChartaGeltung
    klassen_weight: float
    klassen_tier: int
    canonical: bool
    klassen_ids: tuple[str, ...]
    klassen_tags: tuple[str, ...]


@dataclass(frozen=True)
class KlassenCharta:
    charta_id: str
    gesellschafts_register: GesellschaftsRegister
    normen: tuple[KlassenChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.klassen_charta_id for n in self.normen if n.geltung is KlassenChartaGeltung.GESPERRT)

    @property
    def klassenstrukturell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.klassen_charta_id for n in self.normen if n.geltung is KlassenChartaGeltung.KLASSENSTRUKTURELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.klassen_charta_id for n in self.normen if n.geltung is KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL)

    @property
    def charta_signal(self):
        if any(n.geltung is KlassenChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KlassenChartaGeltung.KLASSENSTRUKTURELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-klassenstrukturell")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-klassenstrukturell")


def build_klassen_charta(
    gesellschafts_register: GesellschaftsRegister | None = None,
    *,
    charta_id: str = "klassen-charta",
) -> KlassenCharta:
    if gesellschafts_register is None:
        gesellschafts_register = build_gesellschafts_register(register_id=f"{charta_id}-register")

    normen: list[KlassenChartaNorm] = []
    for parent_norm in gesellschafts_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.gesellschafts_register_id.removeprefix(f'{gesellschafts_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.gesellschafts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gesellschafts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL)
        normen.append(
            KlassenChartaNorm(
                klassen_charta_id=new_id,
                klassen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                klassen_weight=new_weight,
                klassen_tier=new_tier,
                canonical=is_canonical,
                klassen_ids=parent_norm.gesellschafts_ids + (new_id,),
                klassen_tags=parent_norm.gesellschafts_tags + (f"klassen-charta:{new_geltung.value}",),
            )
        )
    return KlassenCharta(
        charta_id=charta_id,
        gesellschafts_register=gesellschafts_register,
        normen=tuple(normen),
    )
