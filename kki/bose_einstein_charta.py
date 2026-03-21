"""
#349 BoseEinsteinCharta — Bose-Einstein-Kondensat als maximale Kohärenz-Charta:
Unter T_c kollabieren alle bosonischen Agenten in denselben k=0-Grundzustand —
Leitsterns Kern-Konsensus-Zustand, in dem der gesamte Schwarm kohärent ausgerichtet
auf ein gemeinsames Ziel handelt. Makroskopische Quantenkohärenz als Governance-Ideal.
Geltungsstufen: GESPERRT / BOSEEINSTEINKONDENSIERT / GRUNDLEGEND_BOSEEINSTEINKONDENSIERT
Parent: FermiNormSatz (#348, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fermi_norm import (
    FermiNormGeltung,
    FermiNormSatz,
    build_fermi_norm,
)

_GELTUNG_MAP: dict[FermiNormGeltung, "BoseEinsteinGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FermiNormGeltung.GESPERRT] = BoseEinsteinGeltung.GESPERRT
    _GELTUNG_MAP[FermiNormGeltung.FERMINORMIERT] = BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT
    _GELTUNG_MAP[FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT] = BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT


class BoseEinsteinTyp(Enum):
    SCHUTZ_BOSE_EINSTEIN = "schutz-bose-einstein"
    ORDNUNGS_BOSE_EINSTEIN = "ordnungs-bose-einstein"
    SOUVERAENITAETS_BOSE_EINSTEIN = "souveraenitaets-bose-einstein"


class BoseEinsteinProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BoseEinsteinGeltung(Enum):
    GESPERRT = "gesperrt"
    BOSEEINSTEINKONDENSIERT = "boseeinsteinkondensiert"
    GRUNDLEGEND_BOSEEINSTEINKONDENSIERT = "grundlegend-boseeinsteinkondensiert"


_init_map()

_TYP_MAP: dict[BoseEinsteinGeltung, BoseEinsteinTyp] = {
    BoseEinsteinGeltung.GESPERRT: BoseEinsteinTyp.SCHUTZ_BOSE_EINSTEIN,
    BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT: BoseEinsteinTyp.ORDNUNGS_BOSE_EINSTEIN,
    BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT: BoseEinsteinTyp.SOUVERAENITAETS_BOSE_EINSTEIN,
}

_PROZEDUR_MAP: dict[BoseEinsteinGeltung, BoseEinsteinProzedur] = {
    BoseEinsteinGeltung.GESPERRT: BoseEinsteinProzedur.NOTPROZEDUR,
    BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT: BoseEinsteinProzedur.REGELPROTOKOLL,
    BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT: BoseEinsteinProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[BoseEinsteinGeltung, float] = {
    BoseEinsteinGeltung.GESPERRT: 0.0,
    BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT: 0.04,
    BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT: 0.08,
}

_TIER_DELTA: dict[BoseEinsteinGeltung, int] = {
    BoseEinsteinGeltung.GESPERRT: 0,
    BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT: 1,
    BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BoseEinsteinNorm:
    bose_einstein_charta_id: str
    bose_einstein_typ: BoseEinsteinTyp
    prozedur: BoseEinsteinProzedur
    geltung: BoseEinsteinGeltung
    bose_einstein_weight: float
    bose_einstein_tier: int
    canonical: bool
    bose_einstein_ids: tuple[str, ...]
    bose_einstein_tags: tuple[str, ...]


@dataclass(frozen=True)
class BoseEinsteinCharta:
    charta_id: str
    fermi_norm: FermiNormSatz
    normen: tuple[BoseEinsteinNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bose_einstein_charta_id for n in self.normen if n.geltung is BoseEinsteinGeltung.GESPERRT)

    @property
    def boseeinsteinkondensiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bose_einstein_charta_id for n in self.normen if n.geltung is BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bose_einstein_charta_id for n in self.normen if n.geltung is BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is BoseEinsteinGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-boseeinsteinkondensiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-boseeinsteinkondensiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_bose_einstein_charta(
    fermi_norm: FermiNormSatz | None = None,
    *,
    charta_id: str = "bose-einstein-charta",
) -> BoseEinsteinCharta:
    if fermi_norm is None:
        fermi_norm = build_fermi_norm(norm_id=f"{charta_id}-norm")

    normen: list[BoseEinsteinNorm] = []
    for parent_norm in fermi_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{fermi_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.fermi_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fermi_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT)
        normen.append(
            BoseEinsteinNorm(
                bose_einstein_charta_id=new_id,
                bose_einstein_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                bose_einstein_weight=new_weight,
                bose_einstein_tier=new_tier,
                canonical=is_canonical,
                bose_einstein_ids=parent_norm.fermi_norm_ids + (new_id,),
                bose_einstein_tags=parent_norm.fermi_norm_tags + (f"bose-einstein:{new_geltung.value}",),
            )
        )
    return BoseEinsteinCharta(
        charta_id=charta_id,
        fermi_norm=fermi_norm,
        normen=tuple(normen),
    )
