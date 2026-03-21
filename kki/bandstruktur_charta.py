"""
#343 BandstrukturCharta — Das Bändermodell als Governance-Zonen-Charta:
Valenzband (aktive Normen), Leitungsband (offene Eskalation), Bandlücke
(verbotene Übergänge). Bloch-Theorem garantiert periodische Gitter-Invarianz.
Geltungsstufen: GESPERRT / BANDSTRUKTURIERT / GRUNDLEGEND_BANDSTRUKTURIERT
Parent: KristallgitterRegister (#342)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kristallgitter_register import (
    KristallgitterRegister,
    KristallgitterGeltung,
    build_kristallgitter_register,
)

_GELTUNG_MAP: dict[KristallgitterGeltung, "BandstrukturGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KristallgitterGeltung.GESPERRT] = BandstrukturGeltung.GESPERRT
    _GELTUNG_MAP[KristallgitterGeltung.GITTERGEORDNET] = BandstrukturGeltung.BANDSTRUKTURIERT
    _GELTUNG_MAP[KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET] = BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT


class BandstrukturTyp(Enum):
    SCHUTZ_BANDSTRUKTUR = "schutz-bandstruktur"
    ORDNUNGS_BANDSTRUKTUR = "ordnungs-bandstruktur"
    SOUVERAENITAETS_BANDSTRUKTUR = "souveraenitaets-bandstruktur"


class BandstrukturProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BandstrukturGeltung(Enum):
    GESPERRT = "gesperrt"
    BANDSTRUKTURIERT = "bandstrukturiert"
    GRUNDLEGEND_BANDSTRUKTURIERT = "grundlegend-bandstrukturiert"


_init_map()

_TYP_MAP: dict[BandstrukturGeltung, BandstrukturTyp] = {
    BandstrukturGeltung.GESPERRT: BandstrukturTyp.SCHUTZ_BANDSTRUKTUR,
    BandstrukturGeltung.BANDSTRUKTURIERT: BandstrukturTyp.ORDNUNGS_BANDSTRUKTUR,
    BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT: BandstrukturTyp.SOUVERAENITAETS_BANDSTRUKTUR,
}

_PROZEDUR_MAP: dict[BandstrukturGeltung, BandstrukturProzedur] = {
    BandstrukturGeltung.GESPERRT: BandstrukturProzedur.NOTPROZEDUR,
    BandstrukturGeltung.BANDSTRUKTURIERT: BandstrukturProzedur.REGELPROTOKOLL,
    BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT: BandstrukturProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[BandstrukturGeltung, float] = {
    BandstrukturGeltung.GESPERRT: 0.0,
    BandstrukturGeltung.BANDSTRUKTURIERT: 0.04,
    BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT: 0.08,
}

_TIER_DELTA: dict[BandstrukturGeltung, int] = {
    BandstrukturGeltung.GESPERRT: 0,
    BandstrukturGeltung.BANDSTRUKTURIERT: 1,
    BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BandstrukturNorm:
    bandstruktur_charta_id: str
    bandstruktur_typ: BandstrukturTyp
    prozedur: BandstrukturProzedur
    geltung: BandstrukturGeltung
    bandstruktur_weight: float
    bandstruktur_tier: int
    canonical: bool
    bandstruktur_ids: tuple[str, ...]
    bandstruktur_tags: tuple[str, ...]


@dataclass(frozen=True)
class BandstrukturCharta:
    charta_id: str
    kristallgitter_register: KristallgitterRegister
    normen: tuple[BandstrukturNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bandstruktur_charta_id for n in self.normen if n.geltung is BandstrukturGeltung.GESPERRT)

    @property
    def bandstrukturiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bandstruktur_charta_id for n in self.normen if n.geltung is BandstrukturGeltung.BANDSTRUKTURIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bandstruktur_charta_id for n in self.normen if n.geltung is BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is BandstrukturGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is BandstrukturGeltung.BANDSTRUKTURIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-bandstrukturiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-bandstrukturiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_bandstruktur_charta(
    kristallgitter_register: KristallgitterRegister | None = None,
    *,
    charta_id: str = "bandstruktur-charta",
) -> BandstrukturCharta:
    if kristallgitter_register is None:
        kristallgitter_register = build_kristallgitter_register(register_id=f"{charta_id}-register")

    normen: list[BandstrukturNorm] = []
    for parent_norm in kristallgitter_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.kristallgitter_register_id.removeprefix(f'{kristallgitter_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.kristallgitter_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kristallgitter_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BandstrukturGeltung.GRUNDLEGEND_BANDSTRUKTURIERT)
        normen.append(
            BandstrukturNorm(
                bandstruktur_charta_id=new_id,
                bandstruktur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                bandstruktur_weight=new_weight,
                bandstruktur_tier=new_tier,
                canonical=is_canonical,
                bandstruktur_ids=parent_norm.kristallgitter_ids + (new_id,),
                bandstruktur_tags=parent_norm.kristallgitter_tags + (f"bandstruktur:{new_geltung.value}",),
            )
        )
    return BandstrukturCharta(
        charta_id=charta_id,
        kristallgitter_register=kristallgitter_register,
        normen=tuple(normen),
    )
