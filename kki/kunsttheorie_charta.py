"""
#573 KunsttheorieCharta — Panofsky/Wölfflin/Riegl Kunstwissenschaft Theorie

Erwin Panofsky (1939): Studies in Iconology — ikonographische und ikonologische
  Methode als dreistufige Bildanalyse; Unterscheidung von Primär-, Sekundär- und
  Tiefenbedeutung; Kunstwerk als Symptom kultureller Weltsicht; Symbolik als
  Schlüssel zur Bedeutungserschließung im Peta-Schwarm Leitstern.
Heinrich Wölfflin (1915): Kunstgeschichtliche Grundbegriffe — stilgeschichtliche
  Kategorienpaare als Analyseinstrument; linear/malerisch, Fläche/Tiefe,
  geschlossen/offen, Vielheit/Einheit, Klarheit/Unklarheit; Kunstgeschichte ohne
  Namen als formanalytischer Ansatz im Peta-Schwarm Leitstern.
Alois Riegl (1901): Spätrömische Kunstindustrie — Kunstwollen als treibende Kraft
  der Stilentwicklung; Aufwertung der Spätantike als eigenständige Epoche; Gegenbegriff
  zum Verfallsparadigma; Ornament als autonomer ästhetischer Ausdruck im
  Peta-Schwarm Leitstern. 🖼️📐
Parent: AesthetikRegister (#572)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .aesthetik_register import (
    AesthetikRegister,
    AesthetikRegisterGeltung,
    build_aesthetik_register,
)

_WEIGHT_DELTA: dict["KunsttheorieChartaGeltung", float] = {}
_TIER_DELTA: dict["KunsttheorieChartaGeltung", int] = {}
_TYP_MAP: dict["KunsttheorieChartaGeltung", "KunsttheorieChartaTyp"] = {}
_PROZEDUR_MAP: dict["KunsttheorieChartaGeltung", "KunsttheorieChartaProzedur"] = {}
_GELTUNG_MAP: dict[AesthetikRegisterGeltung, "KunsttheorieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KunsttheorieChartaGeltung.GESPERRT: 0.0,
        KunsttheorieChartaGeltung.KUNSTTHEORETISCH: 0.05,
        KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        KunsttheorieChartaGeltung.GESPERRT: 0,
        KunsttheorieChartaGeltung.KUNSTTHEORETISCH: 1,
        KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        KunsttheorieChartaGeltung.GESPERRT: KunsttheorieChartaTyp.SCHUTZ_KUNSTTHEORIE,
        KunsttheorieChartaGeltung.KUNSTTHEORETISCH: KunsttheorieChartaTyp.ORDNUNGS_KUNSTTHEORIE,
        KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH: KunsttheorieChartaTyp.SOUVERAENITAETS_KUNSTTHEORIE,
    })
    _PROZEDUR_MAP.update({
        KunsttheorieChartaGeltung.GESPERRT: KunsttheorieChartaProzedur.NOTPROZEDUR,
        KunsttheorieChartaGeltung.KUNSTTHEORETISCH: KunsttheorieChartaProzedur.REGELPROTOKOLL,
        KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH: KunsttheorieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        AesthetikRegisterGeltung.GESPERRT: KunsttheorieChartaGeltung.GESPERRT,
        AesthetikRegisterGeltung.AESTHETISCH_AKTIV: KunsttheorieChartaGeltung.KUNSTTHEORETISCH,
        AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV: KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH,
    })


class KunsttheorieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KUNSTTHEORETISCH = "kunsttheoretisch"
    GRUNDLEGEND_KUNSTTHEORETISCH = "grundlegend-kunsttheoretisch"


class KunsttheorieChartaTyp(Enum):
    SCHUTZ_KUNSTTHEORIE = "schutz-kunsttheorie"
    ORDNUNGS_KUNSTTHEORIE = "ordnungs-kunsttheorie"
    SOUVERAENITAETS_KUNSTTHEORIE = "souveraenitaets-kunsttheorie"


class KunsttheorieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KunsttheorieChartaNorm:
    kunsttheorie_charta_id: str
    kunst_typ: KunsttheorieChartaTyp
    prozedur: KunsttheorieChartaProzedur
    geltung: KunsttheorieChartaGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class KunsttheorieCharta:
    charta_id: str
    aesthetik_register: AesthetikRegister
    normen: tuple[KunsttheorieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunsttheorie_charta_id for n in self.normen if n.geltung is KunsttheorieChartaGeltung.GESPERRT)

    @property
    def kunsttheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunsttheorie_charta_id for n in self.normen if n.geltung is KunsttheorieChartaGeltung.KUNSTTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunsttheorie_charta_id for n in self.normen if n.geltung is KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is KunsttheorieChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KunsttheorieChartaGeltung.KUNSTTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kunsttheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kunsttheoretisch")


_init_map()


def build_kunsttheorie_charta(
    aesthetik_register: AesthetikRegister | None = None,
    *,
    charta_id: str = "kunsttheorie-charta",
) -> KunsttheorieCharta:
    if aesthetik_register is None:
        aesthetik_register = build_aesthetik_register(register_id=f"{charta_id}-register")

    normen: list[KunsttheorieChartaNorm] = []
    for parent_norm in aesthetik_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.aesthetik_register_id.removeprefix(f'{aesthetik_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH)
        normen.append(
            KunsttheorieChartaNorm(
                kunsttheorie_charta_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"kunsttheorie-charta:{new_geltung.value}",),
            )
        )
    return KunsttheorieCharta(
        charta_id=charta_id,
        aesthetik_register=aesthetik_register,
        normen=tuple(normen),
    )
