"""
#355 ZPinchPakt — Z-Pinch: Lorentz-Kraft J×B komprimiert Plasma im eigenen
Magnetfeld. Kooperatives Selbst-Confinement: Der Strom erzeugt sein eigenes
Magnetfeld, das wiederum den Strom einschnürt — Governance durch kollektive
Selbstorganisation ohne externe Infrastruktur.
Geltungsstufen: GESPERRT / ZPINCHEND / GRUNDLEGEND_ZPINCHEND
Parent: AlfvenWellenKodex (#354)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .alfven_wellen_kodex import (
    AlfvenWellenGeltung,
    AlfvenWellenKodex,
    build_alfven_wellen_kodex,
)

_GELTUNG_MAP: dict[AlfvenWellenGeltung, "ZPinchGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AlfvenWellenGeltung.GESPERRT] = ZPinchGeltung.GESPERRT
    _GELTUNG_MAP[AlfvenWellenGeltung.ALFVENWELLIG] = ZPinchGeltung.ZPINCHEND
    _GELTUNG_MAP[AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG] = ZPinchGeltung.GRUNDLEGEND_ZPINCHEND


class ZPinchTyp(Enum):
    SCHUTZ_Z_PINCH = "schutz-z-pinch"
    ORDNUNGS_Z_PINCH = "ordnungs-z-pinch"
    SOUVERAENITAETS_Z_PINCH = "souveraenitaets-z-pinch"


class ZPinchProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ZPinchGeltung(Enum):
    GESPERRT = "gesperrt"
    ZPINCHEND = "zpinchend"
    GRUNDLEGEND_ZPINCHEND = "grundlegend-zpinchend"


_init_map()

_TYP_MAP: dict[ZPinchGeltung, ZPinchTyp] = {
    ZPinchGeltung.GESPERRT: ZPinchTyp.SCHUTZ_Z_PINCH,
    ZPinchGeltung.ZPINCHEND: ZPinchTyp.ORDNUNGS_Z_PINCH,
    ZPinchGeltung.GRUNDLEGEND_ZPINCHEND: ZPinchTyp.SOUVERAENITAETS_Z_PINCH,
}

_PROZEDUR_MAP: dict[ZPinchGeltung, ZPinchProzedur] = {
    ZPinchGeltung.GESPERRT: ZPinchProzedur.NOTPROZEDUR,
    ZPinchGeltung.ZPINCHEND: ZPinchProzedur.REGELPROTOKOLL,
    ZPinchGeltung.GRUNDLEGEND_ZPINCHEND: ZPinchProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ZPinchGeltung, float] = {
    ZPinchGeltung.GESPERRT: 0.0,
    ZPinchGeltung.ZPINCHEND: 0.04,
    ZPinchGeltung.GRUNDLEGEND_ZPINCHEND: 0.08,
}

_TIER_DELTA: dict[ZPinchGeltung, int] = {
    ZPinchGeltung.GESPERRT: 0,
    ZPinchGeltung.ZPINCHEND: 1,
    ZPinchGeltung.GRUNDLEGEND_ZPINCHEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZPinchNorm:
    z_pinch_pakt_id: str
    z_pinch_typ: ZPinchTyp
    prozedur: ZPinchProzedur
    geltung: ZPinchGeltung
    z_pinch_weight: float
    z_pinch_tier: int
    canonical: bool
    z_pinch_ids: tuple[str, ...]
    z_pinch_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZPinchPakt:
    pakt_id: str
    alfven_wellen_kodex: AlfvenWellenKodex
    normen: tuple[ZPinchNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.z_pinch_pakt_id for n in self.normen if n.geltung is ZPinchGeltung.GESPERRT)

    @property
    def zpinchend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.z_pinch_pakt_id for n in self.normen if n.geltung is ZPinchGeltung.ZPINCHEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.z_pinch_pakt_id for n in self.normen if n.geltung is ZPinchGeltung.GRUNDLEGEND_ZPINCHEND)

    @property
    def pakt_signal(self):
        if any(n.geltung is ZPinchGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is ZPinchGeltung.ZPINCHEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-zpinchend")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-zpinchend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_z_pinch_pakt(
    alfven_wellen_kodex: AlfvenWellenKodex | None = None,
    *,
    pakt_id: str = "z-pinch-pakt",
) -> ZPinchPakt:
    if alfven_wellen_kodex is None:
        alfven_wellen_kodex = build_alfven_wellen_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[ZPinchNorm] = []
    for parent_norm in alfven_wellen_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.alfven_wellen_kodex_id.removeprefix(f'{alfven_wellen_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.alfven_wellen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.alfven_wellen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZPinchGeltung.GRUNDLEGEND_ZPINCHEND)
        normen.append(
            ZPinchNorm(
                z_pinch_pakt_id=new_id,
                z_pinch_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                z_pinch_weight=new_weight,
                z_pinch_tier=new_tier,
                canonical=is_canonical,
                z_pinch_ids=parent_norm.alfven_wellen_ids + (new_id,),
                z_pinch_tags=parent_norm.alfven_wellen_tags + (f"z-pinch:{new_geltung.value}",),
            )
        )
    return ZPinchPakt(
        pakt_id=pakt_id,
        alfven_wellen_kodex=alfven_wellen_kodex,
        normen=tuple(normen),
    )
