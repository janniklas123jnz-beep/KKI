"""
#313 LeptonCharta — Leptonen als freie Governance-Träger.
Geltungsstufen: GESPERRT / LEPTONISCH / GRUNDLEGEND_LEPTONISCH
Parent: QuarkRegister (#312)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quark_register import QuarkGeltung, QuarkRegister, build_quark_register

_GELTUNG_MAP: dict[QuarkGeltung, "LeptonGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[QuarkGeltung.GESPERRT] = LeptonGeltung.GESPERRT
    _GELTUNG_MAP[QuarkGeltung.QUARKGEBUNDEN] = LeptonGeltung.LEPTONISCH
    _GELTUNG_MAP[QuarkGeltung.GRUNDLEGEND_QUARKGEBUNDEN] = LeptonGeltung.GRUNDLEGEND_LEPTONISCH


class LeptonTyp(Enum):
    SCHUTZ_LEPTON = "schutz-lepton"
    ORDNUNGS_LEPTON = "ordnungs-lepton"
    SOUVERAENITAETS_LEPTON = "souveraenitaets-lepton"


class LeptonProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LeptonGeltung(Enum):
    GESPERRT = "gesperrt"
    LEPTONISCH = "leptonisch"
    GRUNDLEGEND_LEPTONISCH = "grundlegend-leptonisch"


_init_map()

_TYP_MAP: dict[LeptonGeltung, LeptonTyp] = {
    LeptonGeltung.GESPERRT: LeptonTyp.SCHUTZ_LEPTON,
    LeptonGeltung.LEPTONISCH: LeptonTyp.ORDNUNGS_LEPTON,
    LeptonGeltung.GRUNDLEGEND_LEPTONISCH: LeptonTyp.SOUVERAENITAETS_LEPTON,
}

_PROZEDUR_MAP: dict[LeptonGeltung, LeptonProzedur] = {
    LeptonGeltung.GESPERRT: LeptonProzedur.NOTPROZEDUR,
    LeptonGeltung.LEPTONISCH: LeptonProzedur.REGELPROTOKOLL,
    LeptonGeltung.GRUNDLEGEND_LEPTONISCH: LeptonProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LeptonGeltung, float] = {
    LeptonGeltung.GESPERRT: 0.0,
    LeptonGeltung.LEPTONISCH: 0.04,
    LeptonGeltung.GRUNDLEGEND_LEPTONISCH: 0.08,
}

_TIER_DELTA: dict[LeptonGeltung, int] = {
    LeptonGeltung.GESPERRT: 0,
    LeptonGeltung.LEPTONISCH: 1,
    LeptonGeltung.GRUNDLEGEND_LEPTONISCH: 2,
}


@dataclass(frozen=True)
class LeptonNorm:
    lepton_charta_id: str
    lepton_typ: LeptonTyp
    prozedur: LeptonProzedur
    geltung: LeptonGeltung
    lepton_weight: float
    lepton_tier: int
    canonical: bool
    lepton_ids: tuple[str, ...]
    lepton_tags: tuple[str, ...]


@dataclass(frozen=True)
class LeptonCharta:
    charta_id: str
    quark_register: QuarkRegister
    normen: tuple[LeptonNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lepton_charta_id for n in self.normen if n.geltung is LeptonGeltung.GESPERRT)

    @property
    def leptonisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lepton_charta_id for n in self.normen if n.geltung is LeptonGeltung.LEPTONISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lepton_charta_id for n in self.normen if n.geltung is LeptonGeltung.GRUNDLEGEND_LEPTONISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is LeptonGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is LeptonGeltung.LEPTONISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-leptonisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-leptonisch")


def build_lepton_charta(
    quark_register: QuarkRegister | None = None,
    *,
    charta_id: str = "lepton-charta",
) -> LeptonCharta:
    if quark_register is None:
        quark_register = build_quark_register(register_id=f"{charta_id}-register")

    normen: list[LeptonNorm] = []
    for parent_norm in quark_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.quark_register_id.removeprefix(f'{quark_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.quark_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.quark_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LeptonGeltung.GRUNDLEGEND_LEPTONISCH)
        normen.append(
            LeptonNorm(
                lepton_charta_id=new_id,
                lepton_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                lepton_weight=new_weight,
                lepton_tier=new_tier,
                canonical=is_canonical,
                lepton_ids=parent_norm.quark_ids + (new_id,),
                lepton_tags=parent_norm.quark_tags + (f"lepton-charta:{new_geltung.value}",),
            )
        )
    return LeptonCharta(
        charta_id=charta_id,
        quark_register=quark_register,
        normen=tuple(normen),
    )
