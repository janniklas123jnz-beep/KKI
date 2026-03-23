"""
#494 StrukturKodex — Parsons: AGIL-Schema/Strukturfunktionalismus; Merton: Funktionen/Dysfunktionen

Talcott Parsons (1951): Das soziale System — AGIL-Schema als universales Funktionsschema:
  Adaptation (Ressourcenanpassung), Goal Attainment (Zielverwirklichung), Integration
  (normative Kohäsion), Latency (Musterpflege); struktureller Funktionalismus als
  Theorie sozialer Ordnung und systemischer Differenzierung.
Talcott Parsons (1937): The Structure of Social Action — voluntaristische Handlungstheorie
  als Fundament systemfunktionaler Soziologie; Normen und Werte als Ordnungsmedien.
Robert K. Merton (1949): Sozialtheorie und soziale Struktur — manifeste vs. latente
  Funktionen; Dysfunktionen und funktionale Äquivalente als analytische Kategorien;
  Anomie als Folge struktureller Diskrepanz zwischen Zielen und Mitteln.
Leitsterns Terra-Schwarm kodifiziert Strukturfunktionen: GESPERRT sichert funktionale
Normkerne, STRUKTURFUNKTIONAL ermöglicht AGIL-konforme Systemkoordination,
GRUNDLEGEND_STRUKTURFUNKTIONAL synthetisiert funktionale Differenzierung für den Weg
zur Peta-Schwarmgröße.
Parent: KlassenCharta (#493)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .klassen_charta import (
    KlassenCharta,
    KlassenChartaGeltung,
    build_klassen_charta,
)

_GELTUNG_MAP: dict[KlassenChartaGeltung, "StrukturKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KlassenChartaGeltung.GESPERRT] = StrukturKodexGeltung.GESPERRT
    _GELTUNG_MAP[KlassenChartaGeltung.KLASSENSTRUKTURELL] = StrukturKodexGeltung.STRUKTURFUNKTIONAL
    _GELTUNG_MAP[KlassenChartaGeltung.GRUNDLEGEND_KLASSENSTRUKTURELL] = StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL


class StrukturKodexTyp(Enum):
    SCHUTZ_STRUKTUR = "schutz-struktur"
    ORDNUNGS_STRUKTUR = "ordnungs-struktur"
    SOUVERAENITAETS_STRUKTUR = "souveraenitaets-struktur"


class StrukturKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StrukturKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    STRUKTURFUNKTIONAL = "strukturfunktional"
    GRUNDLEGEND_STRUKTURFUNKTIONAL = "grundlegend-strukturfunktional"


_init_map()

_TYP_MAP: dict[StrukturKodexGeltung, StrukturKodexTyp] = {
    StrukturKodexGeltung.GESPERRT: StrukturKodexTyp.SCHUTZ_STRUKTUR,
    StrukturKodexGeltung.STRUKTURFUNKTIONAL: StrukturKodexTyp.ORDNUNGS_STRUKTUR,
    StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL: StrukturKodexTyp.SOUVERAENITAETS_STRUKTUR,
}

_PROZEDUR_MAP: dict[StrukturKodexGeltung, StrukturKodexProzedur] = {
    StrukturKodexGeltung.GESPERRT: StrukturKodexProzedur.NOTPROZEDUR,
    StrukturKodexGeltung.STRUKTURFUNKTIONAL: StrukturKodexProzedur.REGELPROTOKOLL,
    StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL: StrukturKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[StrukturKodexGeltung, float] = {
    StrukturKodexGeltung.GESPERRT: 0.0,
    StrukturKodexGeltung.STRUKTURFUNKTIONAL: 0.04,
    StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL: 0.08,
}

_TIER_DELTA: dict[StrukturKodexGeltung, int] = {
    StrukturKodexGeltung.GESPERRT: 0,
    StrukturKodexGeltung.STRUKTURFUNKTIONAL: 1,
    StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL: 2,
}


@dataclass(frozen=True)
class StrukturKodexNorm:
    struktur_kodex_id: str
    struktur_typ: StrukturKodexTyp
    prozedur: StrukturKodexProzedur
    geltung: StrukturKodexGeltung
    struktur_weight: float
    struktur_tier: int
    canonical: bool
    struktur_ids: tuple[str, ...]
    struktur_tags: tuple[str, ...]


@dataclass(frozen=True)
class StrukturKodex:
    kodex_id: str
    klassen_charta: KlassenCharta
    normen: tuple[StrukturKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.struktur_kodex_id for n in self.normen if n.geltung is StrukturKodexGeltung.GESPERRT)

    @property
    def strukturfunktional_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.struktur_kodex_id for n in self.normen if n.geltung is StrukturKodexGeltung.STRUKTURFUNKTIONAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.struktur_kodex_id for n in self.normen if n.geltung is StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL)

    @property
    def kodex_signal(self):
        if any(n.geltung is StrukturKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is StrukturKodexGeltung.STRUKTURFUNKTIONAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-strukturfunktional")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-strukturfunktional")


def build_struktur_kodex(
    klassen_charta: KlassenCharta | None = None,
    *,
    kodex_id: str = "struktur-kodex",
) -> StrukturKodex:
    if klassen_charta is None:
        klassen_charta = build_klassen_charta(charta_id=f"{kodex_id}-charta")

    normen: list[StrukturKodexNorm] = []
    for parent_norm in klassen_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.klassen_charta_id.removeprefix(f'{klassen_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.klassen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.klassen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL)
        normen.append(
            StrukturKodexNorm(
                struktur_kodex_id=new_id,
                struktur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                struktur_weight=new_weight,
                struktur_tier=new_tier,
                canonical=is_canonical,
                struktur_ids=parent_norm.klassen_ids + (new_id,),
                struktur_tags=parent_norm.klassen_tags + (f"struktur-kodex:{new_geltung.value}",),
            )
        )
    return StrukturKodex(
        kodex_id=kodex_id,
        klassen_charta=klassen_charta,
        normen=tuple(normen),
    )
