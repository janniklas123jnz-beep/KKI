"""
#415 ZellulaereAutomatenPakt — Zelluläre Automaten: Lokale Regeln, globale Komplexität.
Wolfram (1983): Elementare zelluläre Automaten — 256 Regeln, 4 Klassen.
Rule 30: deterministisch aber chaotisch. Lokale Regeln → globale Komplexität.
Conway's Game of Life (1970): 3 Regeln → Turing-vollständige Komplexität.
Glider, Oscillator, Still Life als Governance-Muster. Emergenz ohne Designer.
Rule 110: Turing-vollständig (Cook 2004). Wolframs 'New Kind of Science' (2002):
Universum als zellulärer Automat. Leitsterns Agenten: regelbasierte Emergenz.
Geltungsstufen: GESPERRT / ZELLULAERAUTOMAT / GRUNDLEGEND_ZELLULAERAUTOMAT
Parent: FraktalKodex (#414)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fraktal_kodex import (
    FraktalKodex,
    FraktalKodexGeltung,
    build_fraktal_kodex,
)

_GELTUNG_MAP: dict[FraktalKodexGeltung, "ZellulaereAutomatenPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FraktalKodexGeltung.GESPERRT] = ZellulaereAutomatenPaktGeltung.GESPERRT
    _GELTUNG_MAP[FraktalKodexGeltung.FRAKTAL] = ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT
    _GELTUNG_MAP[FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL] = ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT


class ZellulaereAutomatenPaktTyp(Enum):
    SCHUTZ_ZELLULAERAUTOMAT = "schutz-zellulaerautomat"
    ORDNUNGS_ZELLULAERAUTOMAT = "ordnungs-zellulaerautomat"
    SOUVERAENITAETS_ZELLULAERAUTOMAT = "souveraenitaets-zellulaerautomat"


class ZellulaereAutomatenPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ZellulaereAutomatenPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    ZELLULAERAUTOMAT = "zellulaerautomat"
    GRUNDLEGEND_ZELLULAERAUTOMAT = "grundlegend-zellulaerautomat"


_init_map()

_TYP_MAP: dict[ZellulaereAutomatenPaktGeltung, ZellulaereAutomatenPaktTyp] = {
    ZellulaereAutomatenPaktGeltung.GESPERRT: ZellulaereAutomatenPaktTyp.SCHUTZ_ZELLULAERAUTOMAT,
    ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT: ZellulaereAutomatenPaktTyp.ORDNUNGS_ZELLULAERAUTOMAT,
    ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT: ZellulaereAutomatenPaktTyp.SOUVERAENITAETS_ZELLULAERAUTOMAT,
}

_PROZEDUR_MAP: dict[ZellulaereAutomatenPaktGeltung, ZellulaereAutomatenPaktProzedur] = {
    ZellulaereAutomatenPaktGeltung.GESPERRT: ZellulaereAutomatenPaktProzedur.NOTPROZEDUR,
    ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT: ZellulaereAutomatenPaktProzedur.REGELPROTOKOLL,
    ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT: ZellulaereAutomatenPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ZellulaereAutomatenPaktGeltung, float] = {
    ZellulaereAutomatenPaktGeltung.GESPERRT: 0.0,
    ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT: 0.04,
    ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT: 0.08,
}

_TIER_DELTA: dict[ZellulaereAutomatenPaktGeltung, int] = {
    ZellulaereAutomatenPaktGeltung.GESPERRT: 0,
    ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT: 1,
    ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZellulaereAutomatenPaktNorm:
    zellulaere_automaten_pakt_id: str
    zellulaerautomat_typ: ZellulaereAutomatenPaktTyp
    prozedur: ZellulaereAutomatenPaktProzedur
    geltung: ZellulaereAutomatenPaktGeltung
    zellulaerautomat_weight: float
    zellulaerautomat_tier: int
    canonical: bool
    zellulaerautomat_ids: tuple[str, ...]
    zellulaerautomat_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZellulaereAutomatenPakt:
    pakt_id: str
    fraktal_kodex: FraktalKodex
    normen: tuple[ZellulaereAutomatenPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zellulaere_automaten_pakt_id for n in self.normen if n.geltung is ZellulaereAutomatenPaktGeltung.GESPERRT)

    @property
    def zellulaerautomat_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zellulaere_automaten_pakt_id for n in self.normen if n.geltung is ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zellulaere_automaten_pakt_id for n in self.normen if n.geltung is ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT)

    @property
    def pakt_signal(self):
        if any(n.geltung is ZellulaereAutomatenPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-zellulaerautomat")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-zellulaerautomat")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_zellulaere_automaten_pakt(
    fraktal_kodex: FraktalKodex | None = None,
    *,
    pakt_id: str = "zellulaere-automaten-pakt",
) -> ZellulaereAutomatenPakt:
    if fraktal_kodex is None:
        fraktal_kodex = build_fraktal_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[ZellulaereAutomatenPaktNorm] = []
    for parent_norm in fraktal_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.fraktal_kodex_id.removeprefix(f'{fraktal_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.fraktal_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fraktal_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT)
        normen.append(
            ZellulaereAutomatenPaktNorm(
                zellulaere_automaten_pakt_id=new_id,
                zellulaerautomat_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                zellulaerautomat_weight=new_weight,
                zellulaerautomat_tier=new_tier,
                canonical=is_canonical,
                zellulaerautomat_ids=parent_norm.fraktal_ids + (new_id,),
                zellulaerautomat_tags=parent_norm.fraktal_tags + (f"zellulaerautomat:{new_geltung.value}",),
            )
        )
    return ZellulaereAutomatenPakt(
        pakt_id=pakt_id,
        fraktal_kodex=fraktal_kodex,
        normen=tuple(normen),
    )
