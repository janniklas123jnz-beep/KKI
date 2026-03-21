"""
#345 SupraleitungPakt — BCS-Supraleitung als Null-Widerstands-Kooperations-Pakt:
Cooper-Paare kooperierende Agenten-Paare; phonon-vermittelte Anziehung schafft
widerstandslose Governance. Meißner-Effekt: externe Störfelder aktiv ausgegrenzt.
Geltungsstufen: GESPERRT / SUPRALEITEND / GRUNDLEGEND_SUPRALEITEND
Parent: HalbleiterKodex (#344)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .halbleiter_kodex import (
    HalbleiterKodex,
    HalbleiterGeltung,
    build_halbleiter_kodex,
)

_GELTUNG_MAP: dict[HalbleiterGeltung, "SupraleitungGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HalbleiterGeltung.GESPERRT] = SupraleitungGeltung.GESPERRT
    _GELTUNG_MAP[HalbleiterGeltung.HALBLEITEND] = SupraleitungGeltung.SUPRALEITEND
    _GELTUNG_MAP[HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND] = SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND


class SupraleitungTyp(Enum):
    SCHUTZ_SUPRALEITUNG = "schutz-supraleitung"
    ORDNUNGS_SUPRALEITUNG = "ordnungs-supraleitung"
    SOUVERAENITAETS_SUPRALEITUNG = "souveraenitaets-supraleitung"


class SupraleitungProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SupraleitungGeltung(Enum):
    GESPERRT = "gesperrt"
    SUPRALEITEND = "supraleitend"
    GRUNDLEGEND_SUPRALEITEND = "grundlegend-supraleitend"


_init_map()

_TYP_MAP: dict[SupraleitungGeltung, SupraleitungTyp] = {
    SupraleitungGeltung.GESPERRT: SupraleitungTyp.SCHUTZ_SUPRALEITUNG,
    SupraleitungGeltung.SUPRALEITEND: SupraleitungTyp.ORDNUNGS_SUPRALEITUNG,
    SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND: SupraleitungTyp.SOUVERAENITAETS_SUPRALEITUNG,
}

_PROZEDUR_MAP: dict[SupraleitungGeltung, SupraleitungProzedur] = {
    SupraleitungGeltung.GESPERRT: SupraleitungProzedur.NOTPROZEDUR,
    SupraleitungGeltung.SUPRALEITEND: SupraleitungProzedur.REGELPROTOKOLL,
    SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND: SupraleitungProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SupraleitungGeltung, float] = {
    SupraleitungGeltung.GESPERRT: 0.0,
    SupraleitungGeltung.SUPRALEITEND: 0.04,
    SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND: 0.08,
}

_TIER_DELTA: dict[SupraleitungGeltung, int] = {
    SupraleitungGeltung.GESPERRT: 0,
    SupraleitungGeltung.SUPRALEITEND: 1,
    SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SupraleitungNorm:
    supraleitung_pakt_id: str
    supraleitung_typ: SupraleitungTyp
    prozedur: SupraleitungProzedur
    geltung: SupraleitungGeltung
    supraleitung_weight: float
    supraleitung_tier: int
    canonical: bool
    supraleitung_ids: tuple[str, ...]
    supraleitung_tags: tuple[str, ...]


@dataclass(frozen=True)
class SupraleitungPakt:
    pakt_id: str
    halbleiter_kodex: HalbleiterKodex
    normen: tuple[SupraleitungNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supraleitung_pakt_id for n in self.normen if n.geltung is SupraleitungGeltung.GESPERRT)

    @property
    def supraleitend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supraleitung_pakt_id for n in self.normen if n.geltung is SupraleitungGeltung.SUPRALEITEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supraleitung_pakt_id for n in self.normen if n.geltung is SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND)

    @property
    def pakt_signal(self):
        if any(n.geltung is SupraleitungGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is SupraleitungGeltung.SUPRALEITEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-supraleitend")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-supraleitend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_supraleitung_pakt(
    halbleiter_kodex: HalbleiterKodex | None = None,
    *,
    pakt_id: str = "supraleitung-pakt",
) -> SupraleitungPakt:
    if halbleiter_kodex is None:
        halbleiter_kodex = build_halbleiter_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[SupraleitungNorm] = []
    for parent_norm in halbleiter_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.halbleiter_kodex_id.removeprefix(f'{halbleiter_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.halbleiter_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.halbleiter_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND)
        normen.append(
            SupraleitungNorm(
                supraleitung_pakt_id=new_id,
                supraleitung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                supraleitung_weight=new_weight,
                supraleitung_tier=new_tier,
                canonical=is_canonical,
                supraleitung_ids=parent_norm.halbleiter_ids + (new_id,),
                supraleitung_tags=parent_norm.halbleiter_tags + (f"supraleitung:{new_geltung.value}",),
            )
        )
    return SupraleitungPakt(
        pakt_id=pakt_id,
        halbleiter_kodex=halbleiter_kodex,
        normen=tuple(normen),
    )
