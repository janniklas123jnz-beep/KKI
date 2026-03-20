"""
#308 ZerfallsNorm — Radioaktiver Zerfall als Governance-Norm der Transformation.
*_norm pattern: Container = ZerfallsNormSatz, Entry = ZerfallsNormEintrag
Geltungsstufen: GESPERRT / ZERFALLEN / GRUNDLEGEND_ZERFALLEN
Parent: RadioaktivitaetsSenat (#307)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .radioaktivitaets_senat import RadioaktivitaetsGeltung, RadioaktivitaetsSenat, build_radioaktivitaets_senat


# ---------------------------------------------------------------------------
# Geltung-Mapping
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[RadioaktivitaetsGeltung, "ZerfallsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RadioaktivitaetsGeltung.GESPERRT] = ZerfallsNormGeltung.GESPERRT
    _GELTUNG_MAP[RadioaktivitaetsGeltung.RADIOAKTIV] = ZerfallsNormGeltung.ZERFALLEN
    _GELTUNG_MAP[RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV] = ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ZerfallsNormTyp(Enum):
    SCHUTZ_ZERFALL = "schutz-zerfall"
    ORDNUNGS_ZERFALL = "ordnungs-zerfall"
    SOUVERAENITAETS_ZERFALL = "souveraenitaets-zerfall"


class ZerfallsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ZerfallsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    ZERFALLEN = "zerfallen"
    GRUNDLEGEND_ZERFALLEN = "grundlegend-zerfallen"


_init_map()

# ---------------------------------------------------------------------------
# Typ & Prozedur lookup
# ---------------------------------------------------------------------------

_TYP_MAP: dict[ZerfallsNormGeltung, ZerfallsNormTyp] = {
    ZerfallsNormGeltung.GESPERRT: ZerfallsNormTyp.SCHUTZ_ZERFALL,
    ZerfallsNormGeltung.ZERFALLEN: ZerfallsNormTyp.ORDNUNGS_ZERFALL,
    ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN: ZerfallsNormTyp.SOUVERAENITAETS_ZERFALL,
}

_PROZEDUR_MAP: dict[ZerfallsNormGeltung, ZerfallsNormProzedur] = {
    ZerfallsNormGeltung.GESPERRT: ZerfallsNormProzedur.NOTPROZEDUR,
    ZerfallsNormGeltung.ZERFALLEN: ZerfallsNormProzedur.REGELPROTOKOLL,
    ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN: ZerfallsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ZerfallsNormGeltung, float] = {
    ZerfallsNormGeltung.GESPERRT: 0.0,
    ZerfallsNormGeltung.ZERFALLEN: 0.04,
    ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN: 0.08,
}

_TIER_DELTA: dict[ZerfallsNormGeltung, int] = {
    ZerfallsNormGeltung.GESPERRT: 0,
    ZerfallsNormGeltung.ZERFALLEN: 1,
    ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses  (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZerfallsNormEintrag:
    norm_id: str
    zerfalls_norm_typ: ZerfallsNormTyp
    prozedur: ZerfallsNormProzedur
    geltung: ZerfallsNormGeltung
    zerfalls_norm_weight: float
    zerfalls_norm_tier: int
    canonical: bool
    zerfalls_norm_ids: tuple[str, ...]
    zerfalls_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZerfallsNormSatz:
    norm_id: str
    radioaktivitaets_senat: RadioaktivitaetsSenat
    normen: tuple[ZerfallsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ZerfallsNormGeltung.GESPERRT)

    @property
    def zerfallen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ZerfallsNormGeltung.ZERFALLEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN)

    @property
    def norm_signal(self):
        if any(n.geltung is ZerfallsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is ZerfallsNormGeltung.ZERFALLEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-zerfallen")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-zerfallen")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_zerfalls_norm(
    radioaktivitaets_senat: RadioaktivitaetsSenat | None = None,
    *,
    norm_id: str = "zerfalls-norm",
) -> ZerfallsNormSatz:
    if radioaktivitaets_senat is None:
        radioaktivitaets_senat = build_radioaktivitaets_senat(senat_id=f"{norm_id}-senat")

    normen: list[ZerfallsNormEintrag] = []
    for parent_norm in radioaktivitaets_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.radioaktivitaets_senat_id.removeprefix(f'{radioaktivitaets_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.radioaktivitaets_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.radioaktivitaets_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN)
        normen.append(
            ZerfallsNormEintrag(
                norm_id=new_id,
                zerfalls_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                zerfalls_norm_weight=new_weight,
                zerfalls_norm_tier=new_tier,
                canonical=is_canonical,
                zerfalls_norm_ids=parent_norm.radioaktivitaets_ids + (new_id,),
                zerfalls_norm_tags=parent_norm.radioaktivitaets_tags + (f"zerfalls-norm:{new_geltung.value}",),
            )
        )
    return ZerfallsNormSatz(
        norm_id=norm_id,
        radioaktivitaets_senat=radioaktivitaets_senat,
        normen=tuple(normen),
    )
