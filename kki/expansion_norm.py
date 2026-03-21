"""
#328 ExpansionNorm — Hubble-Expansion als normiertes Wachstumsprotokoll (*_norm-Muster).
*_norm pattern: Container = ExpansionNormSatz, Entry = ExpansionNormEintrag
Geltungsstufen: GESPERRT / EXPANSIONSNORMIERT / GRUNDLEGEND_EXPANSIONSNORMIERT
Parent: StrukturbildungsSenat (#327)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .strukturbildungs_senat import (
    StrukturbildungsGeltung,
    StrukturbildungsSenat,
    build_strukturbildungs_senat,
)

_GELTUNG_MAP: dict[StrukturbildungsGeltung, "ExpansionNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[StrukturbildungsGeltung.GESPERRT] = ExpansionNormGeltung.GESPERRT
    _GELTUNG_MAP[StrukturbildungsGeltung.STRUKTURBILDEND] = ExpansionNormGeltung.EXPANSIONSNORMIERT
    _GELTUNG_MAP[StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND] = ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT


class ExpansionNormTyp(Enum):
    SCHUTZ_EXPANSION = "schutz-expansion"
    ORDNUNGS_EXPANSION = "ordnungs-expansion"
    SOUVERAENITAETS_EXPANSION = "souveraenitaets-expansion"


class ExpansionNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ExpansionNormGeltung(Enum):
    GESPERRT = "gesperrt"
    EXPANSIONSNORMIERT = "expansionsnormiert"
    GRUNDLEGEND_EXPANSIONSNORMIERT = "grundlegend-expansionsnormiert"


_init_map()

_TYP_MAP: dict[ExpansionNormGeltung, ExpansionNormTyp] = {
    ExpansionNormGeltung.GESPERRT: ExpansionNormTyp.SCHUTZ_EXPANSION,
    ExpansionNormGeltung.EXPANSIONSNORMIERT: ExpansionNormTyp.ORDNUNGS_EXPANSION,
    ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT: ExpansionNormTyp.SOUVERAENITAETS_EXPANSION,
}

_PROZEDUR_MAP: dict[ExpansionNormGeltung, ExpansionNormProzedur] = {
    ExpansionNormGeltung.GESPERRT: ExpansionNormProzedur.NOTPROZEDUR,
    ExpansionNormGeltung.EXPANSIONSNORMIERT: ExpansionNormProzedur.REGELPROTOKOLL,
    ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT: ExpansionNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ExpansionNormGeltung, float] = {
    ExpansionNormGeltung.GESPERRT: 0.0,
    ExpansionNormGeltung.EXPANSIONSNORMIERT: 0.04,
    ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT: 0.08,
}

_TIER_DELTA: dict[ExpansionNormGeltung, int] = {
    ExpansionNormGeltung.GESPERRT: 0,
    ExpansionNormGeltung.EXPANSIONSNORMIERT: 1,
    ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses  (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExpansionNormEintrag:
    norm_id: str
    expansion_norm_typ: ExpansionNormTyp
    prozedur: ExpansionNormProzedur
    geltung: ExpansionNormGeltung
    expansion_norm_weight: float
    expansion_norm_tier: int
    canonical: bool
    expansion_norm_ids: tuple[str, ...]
    expansion_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class ExpansionNormSatz:
    norm_id: str
    strukturbildungs_senat: StrukturbildungsSenat
    normen: tuple[ExpansionNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ExpansionNormGeltung.GESPERRT)

    @property
    def expansionsnormiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ExpansionNormGeltung.EXPANSIONSNORMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT)

    @property
    def norm_signal(self):
        if any(n.geltung is ExpansionNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is ExpansionNormGeltung.EXPANSIONSNORMIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-expansionsnormiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-expansionsnormiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_expansion_norm(
    strukturbildungs_senat: StrukturbildungsSenat | None = None,
    *,
    norm_id: str = "expansion-norm",
) -> ExpansionNormSatz:
    if strukturbildungs_senat is None:
        strukturbildungs_senat = build_strukturbildungs_senat(senat_id=f"{norm_id}-senat")

    normen: list[ExpansionNormEintrag] = []
    for parent_norm in strukturbildungs_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.strukturbildungs_senat_id.removeprefix(f'{strukturbildungs_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.strukturbildungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.strukturbildungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT)
        normen.append(
            ExpansionNormEintrag(
                norm_id=new_id,
                expansion_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                expansion_norm_weight=new_weight,
                expansion_norm_tier=new_tier,
                canonical=is_canonical,
                expansion_norm_ids=parent_norm.strukturbildungs_ids + (new_id,),
                expansion_norm_tags=parent_norm.strukturbildungs_tags + (f"expansion-norm:{new_geltung.value}",),
            )
        )
    return ExpansionNormSatz(
        norm_id=norm_id,
        strukturbildungs_senat=strukturbildungs_senat,
        normen=tuple(normen),
    )
