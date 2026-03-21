"""
#342 KristallgitterRegister — Das periodische Kristallgitter als
Governance-Ordnungsregister: jeder Governance-Knoten an seinem präzisen
Gitterplatz, Defekte als Ausnahmen explizit verwaltet.
Geltungsstufen: GESPERRT / GITTERGEORDNET / GRUNDLEGEND_GITTERGEORDNET
Parent: FestkoerperFeld (#341)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .festkoerper_feld import (
    FestkoerperFeld,
    FestkoerperGeltung,
    build_festkoerper_feld,
)

_GELTUNG_MAP: dict[FestkoerperGeltung, "KristallgitterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FestkoerperGeltung.GESPERRT] = KristallgitterGeltung.GESPERRT
    _GELTUNG_MAP[FestkoerperGeltung.FESTKOERPERLICH] = KristallgitterGeltung.GITTERGEORDNET
    _GELTUNG_MAP[FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH] = KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET


class KristallgitterTyp(Enum):
    SCHUTZ_KRISTALLGITTER = "schutz-kristallgitter"
    ORDNUNGS_KRISTALLGITTER = "ordnungs-kristallgitter"
    SOUVERAENITAETS_KRISTALLGITTER = "souveraenitaets-kristallgitter"


class KristallgitterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KristallgitterGeltung(Enum):
    GESPERRT = "gesperrt"
    GITTERGEORDNET = "gittergeordnet"
    GRUNDLEGEND_GITTERGEORDNET = "grundlegend-gittergeordnet"


_init_map()

_TYP_MAP: dict[KristallgitterGeltung, KristallgitterTyp] = {
    KristallgitterGeltung.GESPERRT: KristallgitterTyp.SCHUTZ_KRISTALLGITTER,
    KristallgitterGeltung.GITTERGEORDNET: KristallgitterTyp.ORDNUNGS_KRISTALLGITTER,
    KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET: KristallgitterTyp.SOUVERAENITAETS_KRISTALLGITTER,
}

_PROZEDUR_MAP: dict[KristallgitterGeltung, KristallgitterProzedur] = {
    KristallgitterGeltung.GESPERRT: KristallgitterProzedur.NOTPROZEDUR,
    KristallgitterGeltung.GITTERGEORDNET: KristallgitterProzedur.REGELPROTOKOLL,
    KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET: KristallgitterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KristallgitterGeltung, float] = {
    KristallgitterGeltung.GESPERRT: 0.0,
    KristallgitterGeltung.GITTERGEORDNET: 0.04,
    KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET: 0.08,
}

_TIER_DELTA: dict[KristallgitterGeltung, int] = {
    KristallgitterGeltung.GESPERRT: 0,
    KristallgitterGeltung.GITTERGEORDNET: 1,
    KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KristallgitterNorm:
    kristallgitter_register_id: str
    kristallgitter_typ: KristallgitterTyp
    prozedur: KristallgitterProzedur
    geltung: KristallgitterGeltung
    kristallgitter_weight: float
    kristallgitter_tier: int
    canonical: bool
    kristallgitter_ids: tuple[str, ...]
    kristallgitter_tags: tuple[str, ...]


@dataclass(frozen=True)
class KristallgitterRegister:
    register_id: str
    festkoerper_feld: FestkoerperFeld
    normen: tuple[KristallgitterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kristallgitter_register_id for n in self.normen if n.geltung is KristallgitterGeltung.GESPERRT)

    @property
    def gittergeordnet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kristallgitter_register_id for n in self.normen if n.geltung is KristallgitterGeltung.GITTERGEORDNET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kristallgitter_register_id for n in self.normen if n.geltung is KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET)

    @property
    def register_signal(self):
        if any(n.geltung is KristallgitterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is KristallgitterGeltung.GITTERGEORDNET for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gittergeordnet")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-gittergeordnet")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kristallgitter_register(
    festkoerper_feld: FestkoerperFeld | None = None,
    *,
    register_id: str = "kristallgitter-register",
) -> KristallgitterRegister:
    if festkoerper_feld is None:
        festkoerper_feld = build_festkoerper_feld(feld_id=f"{register_id}-feld")

    normen: list[KristallgitterNorm] = []
    for parent_norm in festkoerper_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.festkoerper_feld_id.removeprefix(f'{festkoerper_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.festkoerper_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.festkoerper_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KristallgitterGeltung.GRUNDLEGEND_GITTERGEORDNET)
        normen.append(
            KristallgitterNorm(
                kristallgitter_register_id=new_id,
                kristallgitter_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kristallgitter_weight=new_weight,
                kristallgitter_tier=new_tier,
                canonical=is_canonical,
                kristallgitter_ids=parent_norm.festkoerper_ids + (new_id,),
                kristallgitter_tags=parent_norm.festkoerper_tags + (f"kristallgitter:{new_geltung.value}",),
            )
        )
    return KristallgitterRegister(
        register_id=register_id,
        festkoerper_feld=festkoerper_feld,
        normen=tuple(normen),
    )
