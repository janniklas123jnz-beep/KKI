"""
#344 HalbleiterKodex — Der Halbleiter als bedingter Governance-Leiter-Kodex:
Aktivierungsbarriere für Eskalation, dotierte Spezialagenten als n/p-Dotierung,
pn-Übergang als Richtungsventil für Governance-Entscheidungen.
Geltungsstufen: GESPERRT / HALBLEITEND / GRUNDLEGEND_HALBLEITEND
Parent: BandstrukturCharta (#343)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bandstruktur_charta import (
    BandstrukturCharta,
    BandstrukturGeltung,
    build_bandstruktur_charta,
)

_GELTUNG_MAP: dict[BandstrukturGeltung, "HalbleiterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[BandstrukturGeltung.GESPERRT] = HalbleiterGeltung.GESPERRT
    _GELTUNG_MAP[BandstrukturGeltung.BANDSTRUKTURIERT] = HalbleiterGeltung.HALBLEITEND
    _GELTUNG_MAP[BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT] = HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND


class HalbleiterTyp(Enum):
    SCHUTZ_HALBLEITER = "schutz-halbleiter"
    ORDNUNGS_HALBLEITER = "ordnungs-halbleiter"
    SOUVERAENITAETS_HALBLEITER = "souveraenitaets-halbleiter"


class HalbleiterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HalbleiterGeltung(Enum):
    GESPERRT = "gesperrt"
    HALBLEITEND = "halbleitend"
    GRUNDLEGEND_HALBLEITEND = "grundlegend-halbleitend"


_init_map()

_TYP_MAP: dict[HalbleiterGeltung, HalbleiterTyp] = {
    HalbleiterGeltung.GESPERRT: HalbleiterTyp.SCHUTZ_HALBLEITER,
    HalbleiterGeltung.HALBLEITEND: HalbleiterTyp.ORDNUNGS_HALBLEITER,
    HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND: HalbleiterTyp.SOUVERAENITAETS_HALBLEITER,
}

_PROZEDUR_MAP: dict[HalbleiterGeltung, HalbleiterProzedur] = {
    HalbleiterGeltung.GESPERRT: HalbleiterProzedur.NOTPROZEDUR,
    HalbleiterGeltung.HALBLEITEND: HalbleiterProzedur.REGELPROTOKOLL,
    HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND: HalbleiterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HalbleiterGeltung, float] = {
    HalbleiterGeltung.GESPERRT: 0.0,
    HalbleiterGeltung.HALBLEITEND: 0.04,
    HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND: 0.08,
}

_TIER_DELTA: dict[HalbleiterGeltung, int] = {
    HalbleiterGeltung.GESPERRT: 0,
    HalbleiterGeltung.HALBLEITEND: 1,
    HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HalbleiterNorm:
    halbleiter_kodex_id: str
    halbleiter_typ: HalbleiterTyp
    prozedur: HalbleiterProzedur
    geltung: HalbleiterGeltung
    halbleiter_weight: float
    halbleiter_tier: int
    canonical: bool
    halbleiter_ids: tuple[str, ...]
    halbleiter_tags: tuple[str, ...]


@dataclass(frozen=True)
class HalbleiterKodex:
    kodex_id: str
    bandstruktur_charta: BandstrukturCharta
    normen: tuple[HalbleiterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.halbleiter_kodex_id for n in self.normen if n.geltung is HalbleiterGeltung.GESPERRT)

    @property
    def halbleitend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.halbleiter_kodex_id for n in self.normen if n.geltung is HalbleiterGeltung.HALBLEITEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.halbleiter_kodex_id for n in self.normen if n.geltung is HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND)

    @property
    def kodex_signal(self):
        if any(n.geltung is HalbleiterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is HalbleiterGeltung.HALBLEITEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-halbleitend")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-halbleitend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_halbleiter_kodex(
    bandstruktur_charta: BandstrukturCharta | None = None,
    *,
    kodex_id: str = "halbleiter-kodex",
) -> HalbleiterKodex:
    if bandstruktur_charta is None:
        bandstruktur_charta = build_bandstruktur_charta(charta_id=f"{kodex_id}-charta")

    normen: list[HalbleiterNorm] = []
    for parent_norm in bandstruktur_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.bandstruktur_charta_id.removeprefix(f'{bandstruktur_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.bandstruktur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.bandstruktur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HalbleiterGeltung.GRUNDLEGEND_HALBLEITEND)
        normen.append(
            HalbleiterNorm(
                halbleiter_kodex_id=new_id,
                halbleiter_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                halbleiter_weight=new_weight,
                halbleiter_tier=new_tier,
                canonical=is_canonical,
                halbleiter_ids=parent_norm.bandstruktur_ids + (new_id,),
                halbleiter_tags=parent_norm.bandstruktur_tags + (f"halbleiter:{new_geltung.value}",),
            )
        )
    return HalbleiterKodex(
        kodex_id=kodex_id,
        bandstruktur_charta=bandstruktur_charta,
        normen=tuple(normen),
    )
