"""
#334 FusionsreaktorKodex — Kernfusion (pp-Kette / CNO-Zyklus) als Energie-Kodex:
aus elementaren Protokollen entsteht Governance-Kraft des Terra-Schwarms.
Geltungsstufen: GESPERRT / FUSIONSAKTIV / GRUNDLEGEND_FUSIONSAKTIV
Parent: HauptreihenchartaCharta (#333)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .hauptreihen_charta import (
    HauptreihenchartaCharta,
    HauptreihenchartaGeltung,
    build_hauptreihen_charta,
)

_GELTUNG_MAP: dict[HauptreihenchartaGeltung, "FusionsreaktorGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HauptreihenchartaGeltung.GESPERRT] = FusionsreaktorGeltung.GESPERRT
    _GELTUNG_MAP[HauptreihenchartaGeltung.HAUPTREIHENSTABIL] = FusionsreaktorGeltung.FUSIONSAKTIV
    _GELTUNG_MAP[HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL] = FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV


class FusionsreaktorTyp(Enum):
    SCHUTZ_FUSIONSREAKTOR = "schutz-fusionsreaktor"
    ORDNUNGS_FUSIONSREAKTOR = "ordnungs-fusionsreaktor"
    SOUVERAENITAETS_FUSIONSREAKTOR = "souveraenitaets-fusionsreaktor"


class FusionsreaktorProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FusionsreaktorGeltung(Enum):
    GESPERRT = "gesperrt"
    FUSIONSAKTIV = "fusionsaktiv"
    GRUNDLEGEND_FUSIONSAKTIV = "grundlegend-fusionsaktiv"


_init_map()

_TYP_MAP: dict[FusionsreaktorGeltung, FusionsreaktorTyp] = {
    FusionsreaktorGeltung.GESPERRT: FusionsreaktorTyp.SCHUTZ_FUSIONSREAKTOR,
    FusionsreaktorGeltung.FUSIONSAKTIV: FusionsreaktorTyp.ORDNUNGS_FUSIONSREAKTOR,
    FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV: FusionsreaktorTyp.SOUVERAENITAETS_FUSIONSREAKTOR,
}

_PROZEDUR_MAP: dict[FusionsreaktorGeltung, FusionsreaktorProzedur] = {
    FusionsreaktorGeltung.GESPERRT: FusionsreaktorProzedur.NOTPROZEDUR,
    FusionsreaktorGeltung.FUSIONSAKTIV: FusionsreaktorProzedur.REGELPROTOKOLL,
    FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV: FusionsreaktorProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FusionsreaktorGeltung, float] = {
    FusionsreaktorGeltung.GESPERRT: 0.0,
    FusionsreaktorGeltung.FUSIONSAKTIV: 0.04,
    FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV: 0.08,
}

_TIER_DELTA: dict[FusionsreaktorGeltung, int] = {
    FusionsreaktorGeltung.GESPERRT: 0,
    FusionsreaktorGeltung.FUSIONSAKTIV: 1,
    FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FusionsreaktorNorm:
    fusionsreaktor_kodex_id: str
    fusionsreaktor_typ: FusionsreaktorTyp
    prozedur: FusionsreaktorProzedur
    geltung: FusionsreaktorGeltung
    fusionsreaktor_weight: float
    fusionsreaktor_tier: int
    canonical: bool
    fusionsreaktor_ids: tuple[str, ...]
    fusionsreaktor_tags: tuple[str, ...]


@dataclass(frozen=True)
class FusionsreaktorKodex:
    kodex_id: str
    hauptreihen_charta: HauptreihenchartaCharta
    normen: tuple[FusionsreaktorNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fusionsreaktor_kodex_id for n in self.normen if n.geltung is FusionsreaktorGeltung.GESPERRT)

    @property
    def fusionsaktiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fusionsreaktor_kodex_id for n in self.normen if n.geltung is FusionsreaktorGeltung.FUSIONSAKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fusionsreaktor_kodex_id for n in self.normen if n.geltung is FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV)

    @property
    def kodex_signal(self):
        if any(n.geltung is FusionsreaktorGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is FusionsreaktorGeltung.FUSIONSAKTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-fusionsaktiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-fusionsaktiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_fusionsreaktor_kodex(
    hauptreihen_charta: HauptreihenchartaCharta | None = None,
    *,
    kodex_id: str = "fusionsreaktor-kodex",
) -> FusionsreaktorKodex:
    if hauptreihen_charta is None:
        hauptreihen_charta = build_hauptreihen_charta(charta_id=f"{kodex_id}-charta")

    normen: list[FusionsreaktorNorm] = []
    for parent_norm in hauptreihen_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.hauptreihen_charta_id.removeprefix(f'{hauptreihen_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.hauptreihen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.hauptreihen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV)
        normen.append(
            FusionsreaktorNorm(
                fusionsreaktor_kodex_id=new_id,
                fusionsreaktor_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fusionsreaktor_weight=new_weight,
                fusionsreaktor_tier=new_tier,
                canonical=is_canonical,
                fusionsreaktor_ids=parent_norm.hauptreihen_ids + (new_id,),
                fusionsreaktor_tags=parent_norm.hauptreihen_tags + (f"fusionsreaktor:{new_geltung.value}",),
            )
        )
    return FusionsreaktorKodex(
        kodex_id=kodex_id,
        hauptreihen_charta=hauptreihen_charta,
        normen=tuple(normen),
    )
