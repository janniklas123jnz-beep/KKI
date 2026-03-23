"""
#474 RationalismusKodex — Descartes cogito ergo sum, Leibniz Monadologie, Spinoza more geometrico.
Der kontinentale Rationalismus begründet Erkenntnis aus reiner Vernunft: Descartes'
methodischer Zweifel mündet im cogito ergo sum als unerschütterlichem Fundament.
Leibniz' Monadologie konstruiert eine prästabilierte Harmonie aus unteilbaren Substanzen.
Spinozas more geometrico deduziert Ethik und Metaphysik mit geometrischer Strenge aus Axiomen.
Leitsterns Terra-Schwarm folgt rationalistischen Ableitungsstrukturen: GESPERRT sichert
Axiome, RATIONALISTISCH ermöglicht Deduktionsketten, GRUNDLEGEND_RATIONALISTISCH synthetisiert.
Parent: EpistemologieCharta (#473)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .epistemologie_charta import (
    EpistemologieCharta,
    EpistemologieChartaGeltung,
    build_epistemologie_charta,
)

_GELTUNG_MAP: dict[EpistemologieChartaGeltung, "RationalismusKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EpistemologieChartaGeltung.GESPERRT] = RationalismusKodexGeltung.GESPERRT
    _GELTUNG_MAP[EpistemologieChartaGeltung.EPISTEMISCH] = RationalismusKodexGeltung.RATIONALISTISCH
    _GELTUNG_MAP[EpistemologieChartaGeltung.GRUNDLEGEND_EPISTEMISCH] = RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH


class RationalismusKodexTyp(Enum):
    SCHUTZ_RATIONALISMUS = "schutz-rationalismus"
    ORDNUNGS_RATIONALISMUS = "ordnungs-rationalismus"
    SOUVERAENITAETS_RATIONALISMUS = "souveraenitaets-rationalismus"


class RationalismusKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RationalismusKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    RATIONALISTISCH = "rationalistisch"
    GRUNDLEGEND_RATIONALISTISCH = "grundlegend-rationalistisch"


_init_map()

_TYP_MAP = {
    RationalismusKodexGeltung.GESPERRT: RationalismusKodexTyp.SCHUTZ_RATIONALISMUS,
    RationalismusKodexGeltung.RATIONALISTISCH: RationalismusKodexTyp.ORDNUNGS_RATIONALISMUS,
    RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH: RationalismusKodexTyp.SOUVERAENITAETS_RATIONALISMUS,
}
_PROZEDUR_MAP = {
    RationalismusKodexGeltung.GESPERRT: RationalismusKodexProzedur.NOTPROZEDUR,
    RationalismusKodexGeltung.RATIONALISTISCH: RationalismusKodexProzedur.REGELPROTOKOLL,
    RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH: RationalismusKodexProzedur.PLENARPROTOKOLL,
}
_WEIGHT_DELTA = {
    RationalismusKodexGeltung.GESPERRT: 0.0,
    RationalismusKodexGeltung.RATIONALISTISCH: 0.04,
    RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH: 0.08,
}
_TIER_DELTA = {
    RationalismusKodexGeltung.GESPERRT: 0,
    RationalismusKodexGeltung.RATIONALISTISCH: 1,
    RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH: 2,
}


@dataclass(frozen=True)
class RationalismusKodexNorm:
    rationalismus_kodex_id: str
    rationalismus_typ: RationalismusKodexTyp
    prozedur: RationalismusKodexProzedur
    geltung: RationalismusKodexGeltung
    rationalismus_weight: float
    rationalismus_tier: int
    canonical: bool
    rationalismus_ids: tuple[str, ...]
    rationalismus_tags: tuple[str, ...]


@dataclass(frozen=True)
class RationalismusKodex:
    kodex_id: str
    epistemologie_charta: EpistemologieCharta
    normen: tuple[RationalismusKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rationalismus_kodex_id for n in self.normen if n.geltung is RationalismusKodexGeltung.GESPERRT)

    @property
    def rationalistisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rationalismus_kodex_id for n in self.normen if n.geltung is RationalismusKodexGeltung.RATIONALISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rationalismus_kodex_id for n in self.normen if n.geltung is RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH)

    @property
    def kodex_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is RationalismusKodexGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is RationalismusKodexGeltung.RATIONALISTISCH for n in self.normen):
            return SimpleNamespace(status="kodex-rationalistisch")
        return SimpleNamespace(status="kodex-grundlegend-rationalistisch")


def build_rationalismus_kodex(
    epistemologie_charta: EpistemologieCharta | None = None,
    *,
    kodex_id: str = "rationalismus-kodex",
) -> RationalismusKodex:
    if epistemologie_charta is None:
        epistemologie_charta = build_epistemologie_charta(charta_id=f"{kodex_id}-charta")
    normen: list[RationalismusKodexNorm] = []
    for parent_norm in epistemologie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.epistemologie_charta_id.removeprefix(f'{epistemologie_charta.charta_id}-')}"
        is_canonical = parent_norm.canonical and (new_geltung is RationalismusKodexGeltung.GRUNDLEGEND_RATIONALISTISCH)
        normen.append(RationalismusKodexNorm(
            rationalismus_kodex_id=new_id,
            rationalismus_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            rationalismus_weight=round(min(1.0, parent_norm.epistemologie_weight + _WEIGHT_DELTA[new_geltung]), 3),
            rationalismus_tier=parent_norm.epistemologie_tier + _TIER_DELTA[new_geltung],
            canonical=is_canonical,
            rationalismus_ids=parent_norm.epistemologie_ids + (new_id,),
            rationalismus_tags=parent_norm.epistemologie_tags + (f"rationalismus-kodex:{new_geltung.value}",),
        ))
    return RationalismusKodex(kodex_id=kodex_id, epistemologie_charta=epistemologie_charta, normen=tuple(normen))
