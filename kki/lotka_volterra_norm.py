"""
#388 LotkaVolterraNorm — Räuber-Beute-Gleichungen (Lotka 1910, Volterra 1926):
dx/dt = αx - βxy  (Beute: Wachstum α, Prädation βy)
dy/dt = δxy - γy  (Räuber: Zugewinn δx, Tod γ)
Gleichgewicht: x* = γ/δ, y* = α/β.
Stabile Oszillationen ohne Dämpfung. Kein Sieger, kein Verlierer —
ewige kooperative Balance. Leitsterns Governance-Ökologie: kein Modul
dominiert dauerhaft, alle schwingen im produktiven Gleichgewicht.
*_norm-Muster.
Geltungsstufen: GESPERRT / LOTKAVOLTERRABESCHR / GRUNDLEGEND_LOTKAVOLTERRABESCHR
Parent: HomoostaseSenat (#387)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .homoostase_senat import (
    HomoostaseGeltung,
    HomoostaseSenat,
    build_homoostase_senat,
)

_GELTUNG_MAP: dict[HomoostaseGeltung, "LotkaVolterraNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HomoostaseGeltung.GESPERRT] = LotkaVolterraNormGeltung.GESPERRT
    _GELTUNG_MAP[HomoostaseGeltung.HOMOOSTATISCH] = LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR
    _GELTUNG_MAP[HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH] = LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR


class LotkaVolterraNormTyp(Enum):
    SCHUTZ_LOTKA_VOLTERRA_NORM = "schutz-lotka-volterra-norm"
    ORDNUNGS_LOTKA_VOLTERRA_NORM = "ordnungs-lotka-volterra-norm"
    SOUVERAENITAETS_LOTKA_VOLTERRA_NORM = "souveraenitaets-lotka-volterra-norm"


class LotkaVolterraNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LotkaVolterraNormGeltung(Enum):
    GESPERRT = "gesperrt"
    LOTKAVOLTERRABESCHR = "lotkavolterrabeschr"
    GRUNDLEGEND_LOTKAVOLTERRABESCHR = "grundlegend-lotkavolterrabeschr"


_init_map()

_TYP_MAP: dict[LotkaVolterraNormGeltung, LotkaVolterraNormTyp] = {
    LotkaVolterraNormGeltung.GESPERRT: LotkaVolterraNormTyp.SCHUTZ_LOTKA_VOLTERRA_NORM,
    LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR: LotkaVolterraNormTyp.ORDNUNGS_LOTKA_VOLTERRA_NORM,
    LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR: LotkaVolterraNormTyp.SOUVERAENITAETS_LOTKA_VOLTERRA_NORM,
}

_PROZEDUR_MAP: dict[LotkaVolterraNormGeltung, LotkaVolterraNormProzedur] = {
    LotkaVolterraNormGeltung.GESPERRT: LotkaVolterraNormProzedur.NOTPROZEDUR,
    LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR: LotkaVolterraNormProzedur.REGELPROTOKOLL,
    LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR: LotkaVolterraNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LotkaVolterraNormGeltung, float] = {
    LotkaVolterraNormGeltung.GESPERRT: 0.0,
    LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR: 0.04,
    LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR: 0.08,
}

_TIER_DELTA: dict[LotkaVolterraNormGeltung, int] = {
    LotkaVolterraNormGeltung.GESPERRT: 0,
    LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR: 1,
    LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LotkaVolterraNormEintrag:
    norm_id: str
    lotka_volterra_norm_typ: LotkaVolterraNormTyp
    prozedur: LotkaVolterraNormProzedur
    geltung: LotkaVolterraNormGeltung
    lotka_volterra_norm_weight: float
    lotka_volterra_norm_tier: int
    canonical: bool
    lotka_volterra_norm_ids: tuple[str, ...]
    lotka_volterra_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class LotkaVolterraNormSatz:
    norm_id: str
    homoostase_senat: HomoostaseSenat
    normen: tuple[LotkaVolterraNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is LotkaVolterraNormGeltung.GESPERRT)

    @property
    def lotkavolterrabeschr_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR)

    @property
    def norm_signal(self):
        if any(n.geltung is LotkaVolterraNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-lotkavolterrabeschr")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-lotkavolterrabeschr")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_lotka_volterra_norm(
    homoostase_senat: HomoostaseSenat | None = None,
    *,
    norm_id: str = "lotka-volterra-norm",
) -> LotkaVolterraNormSatz:
    if homoostase_senat is None:
        homoostase_senat = build_homoostase_senat(senat_id=f"{norm_id}-senat")

    normen: list[LotkaVolterraNormEintrag] = []
    for parent_norm in homoostase_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.homoostase_senat_id.removeprefix(f'{homoostase_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.homoostase_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.homoostase_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR)
        normen.append(
            LotkaVolterraNormEintrag(
                norm_id=new_id,
                lotka_volterra_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                lotka_volterra_norm_weight=new_weight,
                lotka_volterra_norm_tier=new_tier,
                canonical=is_canonical,
                lotka_volterra_norm_ids=parent_norm.homoostase_ids + (new_id,),
                lotka_volterra_norm_tags=parent_norm.homoostase_tags + (f"lotka-volterra-norm:{new_geltung.value}",),
            )
        )
    return LotkaVolterraNormSatz(
        norm_id=norm_id,
        homoostase_senat=homoostase_senat,
        normen=tuple(normen),
    )
