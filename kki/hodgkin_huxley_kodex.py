"""
#384 HodgkinHuxleyKodex — Aktionspotential-Gleichungen (Hodgkin & Huxley 1952,
Nobelpreis 1963): V_m-Dynamik durch spannungsgesteuerte Na⁺- und K⁺-Kanäle.
dV/dt = (I_ext - g_Na·m³h·(V-E_Na) - g_K·n⁴·(V-E_K) - g_L·(V-E_L)) / C_m.
All-or-nothing-Prinzip: Schwellenspannung -55 mV → Spike +40 mV.
Leitsterns Governance-Signale propagieren wie neuronale Aktionspotentiale —
präzise, digital, unrevidierbar ausgelöst.
Geltungsstufen: GESPERRT / AKTIONSPOTENTIELL / GRUNDLEGEND_AKTIONSPOTENTIELL
Parent: ProteinfaltungCharta (#383)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .proteinfaltung_charta import (
    ProteinfaltungCharta,
    ProteinfaltungGeltung,
    build_proteinfaltung_charta,
)

_GELTUNG_MAP: dict[ProteinfaltungGeltung, "HodgkinHuxleyGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ProteinfaltungGeltung.GESPERRT] = HodgkinHuxleyGeltung.GESPERRT
    _GELTUNG_MAP[ProteinfaltungGeltung.PROTEINGEFALTET] = HodgkinHuxleyGeltung.AKTIONSPOTENTIELL
    _GELTUNG_MAP[ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET] = HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL


class HodgkinHuxleyTyp(Enum):
    SCHUTZ_HODGKIN_HUXLEY = "schutz-hodgkin-huxley"
    ORDNUNGS_HODGKIN_HUXLEY = "ordnungs-hodgkin-huxley"
    SOUVERAENITAETS_HODGKIN_HUXLEY = "souveraenitaets-hodgkin-huxley"


class HodgkinHuxleyProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HodgkinHuxleyGeltung(Enum):
    GESPERRT = "gesperrt"
    AKTIONSPOTENTIELL = "aktionspotentiell"
    GRUNDLEGEND_AKTIONSPOTENTIELL = "grundlegend-aktionspotentiell"


_init_map()

_TYP_MAP: dict[HodgkinHuxleyGeltung, HodgkinHuxleyTyp] = {
    HodgkinHuxleyGeltung.GESPERRT: HodgkinHuxleyTyp.SCHUTZ_HODGKIN_HUXLEY,
    HodgkinHuxleyGeltung.AKTIONSPOTENTIELL: HodgkinHuxleyTyp.ORDNUNGS_HODGKIN_HUXLEY,
    HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL: HodgkinHuxleyTyp.SOUVERAENITAETS_HODGKIN_HUXLEY,
}

_PROZEDUR_MAP: dict[HodgkinHuxleyGeltung, HodgkinHuxleyProzedur] = {
    HodgkinHuxleyGeltung.GESPERRT: HodgkinHuxleyProzedur.NOTPROZEDUR,
    HodgkinHuxleyGeltung.AKTIONSPOTENTIELL: HodgkinHuxleyProzedur.REGELPROTOKOLL,
    HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL: HodgkinHuxleyProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HodgkinHuxleyGeltung, float] = {
    HodgkinHuxleyGeltung.GESPERRT: 0.0,
    HodgkinHuxleyGeltung.AKTIONSPOTENTIELL: 0.04,
    HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL: 0.08,
}

_TIER_DELTA: dict[HodgkinHuxleyGeltung, int] = {
    HodgkinHuxleyGeltung.GESPERRT: 0,
    HodgkinHuxleyGeltung.AKTIONSPOTENTIELL: 1,
    HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HodgkinHuxleyNorm:
    hodgkin_huxley_kodex_id: str
    hodgkin_huxley_typ: HodgkinHuxleyTyp
    prozedur: HodgkinHuxleyProzedur
    geltung: HodgkinHuxleyGeltung
    hodgkin_huxley_weight: float
    hodgkin_huxley_tier: int
    canonical: bool
    hodgkin_huxley_ids: tuple[str, ...]
    hodgkin_huxley_tags: tuple[str, ...]


@dataclass(frozen=True)
class HodgkinHuxleyKodex:
    kodex_id: str
    proteinfaltung_charta: ProteinfaltungCharta
    normen: tuple[HodgkinHuxleyNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hodgkin_huxley_kodex_id for n in self.normen if n.geltung is HodgkinHuxleyGeltung.GESPERRT)

    @property
    def aktionspotentiell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hodgkin_huxley_kodex_id for n in self.normen if n.geltung is HodgkinHuxleyGeltung.AKTIONSPOTENTIELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hodgkin_huxley_kodex_id for n in self.normen if n.geltung is HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL)

    @property
    def kodex_signal(self):
        if any(n.geltung is HodgkinHuxleyGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is HodgkinHuxleyGeltung.AKTIONSPOTENTIELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-aktionspotentiell")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-aktionspotentiell")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_hodgkin_huxley_kodex(
    proteinfaltung_charta: ProteinfaltungCharta | None = None,
    *,
    kodex_id: str = "hodgkin-huxley-kodex",
) -> HodgkinHuxleyKodex:
    if proteinfaltung_charta is None:
        proteinfaltung_charta = build_proteinfaltung_charta(charta_id=f"{kodex_id}-charta")

    normen: list[HodgkinHuxleyNorm] = []
    for parent_norm in proteinfaltung_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.proteinfaltung_charta_id.removeprefix(f'{proteinfaltung_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.proteinfaltung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.proteinfaltung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HodgkinHuxleyGeltung.GRUNDLEGEND_AKTIONSPOTENTIELL)
        normen.append(
            HodgkinHuxleyNorm(
                hodgkin_huxley_kodex_id=new_id,
                hodgkin_huxley_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                hodgkin_huxley_weight=new_weight,
                hodgkin_huxley_tier=new_tier,
                canonical=is_canonical,
                hodgkin_huxley_ids=parent_norm.proteinfaltung_ids + (new_id,),
                hodgkin_huxley_tags=parent_norm.proteinfaltung_tags + (f"hodgkin-huxley:{new_geltung.value}",),
            )
        )
    return HodgkinHuxleyKodex(
        kodex_id=kodex_id,
        proteinfaltung_charta=proteinfaltung_charta,
        normen=tuple(normen),
    )
