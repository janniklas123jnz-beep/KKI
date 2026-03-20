"""
#314 GluonKodex — Gluonen als Bindungs-Governance-Kodex der Starken Kraft.
Geltungsstufen: GESPERRT / GLUONISCH / GRUNDLEGEND_GLUONISCH
Parent: LeptonCharta (#313)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lepton_charta import LeptonCharta, LeptonGeltung, build_lepton_charta

_GELTUNG_MAP: dict[LeptonGeltung, "GluonGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LeptonGeltung.GESPERRT] = GluonGeltung.GESPERRT
    _GELTUNG_MAP[LeptonGeltung.LEPTONISCH] = GluonGeltung.GLUONISCH
    _GELTUNG_MAP[LeptonGeltung.GRUNDLEGEND_LEPTONISCH] = GluonGeltung.GRUNDLEGEND_GLUONISCH


class GluonTyp(Enum):
    SCHUTZ_GLUON = "schutz-gluon"
    ORDNUNGS_GLUON = "ordnungs-gluon"
    SOUVERAENITAETS_GLUON = "souveraenitaets-gluon"


class GluonProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GluonGeltung(Enum):
    GESPERRT = "gesperrt"
    GLUONISCH = "gluonisch"
    GRUNDLEGEND_GLUONISCH = "grundlegend-gluonisch"


_init_map()

_TYP_MAP: dict[GluonGeltung, GluonTyp] = {
    GluonGeltung.GESPERRT: GluonTyp.SCHUTZ_GLUON,
    GluonGeltung.GLUONISCH: GluonTyp.ORDNUNGS_GLUON,
    GluonGeltung.GRUNDLEGEND_GLUONISCH: GluonTyp.SOUVERAENITAETS_GLUON,
}

_PROZEDUR_MAP: dict[GluonGeltung, GluonProzedur] = {
    GluonGeltung.GESPERRT: GluonProzedur.NOTPROZEDUR,
    GluonGeltung.GLUONISCH: GluonProzedur.REGELPROTOKOLL,
    GluonGeltung.GRUNDLEGEND_GLUONISCH: GluonProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GluonGeltung, float] = {
    GluonGeltung.GESPERRT: 0.0,
    GluonGeltung.GLUONISCH: 0.04,
    GluonGeltung.GRUNDLEGEND_GLUONISCH: 0.08,
}

_TIER_DELTA: dict[GluonGeltung, int] = {
    GluonGeltung.GESPERRT: 0,
    GluonGeltung.GLUONISCH: 1,
    GluonGeltung.GRUNDLEGEND_GLUONISCH: 2,
}


@dataclass(frozen=True)
class GluonNorm:
    gluon_kodex_id: str
    gluon_typ: GluonTyp
    prozedur: GluonProzedur
    geltung: GluonGeltung
    gluon_weight: float
    gluon_tier: int
    canonical: bool
    gluon_ids: tuple[str, ...]
    gluon_tags: tuple[str, ...]


@dataclass(frozen=True)
class GluonKodex:
    kodex_id: str
    lepton_charta: LeptonCharta
    normen: tuple[GluonNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gluon_kodex_id for n in self.normen if n.geltung is GluonGeltung.GESPERRT)

    @property
    def gluonisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gluon_kodex_id for n in self.normen if n.geltung is GluonGeltung.GLUONISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gluon_kodex_id for n in self.normen if n.geltung is GluonGeltung.GRUNDLEGEND_GLUONISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is GluonGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is GluonGeltung.GLUONISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gluonisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-gluonisch")


def build_gluon_kodex(
    lepton_charta: LeptonCharta | None = None,
    *,
    kodex_id: str = "gluon-kodex",
) -> GluonKodex:
    if lepton_charta is None:
        lepton_charta = build_lepton_charta(charta_id=f"{kodex_id}-charta")

    normen: list[GluonNorm] = []
    for parent_norm in lepton_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.lepton_charta_id.removeprefix(f'{lepton_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.lepton_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.lepton_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GluonGeltung.GRUNDLEGEND_GLUONISCH)
        normen.append(
            GluonNorm(
                gluon_kodex_id=new_id,
                gluon_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gluon_weight=new_weight,
                gluon_tier=new_tier,
                canonical=is_canonical,
                gluon_ids=parent_norm.lepton_ids + (new_id,),
                gluon_tags=parent_norm.lepton_tags + (f"gluon-kodex:{new_geltung.value}",),
            )
        )
    return GluonKodex(
        kodex_id=kodex_id,
        lepton_charta=lepton_charta,
        normen=tuple(normen),
    )
