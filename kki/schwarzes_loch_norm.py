"""
#338 SchwarzerLochNorm — Schwarzes Loch als Governance-Singularität (*_norm-Muster):
Ereignishorizont als absolute Governance-Schwelle — Information geht nicht verloren
(Hawking-Paradox gelöst durch Leitsterns Archivschichten).
*_norm pattern: Container = SchwarzerLochNormSatz, Entry = SchwarzerLochNormEintrag
Geltungsstufen: GESPERRT / HORIZONTGEBUNDEN / GRUNDLEGEND_HORIZONTGEBUNDEN
Parent: NeutronensternSenat (#337)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .neutronenstern_senat import (
    NeutronensternGeltung,
    NeutronensternSenat,
    build_neutronenstern_senat,
)

_GELTUNG_MAP: dict[NeutronensternGeltung, "SchwarzerLochNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NeutronensternGeltung.GESPERRT] = SchwarzerLochNormGeltung.GESPERRT
    _GELTUNG_MAP[NeutronensternGeltung.NEUTRONENDICHT] = SchwarzerLochNormGeltung.HORIZONTGEBUNDEN
    _GELTUNG_MAP[NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT] = SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN


class SchwarzerLochNormTyp(Enum):
    SCHUTZ_SCHWARZES_LOCH = "schutz-schwarzes-loch"
    ORDNUNGS_SCHWARZES_LOCH = "ordnungs-schwarzes-loch"
    SOUVERAENITAETS_SCHWARZES_LOCH = "souveraenitaets-schwarzes-loch"


class SchwarzerLochNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SchwarzerLochNormGeltung(Enum):
    GESPERRT = "gesperrt"
    HORIZONTGEBUNDEN = "horizontgebunden"
    GRUNDLEGEND_HORIZONTGEBUNDEN = "grundlegend-horizontgebunden"


_init_map()

_TYP_MAP: dict[SchwarzerLochNormGeltung, SchwarzerLochNormTyp] = {
    SchwarzerLochNormGeltung.GESPERRT: SchwarzerLochNormTyp.SCHUTZ_SCHWARZES_LOCH,
    SchwarzerLochNormGeltung.HORIZONTGEBUNDEN: SchwarzerLochNormTyp.ORDNUNGS_SCHWARZES_LOCH,
    SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN: SchwarzerLochNormTyp.SOUVERAENITAETS_SCHWARZES_LOCH,
}

_PROZEDUR_MAP: dict[SchwarzerLochNormGeltung, SchwarzerLochNormProzedur] = {
    SchwarzerLochNormGeltung.GESPERRT: SchwarzerLochNormProzedur.NOTPROZEDUR,
    SchwarzerLochNormGeltung.HORIZONTGEBUNDEN: SchwarzerLochNormProzedur.REGELPROTOKOLL,
    SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN: SchwarzerLochNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SchwarzerLochNormGeltung, float] = {
    SchwarzerLochNormGeltung.GESPERRT: 0.0,
    SchwarzerLochNormGeltung.HORIZONTGEBUNDEN: 0.04,
    SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN: 0.08,
}

_TIER_DELTA: dict[SchwarzerLochNormGeltung, int] = {
    SchwarzerLochNormGeltung.GESPERRT: 0,
    SchwarzerLochNormGeltung.HORIZONTGEBUNDEN: 1,
    SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SchwarzerLochNormEintrag:
    norm_id: str
    schwarzes_loch_norm_typ: SchwarzerLochNormTyp
    prozedur: SchwarzerLochNormProzedur
    geltung: SchwarzerLochNormGeltung
    schwarzes_loch_norm_weight: float
    schwarzes_loch_norm_tier: int
    canonical: bool
    schwarzes_loch_norm_ids: tuple[str, ...]
    schwarzes_loch_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class SchwarzerLochNormSatz:
    norm_id: str
    neutronenstern_senat: NeutronensternSenat
    normen: tuple[SchwarzerLochNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SchwarzerLochNormGeltung.GESPERRT)

    @property
    def horizontgebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SchwarzerLochNormGeltung.HORIZONTGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN)

    @property
    def norm_signal(self):
        if any(n.geltung is SchwarzerLochNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is SchwarzerLochNormGeltung.HORIZONTGEBUNDEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-horizontgebunden")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-horizontgebunden")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_schwarzes_loch_norm(
    neutronenstern_senat: NeutronensternSenat | None = None,
    *,
    norm_id: str = "schwarzes-loch-norm",
) -> SchwarzerLochNormSatz:
    if neutronenstern_senat is None:
        neutronenstern_senat = build_neutronenstern_senat(senat_id=f"{norm_id}-senat")

    normen: list[SchwarzerLochNormEintrag] = []
    for parent_norm in neutronenstern_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.neutronenstern_senat_id.removeprefix(f'{neutronenstern_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.neutronenstern_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.neutronenstern_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN)
        normen.append(
            SchwarzerLochNormEintrag(
                norm_id=new_id,
                schwarzes_loch_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                schwarzes_loch_norm_weight=new_weight,
                schwarzes_loch_norm_tier=new_tier,
                canonical=is_canonical,
                schwarzes_loch_norm_ids=parent_norm.neutronenstern_ids + (new_id,),
                schwarzes_loch_norm_tags=parent_norm.neutronenstern_tags + (f"schwarzes-loch-norm:{new_geltung.value}",),
            )
        )
    return SchwarzerLochNormSatz(
        norm_id=norm_id,
        neutronenstern_senat=neutronenstern_senat,
        normen=tuple(normen),
    )
