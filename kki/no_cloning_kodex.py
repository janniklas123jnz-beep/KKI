"""
#379 NoCloningKodex — No-Cloning-Theorem (Wootters & Zurek 1982): Ein beliebiger
Quantenzustand |ψ⟩ kann nicht perfekt kopiert werden — |ψ⟩|0⟩ ≠ U|ψ⟩|ψ⟩ für alle |ψ⟩.
Leitsterns Agenten-Identitäten sind physikalisch einzigartig und unkopiebar.
Fälschung und unauthorisierte Replikation sind nicht nur verboten, sondern
durch fundamentale Quantenmechanik unmöglich.
Geltungsstufen: GESPERRT / NICHTKLONBAR / GRUNDLEGEND_NICHTKLONBAR
Parent: LandauerManifest (#378)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .landauer_manifest import (
    LandauerGeltung,
    LandauerManifest,
    build_landauer_manifest,
)

_GELTUNG_MAP: dict[LandauerGeltung, "NoCloningGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LandauerGeltung.GESPERRT] = NoCloningGeltung.GESPERRT
    _GELTUNG_MAP[LandauerGeltung.LANDAUERGEBUNDEN] = NoCloningGeltung.NICHTKLONBAR
    _GELTUNG_MAP[LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN] = NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR


class NoCloningTyp(Enum):
    SCHUTZ_NO_CLONING = "schutz-no-cloning"
    ORDNUNGS_NO_CLONING = "ordnungs-no-cloning"
    SOUVERAENITAETS_NO_CLONING = "souveraenitaets-no-cloning"


class NoCloningProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NoCloningGeltung(Enum):
    GESPERRT = "gesperrt"
    NICHTKLONBAR = "nichtklonbar"
    GRUNDLEGEND_NICHTKLONBAR = "grundlegend-nichtklonbar"


_init_map()

_TYP_MAP: dict[NoCloningGeltung, NoCloningTyp] = {
    NoCloningGeltung.GESPERRT: NoCloningTyp.SCHUTZ_NO_CLONING,
    NoCloningGeltung.NICHTKLONBAR: NoCloningTyp.ORDNUNGS_NO_CLONING,
    NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR: NoCloningTyp.SOUVERAENITAETS_NO_CLONING,
}

_PROZEDUR_MAP: dict[NoCloningGeltung, NoCloningProzedur] = {
    NoCloningGeltung.GESPERRT: NoCloningProzedur.NOTPROZEDUR,
    NoCloningGeltung.NICHTKLONBAR: NoCloningProzedur.REGELPROTOKOLL,
    NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR: NoCloningProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NoCloningGeltung, float] = {
    NoCloningGeltung.GESPERRT: 0.0,
    NoCloningGeltung.NICHTKLONBAR: 0.04,
    NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR: 0.08,
}

_TIER_DELTA: dict[NoCloningGeltung, int] = {
    NoCloningGeltung.GESPERRT: 0,
    NoCloningGeltung.NICHTKLONBAR: 1,
    NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NoCloningNorm:
    no_cloning_kodex_id: str
    no_cloning_typ: NoCloningTyp
    prozedur: NoCloningProzedur
    geltung: NoCloningGeltung
    no_cloning_weight: float
    no_cloning_tier: int
    canonical: bool
    no_cloning_ids: tuple[str, ...]
    no_cloning_tags: tuple[str, ...]


@dataclass(frozen=True)
class NoCloningKodex:
    kodex_id: str
    landauer_manifest: LandauerManifest
    normen: tuple[NoCloningNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.no_cloning_kodex_id for n in self.normen if n.geltung is NoCloningGeltung.GESPERRT)

    @property
    def nichtklonbar_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.no_cloning_kodex_id for n in self.normen if n.geltung is NoCloningGeltung.NICHTKLONBAR)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.no_cloning_kodex_id for n in self.normen if n.geltung is NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR)

    @property
    def kodex_signal(self):
        if any(n.geltung is NoCloningGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is NoCloningGeltung.NICHTKLONBAR for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-nichtklonbar")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-nichtklonbar")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_no_cloning_kodex(
    landauer_manifest: LandauerManifest | None = None,
    *,
    kodex_id: str = "no-cloning-kodex",
) -> NoCloningKodex:
    if landauer_manifest is None:
        landauer_manifest = build_landauer_manifest(manifest_id=f"{kodex_id}-manifest")

    normen: list[NoCloningNorm] = []
    for parent_norm in landauer_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.landauer_manifest_id.removeprefix(f'{landauer_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.landauer_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.landauer_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR)
        normen.append(
            NoCloningNorm(
                no_cloning_kodex_id=new_id,
                no_cloning_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                no_cloning_weight=new_weight,
                no_cloning_tier=new_tier,
                canonical=is_canonical,
                no_cloning_ids=parent_norm.landauer_ids + (new_id,),
                no_cloning_tags=parent_norm.landauer_tags + (f"no-cloning:{new_geltung.value}",),
            )
        )
    return NoCloningKodex(
        kodex_id=kodex_id,
        landauer_manifest=landauer_manifest,
        normen=tuple(normen),
    )
