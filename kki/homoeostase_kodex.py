"""
#484 HomoeostaseKodex — Cannon: innere Balance als Grundbedingung lebender Systeme.
Walter Cannon (1932): The Wisdom of the Body — Homöostase als dynamisches Gleichgewicht;
  physiologische Regelkreise halten Kernparameter in lebensfähigen Grenzen.
W. Ross Ashby (1960): Design for a Brain — Ultrastabilität und adaptive Regelung;
  ein System mit mehreren Gleichgewichtszuständen wechselt bei Überlastung das Regime.
Gregory Bateson (1972): Ökologie des Geistes — Informationsmuster verbinden Organismus
  und Umwelt; Differenz als Grundelement aller Kommunikation und Kognition.
Leitsterns Terra-Schwarm kodifiziert Gleichgewicht: GESPERRT bewahrt Kernhomöostase,
HOMOEOSTATISCH ermöglicht adaptive Selbstregulation, GRUNDLEGEND_HOMOEOSTATISCH
synthetisiert ultrastabile Resilienz über alle Schwarmschichten.
Parent: AutopoiesisCharta (#483)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .autopoiesis_charta import (
    AutopoiesisCharta,
    AutopoiesisChartaGeltung,
    build_autopoiesis_charta,
)

_GELTUNG_MAP: dict[AutopoiesisChartaGeltung, "HomoeostaseKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AutopoiesisChartaGeltung.GESPERRT] = HomoeostaseKodexGeltung.GESPERRT
    _GELTUNG_MAP[AutopoiesisChartaGeltung.AUTOPOIETISCH] = HomoeostaseKodexGeltung.HOMOEOSTATISCH
    _GELTUNG_MAP[AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH] = HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH


class HomoeostaseKodexTyp(Enum):
    SCHUTZ_HOMOEOSTASE = "schutz-homoeostase"
    ORDNUNGS_HOMOEOSTASE = "ordnungs-homoeostase"
    SOUVERAENITAETS_HOMOEOSTASE = "souveraenitaets-homoeostase"


class HomoeostaseKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HomoeostaseKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    HOMOEOSTATISCH = "homoeostatisch"
    GRUNDLEGEND_HOMOEOSTATISCH = "grundlegend-homoeostatisch"


_init_map()

_TYP_MAP: dict[HomoeostaseKodexGeltung, HomoeostaseKodexTyp] = {
    HomoeostaseKodexGeltung.GESPERRT: HomoeostaseKodexTyp.SCHUTZ_HOMOEOSTASE,
    HomoeostaseKodexGeltung.HOMOEOSTATISCH: HomoeostaseKodexTyp.ORDNUNGS_HOMOEOSTASE,
    HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH: HomoeostaseKodexTyp.SOUVERAENITAETS_HOMOEOSTASE,
}

_PROZEDUR_MAP: dict[HomoeostaseKodexGeltung, HomoeostaseKodexProzedur] = {
    HomoeostaseKodexGeltung.GESPERRT: HomoeostaseKodexProzedur.NOTPROZEDUR,
    HomoeostaseKodexGeltung.HOMOEOSTATISCH: HomoeostaseKodexProzedur.REGELPROTOKOLL,
    HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH: HomoeostaseKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HomoeostaseKodexGeltung, float] = {
    HomoeostaseKodexGeltung.GESPERRT: 0.0,
    HomoeostaseKodexGeltung.HOMOEOSTATISCH: 0.04,
    HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH: 0.08,
}

_TIER_DELTA: dict[HomoeostaseKodexGeltung, int] = {
    HomoeostaseKodexGeltung.GESPERRT: 0,
    HomoeostaseKodexGeltung.HOMOEOSTATISCH: 1,
    HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH: 2,
}


@dataclass(frozen=True)
class HomoeostaseKodexNorm:
    homoeostase_kodex_id: str
    homoeostase_typ: HomoeostaseKodexTyp
    prozedur: HomoeostaseKodexProzedur
    geltung: HomoeostaseKodexGeltung
    homoeostase_weight: float
    homoeostase_tier: int
    canonical: bool
    homoeostase_ids: tuple[str, ...]
    homoeostase_tags: tuple[str, ...]


@dataclass(frozen=True)
class HomoeostaseKodex:
    kodex_id: str
    autopoiesis_charta: AutopoiesisCharta
    normen: tuple[HomoeostaseKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.homoeostase_kodex_id for n in self.normen if n.geltung is HomoeostaseKodexGeltung.GESPERRT)

    @property
    def homoeostatisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.homoeostase_kodex_id for n in self.normen if n.geltung is HomoeostaseKodexGeltung.HOMOEOSTATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.homoeostase_kodex_id for n in self.normen if n.geltung is HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is HomoeostaseKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is HomoeostaseKodexGeltung.HOMOEOSTATISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-homoeostatisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-homoeostatisch")


def build_homoeostase_kodex(
    autopoiesis_charta: AutopoiesisCharta | None = None,
    *,
    kodex_id: str = "homoeostase-kodex",
) -> HomoeostaseKodex:
    if autopoiesis_charta is None:
        autopoiesis_charta = build_autopoiesis_charta(charta_id=f"{kodex_id}-charta")

    normen: list[HomoeostaseKodexNorm] = []
    for parent_norm in autopoiesis_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.autopoiesis_charta_id.removeprefix(f'{autopoiesis_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.autopoiesis_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.autopoiesis_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH)
        normen.append(
            HomoeostaseKodexNorm(
                homoeostase_kodex_id=new_id,
                homoeostase_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                homoeostase_weight=new_weight,
                homoeostase_tier=new_tier,
                canonical=is_canonical,
                homoeostase_ids=parent_norm.autopoiesis_ids + (new_id,),
                homoeostase_tags=parent_norm.autopoiesis_tags + (f"homoeostase-kodex:{new_geltung.value}",),
            )
        )
    return HomoeostaseKodex(
        kodex_id=kodex_id,
        autopoiesis_charta=autopoiesis_charta,
        normen=tuple(normen),
    )
