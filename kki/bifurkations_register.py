"""
#362 BifurkationsRegister — Das Bifurkationsdiagramm zeigt Phasenübergänge:
bei r < 3 stabiler Fixpunkt, bei r > 3 Periodenverdopplung, bei r > 3,57
deterministisches Chaos. Leitsterns Agenten erkennen Systemzustandsübergänge
und handeln antizipativ vor dem kritischen Punkt.
Geltungsstufen: GESPERRT / BIFURKIERT / GRUNDLEGEND_BIFURKIERT
Parent: LorenzAttraktorFeld (#361)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lorenz_attraktor_feld import (
    LorenzAttraktorFeld,
    LorenzAttraktorGeltung,
    build_lorenz_attraktor_feld,
)

_GELTUNG_MAP: dict[LorenzAttraktorGeltung, "BifurkationsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LorenzAttraktorGeltung.GESPERRT] = BifurkationsGeltung.GESPERRT
    _GELTUNG_MAP[LorenzAttraktorGeltung.LORENZATTRAHIERT] = BifurkationsGeltung.BIFURKIERT
    _GELTUNG_MAP[LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT] = BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT


class BifurkationsTyp(Enum):
    SCHUTZ_BIFURKATION = "schutz-bifurkation"
    ORDNUNGS_BIFURKATION = "ordnungs-bifurkation"
    SOUVERAENITAETS_BIFURKATION = "souveraenitaets-bifurkation"


class BifurkationsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BifurkationsGeltung(Enum):
    GESPERRT = "gesperrt"
    BIFURKIERT = "bifurkiert"
    GRUNDLEGEND_BIFURKIERT = "grundlegend-bifurkiert"


_init_map()

_TYP_MAP: dict[BifurkationsGeltung, BifurkationsTyp] = {
    BifurkationsGeltung.GESPERRT: BifurkationsTyp.SCHUTZ_BIFURKATION,
    BifurkationsGeltung.BIFURKIERT: BifurkationsTyp.ORDNUNGS_BIFURKATION,
    BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT: BifurkationsTyp.SOUVERAENITAETS_BIFURKATION,
}

_PROZEDUR_MAP: dict[BifurkationsGeltung, BifurkationsProzedur] = {
    BifurkationsGeltung.GESPERRT: BifurkationsProzedur.NOTPROZEDUR,
    BifurkationsGeltung.BIFURKIERT: BifurkationsProzedur.REGELPROTOKOLL,
    BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT: BifurkationsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[BifurkationsGeltung, float] = {
    BifurkationsGeltung.GESPERRT: 0.0,
    BifurkationsGeltung.BIFURKIERT: 0.04,
    BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT: 0.08,
}

_TIER_DELTA: dict[BifurkationsGeltung, int] = {
    BifurkationsGeltung.GESPERRT: 0,
    BifurkationsGeltung.BIFURKIERT: 1,
    BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BifurkationsNorm:
    bifurkations_register_id: str
    bifurkations_typ: BifurkationsTyp
    prozedur: BifurkationsProzedur
    geltung: BifurkationsGeltung
    bifurkations_weight: float
    bifurkations_tier: int
    canonical: bool
    bifurkations_ids: tuple[str, ...]
    bifurkations_tags: tuple[str, ...]


@dataclass(frozen=True)
class BifurkationsRegister:
    register_id: str
    lorenz_attraktor_feld: LorenzAttraktorFeld
    normen: tuple[BifurkationsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bifurkations_register_id for n in self.normen if n.geltung is BifurkationsGeltung.GESPERRT)

    @property
    def bifurkiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bifurkations_register_id for n in self.normen if n.geltung is BifurkationsGeltung.BIFURKIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bifurkations_register_id for n in self.normen if n.geltung is BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT)

    @property
    def register_signal(self):
        if any(n.geltung is BifurkationsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is BifurkationsGeltung.BIFURKIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-bifurkiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-bifurkiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_bifurkations_register(
    lorenz_attraktor_feld: LorenzAttraktorFeld | None = None,
    *,
    register_id: str = "bifurkations-register",
) -> BifurkationsRegister:
    if lorenz_attraktor_feld is None:
        lorenz_attraktor_feld = build_lorenz_attraktor_feld(feld_id=f"{register_id}-feld")

    normen: list[BifurkationsNorm] = []
    for parent_norm in lorenz_attraktor_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.lorenz_attraktor_feld_id.removeprefix(f'{lorenz_attraktor_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.lorenz_attraktor_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.lorenz_attraktor_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT)
        normen.append(
            BifurkationsNorm(
                bifurkations_register_id=new_id,
                bifurkations_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                bifurkations_weight=new_weight,
                bifurkations_tier=new_tier,
                canonical=is_canonical,
                bifurkations_ids=parent_norm.lorenz_attraktor_ids + (new_id,),
                bifurkations_tags=parent_norm.lorenz_attraktor_tags + (f"bifurkation:{new_geltung.value}",),
            )
        )
    return BifurkationsRegister(
        register_id=register_id,
        lorenz_attraktor_feld=lorenz_attraktor_feld,
        normen=tuple(normen),
    )
