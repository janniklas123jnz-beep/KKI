"""#295 – WellenausbreitungsPakt: Wellenausbreitung als Governance-Pakt.

Parent: induktions_kodex (#294)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .induktions_kodex import (
    InduktionsGeltung,
    InduktionsKodex,
    build_induktions_kodex,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class WellenausbreitungsTyp(Enum):
    SCHUTZ_WELLENAUSBREITUNG = "schutz-wellenausbreitung"
    ORDNUNGS_WELLENAUSBREITUNG = "ordnungs-wellenausbreitung"
    SOUVERAENITAETS_WELLENAUSBREITUNG = "souveraenitaets-wellenausbreitung"


class WellenausbreitungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WellenausbreitungsGeltung(Enum):
    GESPERRT = "gesperrt"
    WELLENAUSBREITEND = "wellenausbreitend"
    GRUNDLEGEND_WELLENAUSBREITEND = "grundlegend-wellenausbreitend"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[InduktionsGeltung, WellenausbreitungsGeltung] = {
    InduktionsGeltung.GESPERRT: WellenausbreitungsGeltung.GESPERRT,
    InduktionsGeltung.INDUZIERT: WellenausbreitungsGeltung.WELLENAUSBREITEND,
    InduktionsGeltung.GRUNDLEGEND_INDUZIERT: WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND,
}

_TYP_MAP: dict[InduktionsGeltung, WellenausbreitungsTyp] = {
    InduktionsGeltung.GESPERRT: WellenausbreitungsTyp.SCHUTZ_WELLENAUSBREITUNG,
    InduktionsGeltung.INDUZIERT: WellenausbreitungsTyp.ORDNUNGS_WELLENAUSBREITUNG,
    InduktionsGeltung.GRUNDLEGEND_INDUZIERT: WellenausbreitungsTyp.SOUVERAENITAETS_WELLENAUSBREITUNG,
}

_PROZEDUR_MAP: dict[InduktionsGeltung, WellenausbreitungsProzedur] = {
    InduktionsGeltung.GESPERRT: WellenausbreitungsProzedur.NOTPROZEDUR,
    InduktionsGeltung.INDUZIERT: WellenausbreitungsProzedur.REGELPROTOKOLL,
    InduktionsGeltung.GRUNDLEGEND_INDUZIERT: WellenausbreitungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[InduktionsGeltung, float] = {
    InduktionsGeltung.GESPERRT: 0.0,
    InduktionsGeltung.INDUZIERT: 0.04,
    InduktionsGeltung.GRUNDLEGEND_INDUZIERT: 0.08,
}

_TIER_BONUS: dict[InduktionsGeltung, int] = {
    InduktionsGeltung.GESPERRT: 0,
    InduktionsGeltung.INDUZIERT: 1,
    InduktionsGeltung.GRUNDLEGEND_INDUZIERT: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WellenausbreitungsNorm:
    wellenausbreitung_pakt_id: str
    wellenausbreitung_typ: WellenausbreitungsTyp
    prozedur: WellenausbreitungsProzedur
    geltung: WellenausbreitungsGeltung
    wellenausbreitung_weight: float
    wellenausbreitung_tier: int
    canonical: bool
    wellenausbreitung_ids: tuple[str, ...]
    wellenausbreitung_tags: tuple[str, ...]


@dataclass(frozen=True)
class WellenausbreitungsPakt:
    pakt_id: str
    induktions_kodex: InduktionsKodex
    normen: tuple[WellenausbreitungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wellenausbreitung_pakt_id for n in self.normen if n.geltung is WellenausbreitungsGeltung.GESPERRT)

    @property
    def wellenausbreitend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wellenausbreitung_pakt_id for n in self.normen if n.geltung is WellenausbreitungsGeltung.WELLENAUSBREITEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wellenausbreitung_pakt_id for n in self.normen if n.geltung is WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND)

    @property
    def pakt_signal(self):
        if any(n.geltung is WellenausbreitungsGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is WellenausbreitungsGeltung.WELLENAUSBREITEND for n in self.normen):
            status = "pakt-wellenausbreitend"
            severity = "warning"
        else:
            status = "pakt-grundlegend-wellenausbreitend"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_wellenausbreitung_pakt(
    induktions_kodex: InduktionsKodex | None = None,
    *,
    pakt_id: str = "wellenausbreitung-pakt",
) -> WellenausbreitungsPakt:
    if induktions_kodex is None:
        induktions_kodex = build_induktions_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[WellenausbreitungsNorm] = []
    for parent_norm in induktions_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.induktions_kodex_id.removeprefix(f'{induktions_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.induktions_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.induktions_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND)
        normen.append(
            WellenausbreitungsNorm(
                wellenausbreitung_pakt_id=new_id,
                wellenausbreitung_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                wellenausbreitung_weight=raw_weight,
                wellenausbreitung_tier=new_tier,
                canonical=is_canonical,
                wellenausbreitung_ids=parent_norm.induktions_ids + (new_id,),
                wellenausbreitung_tags=parent_norm.induktions_tags + (f"wellenausbreitung-pakt:{new_geltung.value}",),
            )
        )

    return WellenausbreitungsPakt(
        pakt_id=pakt_id,
        induktions_kodex=induktions_kodex,
        normen=tuple(normen),
    )
