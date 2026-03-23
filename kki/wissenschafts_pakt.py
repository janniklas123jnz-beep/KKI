"""
#475 WissenschaftsPakt — Popper: Falsifikation, Kritischer Rationalismus, Demarkationsproblem.
Karl Poppers Kritischer Rationalismus definiert Wissenschaftlichkeit durch Falsifizierbarkeit:
Eine Theorie ist wissenschaftlich, wenn sie prinzipiell widerlegbar ist. Das Demarkationsproblem
trennt Wissenschaft von Pseudowissenschaft. Die hypothetisch-deduktive Methode leitet aus
Theorien prüfbare Vorhersagen ab. Leitsterns Terra-Schwarm prüft Hypothesen systematisch:
GESPERRT sichert Kerntheorien, WISSENSCHAFTLICH ermöglicht Falsifikationstests,
GRUNDLEGEND_WISSENSCHAFTLICH synthetisiert wissenschaftliche Erkenntnisfortschritte.
Parent: RationalismusKodex (#474)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rationalismus_kodex import (
    RationalismusKodex,
    RationalismusKodexGeltung,
    build_rationalismus_kodex,
)

_GELTUNG_MAP: dict[RationalismusKodexGeltung, "WissenschaftsPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RationalismusKodexGeltung.GESPERRT] = WissenschaftsPaktGeltung.GESPERRT
    _GELTUNG_MAP[RationalismusKodexGeltung.RATIONALISTISCH] = WissenschaftsPaktGeltung.WISSENSCHAFTLICH
    _GELTUNG_MAP[RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH] = WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH


class WissenschaftsPaktTyp(Enum):
    SCHUTZ_WISSENSCHAFT = "schutz-wissenschaft"
    ORDNUNGS_WISSENSCHAFT = "ordnungs-wissenschaft"
    SOUVERAENITAETS_WISSENSCHAFT = "souveraenitaets-wissenschaft"


class WissenschaftsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WissenschaftsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    WISSENSCHAFTLICH = "wissenschaftlich"
    GRUNDLEGEND_WISSENSCHAFTLICH = "grundlegend-wissenschaftlich"


_init_map()

_TYP_MAP = {
    WissenschaftsPaktGeltung.GESPERRT: WissenschaftsPaktTyp.SCHUTZ_WISSENSCHAFT,
    WissenschaftsPaktGeltung.WISSENSCHAFTLICH: WissenschaftsPaktTyp.ORDNUNGS_WISSENSCHAFT,
    WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH: WissenschaftsPaktTyp.SOUVERAENITAETS_WISSENSCHAFT,
}
_PROZEDUR_MAP = {
    WissenschaftsPaktGeltung.GESPERRT: WissenschaftsPaktProzedur.NOTPROZEDUR,
    WissenschaftsPaktGeltung.WISSENSCHAFTLICH: WissenschaftsPaktProzedur.REGELPROTOKOLL,
    WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH: WissenschaftsPaktProzedur.PLENARPROTOKOLL,
}
_WEIGHT_DELTA = {
    WissenschaftsPaktGeltung.GESPERRT: 0.0,
    WissenschaftsPaktGeltung.WISSENSCHAFTLICH: 0.04,
    WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH: 0.08,
}
_TIER_DELTA = {
    WissenschaftsPaktGeltung.GESPERRT: 0,
    WissenschaftsPaktGeltung.WISSENSCHAFTLICH: 1,
    WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH: 2,
}


@dataclass(frozen=True)
class WissenschaftsPaktNorm:
    wissenschafts_pakt_id: str
    wissenschafts_typ: WissenschaftsPaktTyp
    prozedur: WissenschaftsPaktProzedur
    geltung: WissenschaftsPaktGeltung
    wissenschafts_weight: float
    wissenschafts_tier: int
    canonical: bool
    wissenschafts_ids: tuple[str, ...]
    wissenschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class WissenschaftsPakt:
    pakt_id: str
    rationalismus_kodex: RationalismusKodex
    normen: tuple[WissenschaftsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wissenschafts_pakt_id for n in self.normen if n.geltung is WissenschaftsPaktGeltung.GESPERRT)

    @property
    def wissenschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wissenschafts_pakt_id for n in self.normen if n.geltung is WissenschaftsPaktGeltung.WISSENSCHAFTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wissenschafts_pakt_id for n in self.normen if n.geltung is WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH)

    @property
    def pakt_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is WissenschaftsPaktGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is WissenschaftsPaktGeltung.WISSENSCHAFTLICH for n in self.normen):
            return SimpleNamespace(status="pakt-wissenschaftlich")
        return SimpleNamespace(status="pakt-grundlegend-wissenschaftlich")


def build_wissenschafts_pakt(
    rationalismus_kodex: RationalismusKodex | None = None,
    *,
    pakt_id: str = "wissenschafts-pakt",
) -> WissenschaftsPakt:
    if rationalismus_kodex is None:
        rationalismus_kodex = build_rationalismus_kodex(kodex_id=f"{pakt_id}-kodex")
    normen: list[WissenschaftsPaktNorm] = []
    for parent_norm in rationalismus_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.rationalismus_kodex_id.removeprefix(f'{rationalismus_kodex.kodex_id}-')}"
        is_canonical = parent_norm.canonical and (new_geltung is WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH)
        normen.append(WissenschaftsPaktNorm(
            wissenschafts_pakt_id=new_id,
            wissenschafts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            wissenschafts_weight=round(min(1.0, parent_norm.rationalismus_weight + _WEIGHT_DELTA[new_geltung]), 3),
            wissenschafts_tier=parent_norm.rationalismus_tier + _TIER_DELTA[new_geltung],
            canonical=is_canonical,
            wissenschafts_ids=parent_norm.rationalismus_ids + (new_id,),
            wissenschafts_tags=parent_norm.rationalismus_tags + (f"wissenschafts-pakt:{new_geltung.value}",),
        ))
    return WissenschaftsPakt(pakt_id=pakt_id, rationalismus_kodex=rationalismus_kodex, normen=tuple(normen))
