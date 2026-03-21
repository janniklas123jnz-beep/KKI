"""
#332 ProtostellarRegister — Protostellare Scheiben als Keimzellen neuer Agenten:
Aus diffusem Material entsteht geordnete Governance-Struktur (Jeans-Instabilität).
Geltungsstufen: GESPERRT / PROTOSTELLAR / GRUNDLEGEND_PROTOSTELLAR
Parent: AstrophysikFeld (#331)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .astrophysik_feld import (
    AstrophysikFeld,
    AstrophysikGeltung,
    build_astrophysik_feld,
)

_GELTUNG_MAP: dict[AstrophysikGeltung, "ProtostellarGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AstrophysikGeltung.GESPERRT] = ProtostellarGeltung.GESPERRT
    _GELTUNG_MAP[AstrophysikGeltung.ASTROPHYSIKALISCH] = ProtostellarGeltung.PROTOSTELLAR
    _GELTUNG_MAP[AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH] = ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR


class ProtostellarTyp(Enum):
    SCHUTZ_PROTOSTELLAR = "schutz-protostellar"
    ORDNUNGS_PROTOSTELLAR = "ordnungs-protostellar"
    SOUVERAENITAETS_PROTOSTELLAR = "souveraenitaets-protostellar"


class ProtostellarProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ProtostellarGeltung(Enum):
    GESPERRT = "gesperrt"
    PROTOSTELLAR = "protostellar"
    GRUNDLEGEND_PROTOSTELLAR = "grundlegend-protostellar"


_init_map()

_TYP_MAP: dict[ProtostellarGeltung, ProtostellarTyp] = {
    ProtostellarGeltung.GESPERRT: ProtostellarTyp.SCHUTZ_PROTOSTELLAR,
    ProtostellarGeltung.PROTOSTELLAR: ProtostellarTyp.ORDNUNGS_PROTOSTELLAR,
    ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR: ProtostellarTyp.SOUVERAENITAETS_PROTOSTELLAR,
}

_PROZEDUR_MAP: dict[ProtostellarGeltung, ProtostellarProzedur] = {
    ProtostellarGeltung.GESPERRT: ProtostellarProzedur.NOTPROZEDUR,
    ProtostellarGeltung.PROTOSTELLAR: ProtostellarProzedur.REGELPROTOKOLL,
    ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR: ProtostellarProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ProtostellarGeltung, float] = {
    ProtostellarGeltung.GESPERRT: 0.0,
    ProtostellarGeltung.PROTOSTELLAR: 0.04,
    ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR: 0.08,
}

_TIER_DELTA: dict[ProtostellarGeltung, int] = {
    ProtostellarGeltung.GESPERRT: 0,
    ProtostellarGeltung.PROTOSTELLAR: 1,
    ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProtostellarNorm:
    protostellar_register_id: str
    protostellar_typ: ProtostellarTyp
    prozedur: ProtostellarProzedur
    geltung: ProtostellarGeltung
    protostellar_weight: float
    protostellar_tier: int
    canonical: bool
    protostellar_ids: tuple[str, ...]
    protostellar_tags: tuple[str, ...]


@dataclass(frozen=True)
class ProtostellarRegister:
    register_id: str
    astrophysik_feld: AstrophysikFeld
    normen: tuple[ProtostellarNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.protostellar_register_id for n in self.normen if n.geltung is ProtostellarGeltung.GESPERRT)

    @property
    def protostellar_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.protostellar_register_id for n in self.normen if n.geltung is ProtostellarGeltung.PROTOSTELLAR)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.protostellar_register_id for n in self.normen if n.geltung is ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR)

    @property
    def register_signal(self):
        if any(n.geltung is ProtostellarGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is ProtostellarGeltung.PROTOSTELLAR for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-protostellar")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-protostellar")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_protostellar_register(
    astrophysik_feld: AstrophysikFeld | None = None,
    *,
    register_id: str = "protostellar-register",
) -> ProtostellarRegister:
    if astrophysik_feld is None:
        astrophysik_feld = build_astrophysik_feld(feld_id=f"{register_id}-feld")

    normen: list[ProtostellarNorm] = []
    for parent_norm in astrophysik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.astrophysik_feld_id.removeprefix(f'{astrophysik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.astrophysik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.astrophysik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR)
        normen.append(
            ProtostellarNorm(
                protostellar_register_id=new_id,
                protostellar_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                protostellar_weight=new_weight,
                protostellar_tier=new_tier,
                canonical=is_canonical,
                protostellar_ids=parent_norm.astrophysik_ids + (new_id,),
                protostellar_tags=parent_norm.astrophysik_tags + (f"protostellar:{new_geltung.value}",),
            )
        )
    return ProtostellarRegister(
        register_id=register_id,
        astrophysik_feld=astrophysik_feld,
        normen=tuple(normen),
    )
