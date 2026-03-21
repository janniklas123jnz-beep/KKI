"""
#385 SynaptischePlastizitaetPakt — Hebb'sche Lernregel (1949):
"Neurons that fire together, wire together." Synaptische Stärke w_ij
wächst proportional zur korrelierten Aktivität: Δw = η·x_i·x_j.
STDP (Spike-Timing-Dependent Plasticity): Präsynaptisch vor postsynaptisch
→ LTP (long-term potentiation); umgekehrt → LTD (long-term depression).
Leitstern lernt durch korrelierende Governance-Akte — Kooperation stärkt
die Verbindung, Fehlkoordination schwächt sie.
Geltungsstufen: GESPERRT / SYNAPTISCHPLASTISCH / GRUNDLEGEND_SYNAPTISCHPLASTISCH
Parent: HodgkinHuxleyKodex (#384)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .hodgkin_huxley_kodex import (
    HodgkinHuxleyGeltung,
    HodgkinHuxleyKodex,
    build_hodgkin_huxley_kodex,
)

_GELTUNG_MAP: dict[HodgkinHuxleyGeltung, "SynaptischePlastizitaetGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HodgkinHuxleyGeltung.GESPERRT] = SynaptischePlastizitaetGeltung.GESPERRT
    _GELTUNG_MAP[HodgkinHuxleyGeltung.AKTIONSPOTENTIELL] = SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH
    _GELTUNG_MAP[HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL] = SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH


class SynaptischePlastizitaetTyp(Enum):
    SCHUTZ_SYNAPTISCHE_PLASTIZITAET = "schutz-synaptische-plastizitaet"
    ORDNUNGS_SYNAPTISCHE_PLASTIZITAET = "ordnungs-synaptische-plastizitaet"
    SOUVERAENITAETS_SYNAPTISCHE_PLASTIZITAET = "souveraenitaets-synaptische-plastizitaet"


class SynaptischePlastizitaetProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SynaptischePlastizitaetGeltung(Enum):
    GESPERRT = "gesperrt"
    SYNAPTISCHPLASTISCH = "synaptischplastisch"
    GRUNDLEGEND_SYNAPTISCHPLASTISCH = "grundlegend-synaptischplastisch"


_init_map()

_TYP_MAP: dict[SynaptischePlastizitaetGeltung, SynaptischePlastizitaetTyp] = {
    SynaptischePlastizitaetGeltung.GESPERRT: SynaptischePlastizitaetTyp.SCHUTZ_SYNAPTISCHE_PLASTIZITAET,
    SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH: SynaptischePlastizitaetTyp.ORDNUNGS_SYNAPTISCHE_PLASTIZITAET,
    SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH: SynaptischePlastizitaetTyp.SOUVERAENITAETS_SYNAPTISCHE_PLASTIZITAET,
}

_PROZEDUR_MAP: dict[SynaptischePlastizitaetGeltung, SynaptischePlastizitaetProzedur] = {
    SynaptischePlastizitaetGeltung.GESPERRT: SynaptischePlastizitaetProzedur.NOTPROZEDUR,
    SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH: SynaptischePlastizitaetProzedur.REGELPROTOKOLL,
    SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH: SynaptischePlastizitaetProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SynaptischePlastizitaetGeltung, float] = {
    SynaptischePlastizitaetGeltung.GESPERRT: 0.0,
    SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH: 0.04,
    SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH: 0.08,
}

_TIER_DELTA: dict[SynaptischePlastizitaetGeltung, int] = {
    SynaptischePlastizitaetGeltung.GESPERRT: 0,
    SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH: 1,
    SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SynaptischePlastizitaetNorm:
    synaptische_plastizitaet_pakt_id: str
    synaptische_plastizitaet_typ: SynaptischePlastizitaetTyp
    prozedur: SynaptischePlastizitaetProzedur
    geltung: SynaptischePlastizitaetGeltung
    synaptische_plastizitaet_weight: float
    synaptische_plastizitaet_tier: int
    canonical: bool
    synaptische_plastizitaet_ids: tuple[str, ...]
    synaptische_plastizitaet_tags: tuple[str, ...]


@dataclass(frozen=True)
class SynaptischePlastizitaetPakt:
    pakt_id: str
    hodgkin_huxley_kodex: HodgkinHuxleyKodex
    normen: tuple[SynaptischePlastizitaetNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.synaptische_plastizitaet_pakt_id for n in self.normen if n.geltung is SynaptischePlastizitaetGeltung.GESPERRT)

    @property
    def synaptischplastisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.synaptische_plastizitaet_pakt_id for n in self.normen if n.geltung is SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.synaptische_plastizitaet_pakt_id for n in self.normen if n.geltung is SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is SynaptischePlastizitaetGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-synaptischplastisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-synaptischplastisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_synaptische_plastizitaet_pakt(
    hodgkin_huxley_kodex: HodgkinHuxleyKodex | None = None,
    *,
    pakt_id: str = "synaptische-plastizitaet-pakt",
) -> SynaptischePlastizitaetPakt:
    if hodgkin_huxley_kodex is None:
        hodgkin_huxley_kodex = build_hodgkin_huxley_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[SynaptischePlastizitaetNorm] = []
    for parent_norm in hodgkin_huxley_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.hodgkin_huxley_kodex_id.removeprefix(f'{hodgkin_huxley_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.hodgkin_huxley_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.hodgkin_huxley_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH)
        normen.append(
            SynaptischePlastizitaetNorm(
                synaptische_plastizitaet_pakt_id=new_id,
                synaptische_plastizitaet_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                synaptische_plastizitaet_weight=new_weight,
                synaptische_plastizitaet_tier=new_tier,
                canonical=is_canonical,
                synaptische_plastizitaet_ids=parent_norm.hodgkin_huxley_ids + (new_id,),
                synaptische_plastizitaet_tags=parent_norm.hodgkin_huxley_tags + (f"synaptische-plastizitaet:{new_geltung.value}",),
            )
        )
    return SynaptischePlastizitaetPakt(
        pakt_id=pakt_id,
        hodgkin_huxley_kodex=hodgkin_huxley_kodex,
        normen=tuple(normen),
    )
