"""
#523 KapitalCharta — Marx/Engels/Piketty Kapital als gesellschaftliches Verhältnis

Karl Marx (1867): Das Kapital — Kapital als gesellschaftliches Verhältnis, nicht als Ding;
  Mehrwerttheorie und Ausbeutung der Arbeitskraft; Akkumulationsdynamik und Konzentration
  des Kapitals als systemische Tendenz im Schwarm.
Friedrich Engels (1845): Die Lage der arbeitenden Klasse in England — materielle Basis
  der Produktionsverhältnisse; Klassenwiderspruch als Motor des historischen Wandels;
  kollektive Organisation als Gegengewicht zur Kapitalkonzentration.
Thomas Piketty (2013): Kapital im 21. Jahrhundert — empirische Analyse der
  Ungleichheitsdynamik; r > g als fundamentales Gesetz der Kapitalakkumulation;
  globales Kapitalregister und Vermögenssteuer als Regulierungsinstrument im Schwarm.
Rudolf Hilferding (1910): Das Finanzkapital — Verschmelzung von Industrie- und
  Bankkapital; Monopolisierungstendenzen; Imperialismus als Exportform von Kapital. 💹
Module #523, Parent: MarktRegister (#522)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .markt_register import (
    MarktRegister,
    MarktRegisterGeltung,
    build_markt_register,
)

_WEIGHT_DELTA: dict["KapitalChartaGeltung", float] = {}
_TIER_DELTA: dict["KapitalChartaGeltung", int] = {}
_TYP_MAP: dict["KapitalChartaGeltung", "KapitalChartaTyp"] = {}
_PROZEDUR_MAP: dict["KapitalChartaGeltung", "KapitalChartaProzedur"] = {}
_GELTUNG_MAP: dict[MarktRegisterGeltung, "KapitalChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KapitalChartaGeltung.GESPERRT: 0.0,
        KapitalChartaGeltung.KAPITALISTISCH: 0.05,
        KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH: 0.1,
    })
    _TIER_DELTA.update({
        KapitalChartaGeltung.GESPERRT: 0,
        KapitalChartaGeltung.KAPITALISTISCH: 1,
        KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH: 2,
    })
    _TYP_MAP.update({
        KapitalChartaGeltung.GESPERRT: KapitalChartaTyp.SCHUTZ_KAPITAL,
        KapitalChartaGeltung.KAPITALISTISCH: KapitalChartaTyp.ORDNUNGS_KAPITAL,
        KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH: KapitalChartaTyp.SOUVERAENITAETS_KAPITAL,
    })
    _PROZEDUR_MAP.update({
        KapitalChartaGeltung.GESPERRT: KapitalChartaProzedur.NOTPROZEDUR,
        KapitalChartaGeltung.KAPITALISTISCH: KapitalChartaProzedur.REGELPROTOKOLL,
        KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH: KapitalChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        MarktRegisterGeltung.GESPERRT: KapitalChartaGeltung.GESPERRT,
        MarktRegisterGeltung.MARKTLICH: KapitalChartaGeltung.KAPITALISTISCH,
        MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH: KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH,
    })


class KapitalChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KAPITALISTISCH = "kapitalistisch"
    GRUNDLEGEND_KAPITALISTISCH = "grundlegend-kapitalistisch"


class KapitalChartaTyp(Enum):
    SCHUTZ_KAPITAL = "schutz-kapital"
    ORDNUNGS_KAPITAL = "ordnungs-kapital"
    SOUVERAENITAETS_KAPITAL = "souveraenitaets-kapital"


class KapitalChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KapitalChartaNorm:
    kapital_charta_id: str
    kapital_typ: KapitalChartaTyp
    prozedur: KapitalChartaProzedur
    geltung: KapitalChartaGeltung
    kapital_weight: float
    kapital_tier: int
    canonical: bool
    kapital_ids: tuple[str, ...]
    kapital_tags: tuple[str, ...]


@dataclass(frozen=True)
class KapitalCharta:
    charta_id: str
    markt_register: MarktRegister
    normen: tuple[KapitalChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kapital_charta_id for n in self.normen if n.geltung is KapitalChartaGeltung.GESPERRT)

    @property
    def kapitalistisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kapital_charta_id for n in self.normen if n.geltung is KapitalChartaGeltung.KAPITALISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kapital_charta_id for n in self.normen if n.geltung is KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is KapitalChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KapitalChartaGeltung.KAPITALISTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kapitalistisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kapitalistisch")


_init_map()


def build_kapital_charta(
    markt_register: MarktRegister | None = None,
    *,
    charta_id: str = "kapital-charta",
) -> KapitalCharta:
    if markt_register is None:
        markt_register = build_markt_register(
            register_id=f"{charta_id}-markt-register"
        )

    normen: list[KapitalChartaNorm] = []
    for parent_norm in markt_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.markt_register_id.removeprefix(f'{markt_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.markt_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.markt_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH)
        normen.append(
            KapitalChartaNorm(
                kapital_charta_id=new_id,
                kapital_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kapital_weight=new_weight,
                kapital_tier=new_tier,
                canonical=is_canonical,
                kapital_ids=parent_norm.markt_ids + (new_id,),
                kapital_tags=parent_norm.markt_tags + (f"kapital-charta:{new_geltung.value}",),
            )
        )
    return KapitalCharta(
        charta_id=charta_id,
        markt_register=markt_register,
        normen=tuple(normen),
    )
