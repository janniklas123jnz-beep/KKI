"""
#312 QuarkRegister — Quarks als Governance-Register mit Confinement-Prinzip.
Geltungsstufen: GESPERRT / QUARKGEBUNDEN / GRUNDLEGEND_QUARKGEBUNDEN
Parent: TeilchenFeld (#311)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .teilchen_feld import TeilchenFeld, TeilchenGeltung, build_teilchen_feld

_GELTUNG_MAP: dict[TeilchenGeltung, "QuarkGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[TeilchenGeltung.GESPERRT] = QuarkGeltung.GESPERRT
    _GELTUNG_MAP[TeilchenGeltung.TEILCHENGEBUNDEN] = QuarkGeltung.QUARKGEBUNDEN
    _GELTUNG_MAP[TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN] = QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN


class QuarkTyp(Enum):
    SCHUTZ_QUARK = "schutz-quark"
    ORDNUNGS_QUARK = "ordnungs-quark"
    SOUVERAENITAETS_QUARK = "souveraenitaets-quark"


class QuarkProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuarkGeltung(Enum):
    GESPERRT = "gesperrt"
    QUARKGEBUNDEN = "quarkgebunden"
    GRUNDLEGEND_QUARKGEBUNDEN = "grundlegend-quarkgebunden"


_init_map()

_TYP_MAP: dict[QuarkGeltung, QuarkTyp] = {
    QuarkGeltung.GESPERRT: QuarkTyp.SCHUTZ_QUARK,
    QuarkGeltung.QUARKGEBUNDEN: QuarkTyp.ORDNUNGS_QUARK,
    QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN: QuarkTyp.SOUVERAENITAETS_QUARK,
}

_PROZEDUR_MAP: dict[QuarkGeltung, QuarkProzedur] = {
    QuarkGeltung.GESPERRT: QuarkProzedur.NOTPROZEDUR,
    QuarkGeltung.QUARKGEBUNDEN: QuarkProzedur.REGELPROTOKOLL,
    QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN: QuarkProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[QuarkGeltung, float] = {
    QuarkGeltung.GESPERRT: 0.0,
    QuarkGeltung.QUARKGEBUNDEN: 0.04,
    QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN: 0.08,
}

_TIER_DELTA: dict[QuarkGeltung, int] = {
    QuarkGeltung.GESPERRT: 0,
    QuarkGeltung.QUARKGEBUNDEN: 1,
    QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN: 2,
}


@dataclass(frozen=True)
class QuarkNorm:
    quark_register_id: str
    quark_typ: QuarkTyp
    prozedur: QuarkProzedur
    geltung: QuarkGeltung
    quark_weight: float
    quark_tier: int
    canonical: bool
    quark_ids: tuple[str, ...]
    quark_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuarkRegister:
    register_id: str
    teilchen_feld: TeilchenFeld
    normen: tuple[QuarkNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quark_register_id for n in self.normen if n.geltung is QuarkGeltung.GESPERRT)

    @property
    def quarkgebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quark_register_id for n in self.normen if n.geltung is QuarkGeltung.QUARKGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quark_register_id for n in self.normen if n.geltung is QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN)

    @property
    def register_signal(self):
        if any(n.geltung is QuarkGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is QuarkGeltung.QUARKGEBUNDEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-quarkgebunden")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-quarkgebunden")


def build_quark_register(
    teilchen_feld: TeilchenFeld | None = None,
    *,
    register_id: str = "quark-register",
) -> QuarkRegister:
    if teilchen_feld is None:
        teilchen_feld = build_teilchen_feld(feld_id=f"{register_id}-feld")

    normen: list[QuarkNorm] = []
    for parent_norm in teilchen_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.teilchen_feld_id.removeprefix(f'{teilchen_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.teilchen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.teilchen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN)
        normen.append(
            QuarkNorm(
                quark_register_id=new_id,
                quark_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                quark_weight=new_weight,
                quark_tier=new_tier,
                canonical=is_canonical,
                quark_ids=parent_norm.teilchen_ids + (new_id,),
                quark_tags=parent_norm.teilchen_tags + (f"quark-register:{new_geltung.value}",),
            )
        )
    return QuarkRegister(
        register_id=register_id,
        teilchen_feld=teilchen_feld,
        normen=tuple(normen),
    )
