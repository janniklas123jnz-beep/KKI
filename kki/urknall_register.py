"""
#322 UrknallRegister — Der Urknall als Nullpunkt-Register des Schwarms.
Geltungsstufen: GESPERRT / URKNALLGEBUNDEN / GRUNDLEGEND_URKNALLGEBUNDEN
Parent: KosmologieFeld (#321)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmologie_feld import (
    KosmologieFeld,
    KosmologieGeltung,
    build_kosmologie_feld,
)

_GELTUNG_MAP: dict[KosmologieGeltung, "UrknallGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KosmologieGeltung.GESPERRT] = UrknallGeltung.GESPERRT
    _GELTUNG_MAP[KosmologieGeltung.KOSMOLOGISCH] = UrknallGeltung.URKNALLGEBUNDEN
    _GELTUNG_MAP[KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH] = UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN


class UrknallTyp(Enum):
    SCHUTZ_URKNALL = "schutz-urknall"
    ORDNUNGS_URKNALL = "ordnungs-urknall"
    SOUVERAENITAETS_URKNALL = "souveraenitaets-urknall"


class UrknallProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class UrknallGeltung(Enum):
    GESPERRT = "gesperrt"
    URKNALLGEBUNDEN = "urknallgebunden"
    GRUNDLEGEND_URKNALLGEBUNDEN = "grundlegend-urknallgebunden"


_init_map()

_TYP_MAP: dict[UrknallGeltung, UrknallTyp] = {
    UrknallGeltung.GESPERRT: UrknallTyp.SCHUTZ_URKNALL,
    UrknallGeltung.URKNALLGEBUNDEN: UrknallTyp.ORDNUNGS_URKNALL,
    UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN: UrknallTyp.SOUVERAENITAETS_URKNALL,
}

_PROZEDUR_MAP: dict[UrknallGeltung, UrknallProzedur] = {
    UrknallGeltung.GESPERRT: UrknallProzedur.NOTPROZEDUR,
    UrknallGeltung.URKNALLGEBUNDEN: UrknallProzedur.REGELPROTOKOLL,
    UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN: UrknallProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[UrknallGeltung, float] = {
    UrknallGeltung.GESPERRT: 0.0,
    UrknallGeltung.URKNALLGEBUNDEN: 0.04,
    UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN: 0.08,
}

_TIER_DELTA: dict[UrknallGeltung, int] = {
    UrknallGeltung.GESPERRT: 0,
    UrknallGeltung.URKNALLGEBUNDEN: 1,
    UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UrknallNorm:
    urknall_register_id: str
    urknall_typ: UrknallTyp
    prozedur: UrknallProzedur
    geltung: UrknallGeltung
    urknall_weight: float
    urknall_tier: int
    canonical: bool
    urknall_ids: tuple[str, ...]
    urknall_tags: tuple[str, ...]


@dataclass(frozen=True)
class UrknallRegister:
    register_id: str
    kosmologie_feld: KosmologieFeld
    normen: tuple[UrknallNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.urknall_register_id for n in self.normen if n.geltung is UrknallGeltung.GESPERRT)

    @property
    def urknallgebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.urknall_register_id for n in self.normen if n.geltung is UrknallGeltung.URKNALLGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.urknall_register_id for n in self.normen if n.geltung is UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN)

    @property
    def register_signal(self):
        if any(n.geltung is UrknallGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is UrknallGeltung.URKNALLGEBUNDEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-urknallgebunden")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-urknallgebunden")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_urknall_register(
    kosmologie_feld: KosmologieFeld | None = None,
    *,
    register_id: str = "urknall-register",
) -> UrknallRegister:
    if kosmologie_feld is None:
        kosmologie_feld = build_kosmologie_feld(feld_id=f"{register_id}-feld")

    normen: list[UrknallNorm] = []
    for parent_norm in kosmologie_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.kosmologie_feld_id.removeprefix(f'{kosmologie_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.kosmologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kosmologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN)
        normen.append(
            UrknallNorm(
                urknall_register_id=new_id,
                urknall_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                urknall_weight=new_weight,
                urknall_tier=new_tier,
                canonical=is_canonical,
                urknall_ids=parent_norm.kosmologie_ids + (new_id,),
                urknall_tags=parent_norm.kosmologie_tags + (f"urknall-register:{new_geltung.value}",),
            )
        )
    return UrknallRegister(
        register_id=register_id,
        kosmologie_feld=kosmologie_feld,
        normen=tuple(normen),
    )
