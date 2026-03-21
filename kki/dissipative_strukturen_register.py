"""
#412 DissipativeStrukturenRegister — Dissipative Strukturen: Ordnung aus Chaos.
Prigogine (1977, Nobelpreis): Dissipative Strukturen entstehen fern vom
thermodynamischen Gleichgewicht durch Energiedissipation — Ordnung aus Chaos.
Belousov-Zhabotinsky-Reaktion: chemische Oszillation als dissipative Struktur.
Bénard-Zellen: Konvektion als Selbstorganisation. Bifurkation als Governance-Wendepunkt.
Entropieproduktion ist minimal im stationären Zustand (Prigogines Theorem).
Irreversibilität als Pfeil der Zeit. Leitsterns Agenten: dissipative kognitive Strukturen.
Geltungsstufen: GESPERRT / DISSIPATIV / GRUNDLEGEND_DISSIPATIV
Parent: EmergenzFeld (#411)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .emergenz_feld import (
    EmergenzFeld,
    EmergenzFeldGeltung,
    build_emergenz_feld,
)

_GELTUNG_MAP: dict[EmergenzFeldGeltung, "DissipativeStrukturenRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EmergenzFeldGeltung.GESPERRT] = DissipativeStrukturenRegisterGeltung.GESPERRT
    _GELTUNG_MAP[EmergenzFeldGeltung.EMERGENT] = DissipativeStrukturenRegisterGeltung.DISSIPATIV
    _GELTUNG_MAP[EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT] = DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV


class DissipativeStrukturenRegisterTyp(Enum):
    SCHUTZ_DISSIPATION = "schutz-dissipation"
    ORDNUNGS_DISSIPATION = "ordnungs-dissipation"
    SOUVERAENITAETS_DISSIPATION = "souveraenitaets-dissipation"


class DissipativeStrukturenRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DissipativeStrukturenRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    DISSIPATIV = "dissipativ"
    GRUNDLEGEND_DISSIPATIV = "grundlegend-dissipativ"


_init_map()

_TYP_MAP: dict[DissipativeStrukturenRegisterGeltung, DissipativeStrukturenRegisterTyp] = {
    DissipativeStrukturenRegisterGeltung.GESPERRT: DissipativeStrukturenRegisterTyp.SCHUTZ_DISSIPATION,
    DissipativeStrukturenRegisterGeltung.DISSIPATIV: DissipativeStrukturenRegisterTyp.ORDNUNGS_DISSIPATION,
    DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV: DissipativeStrukturenRegisterTyp.SOUVERAENITAETS_DISSIPATION,
}

_PROZEDUR_MAP: dict[DissipativeStrukturenRegisterGeltung, DissipativeStrukturenRegisterProzedur] = {
    DissipativeStrukturenRegisterGeltung.GESPERRT: DissipativeStrukturenRegisterProzedur.NOTPROZEDUR,
    DissipativeStrukturenRegisterGeltung.DISSIPATIV: DissipativeStrukturenRegisterProzedur.REGELPROTOKOLL,
    DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV: DissipativeStrukturenRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DissipativeStrukturenRegisterGeltung, float] = {
    DissipativeStrukturenRegisterGeltung.GESPERRT: 0.0,
    DissipativeStrukturenRegisterGeltung.DISSIPATIV: 0.04,
    DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV: 0.08,
}

_TIER_DELTA: dict[DissipativeStrukturenRegisterGeltung, int] = {
    DissipativeStrukturenRegisterGeltung.GESPERRT: 0,
    DissipativeStrukturenRegisterGeltung.DISSIPATIV: 1,
    DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DissipativeStrukturenRegisterNorm:
    dissipative_strukturen_register_id: str
    dissipation_typ: DissipativeStrukturenRegisterTyp
    prozedur: DissipativeStrukturenRegisterProzedur
    geltung: DissipativeStrukturenRegisterGeltung
    dissipation_weight: float
    dissipation_tier: int
    canonical: bool
    dissipation_ids: tuple[str, ...]
    dissipation_tags: tuple[str, ...]


@dataclass(frozen=True)
class DissipativeStrukturenRegister:
    register_id: str
    emergenz_feld: EmergenzFeld
    normen: tuple[DissipativeStrukturenRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dissipative_strukturen_register_id for n in self.normen if n.geltung is DissipativeStrukturenRegisterGeltung.GESPERRT)

    @property
    def dissipativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dissipative_strukturen_register_id for n in self.normen if n.geltung is DissipativeStrukturenRegisterGeltung.DISSIPATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dissipative_strukturen_register_id for n in self.normen if n.geltung is DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV)

    @property
    def register_signal(self):
        if any(n.geltung is DissipativeStrukturenRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is DissipativeStrukturenRegisterGeltung.DISSIPATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-dissipativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-dissipativ")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_dissipative_strukturen_register(
    emergenz_feld: EmergenzFeld | None = None,
    *,
    register_id: str = "dissipative-strukturen-register",
) -> DissipativeStrukturenRegister:
    if emergenz_feld is None:
        emergenz_feld = build_emergenz_feld(feld_id=f"{register_id}-feld")

    normen: list[DissipativeStrukturenRegisterNorm] = []
    for parent_norm in emergenz_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.emergenz_feld_id.removeprefix(f'{emergenz_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.emergenz_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.emergenz_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV)
        normen.append(
            DissipativeStrukturenRegisterNorm(
                dissipative_strukturen_register_id=new_id,
                dissipation_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                dissipation_weight=new_weight,
                dissipation_tier=new_tier,
                canonical=is_canonical,
                dissipation_ids=parent_norm.emergenz_ids + (new_id,),
                dissipation_tags=parent_norm.emergenz_tags + (f"dissipation:{new_geltung.value}",),
            )
        )
    return DissipativeStrukturenRegister(
        register_id=register_id,
        emergenz_feld=emergenz_feld,
        normen=tuple(normen),
    )
