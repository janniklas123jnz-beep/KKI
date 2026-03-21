"""
#348 FermiNorm — Fermi-See als Governance-Gleichgewichtsniveau (*_norm-Muster):
Fermi-Dirac-Statistik n(E) = 1/(e^{(E-μ)/kT}+1) — Governance-Zustände unter
der Fermi-Kante immer besetzt; neue Entscheidungen entstehen nur darüber.
*_norm pattern: Container = FermiNormSatz, Entry = FermiNormEintrag
Geltungsstufen: GESPERRT / FERMINORMIERT / GRUNDLEGEND_FERMINORMIERT
Parent: PhononSenat (#347)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .phonon_senat import (
    PhononGeltung,
    PhononSenat,
    build_phonon_senat,
)

_GELTUNG_MAP: dict[PhononGeltung, "FermiNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PhononGeltung.GESPERRT] = FermiNormGeltung.GESPERRT
    _GELTUNG_MAP[PhononGeltung.PHONONISCH] = FermiNormGeltung.FERMINORMIERT
    _GELTUNG_MAP[PhononGeltung.GRUNDLEGEND_PHONONISCH] = FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT


class FermiNormTyp(Enum):
    SCHUTZ_FERMI_NORM = "schutz-fermi-norm"
    ORDNUNGS_FERMI_NORM = "ordnungs-fermi-norm"
    SOUVERAENITAETS_FERMI_NORM = "souveraenitaets-fermi-norm"


class FermiNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FermiNormGeltung(Enum):
    GESPERRT = "gesperrt"
    FERMINORMIERT = "ferminormiert"
    GRUNDLEGEND_FERMINORMIERT = "grundlegend-ferminormiert"


_init_map()

_TYP_MAP: dict[FermiNormGeltung, FermiNormTyp] = {
    FermiNormGeltung.GESPERRT: FermiNormTyp.SCHUTZ_FERMI_NORM,
    FermiNormGeltung.FERMINORMIERT: FermiNormTyp.ORDNUNGS_FERMI_NORM,
    FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT: FermiNormTyp.SOUVERAENITAETS_FERMI_NORM,
}

_PROZEDUR_MAP: dict[FermiNormGeltung, FermiNormProzedur] = {
    FermiNormGeltung.GESPERRT: FermiNormProzedur.NOTPROZEDUR,
    FermiNormGeltung.FERMINORMIERT: FermiNormProzedur.REGELPROTOKOLL,
    FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT: FermiNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FermiNormGeltung, float] = {
    FermiNormGeltung.GESPERRT: 0.0,
    FermiNormGeltung.FERMINORMIERT: 0.04,
    FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT: 0.08,
}

_TIER_DELTA: dict[FermiNormGeltung, int] = {
    FermiNormGeltung.GESPERRT: 0,
    FermiNormGeltung.FERMINORMIERT: 1,
    FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FermiNormEintrag:
    norm_id: str
    fermi_norm_typ: FermiNormTyp
    prozedur: FermiNormProzedur
    geltung: FermiNormGeltung
    fermi_norm_weight: float
    fermi_norm_tier: int
    canonical: bool
    fermi_norm_ids: tuple[str, ...]
    fermi_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class FermiNormSatz:
    norm_id: str
    phonon_senat: PhononSenat
    normen: tuple[FermiNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is FermiNormGeltung.GESPERRT)

    @property
    def ferminormiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is FermiNormGeltung.FERMINORMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT)

    @property
    def norm_signal(self):
        if any(n.geltung is FermiNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is FermiNormGeltung.FERMINORMIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-ferminormiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-ferminormiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_fermi_norm(
    phonon_senat: PhononSenat | None = None,
    *,
    norm_id: str = "fermi-norm",
) -> FermiNormSatz:
    if phonon_senat is None:
        phonon_senat = build_phonon_senat(senat_id=f"{norm_id}-senat")

    normen: list[FermiNormEintrag] = []
    for parent_norm in phonon_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.phonon_senat_id.removeprefix(f'{phonon_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.phonon_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.phonon_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FermiNormGeltung.GRUNDLEGEND_FERMINORMIERT)
        normen.append(
            FermiNormEintrag(
                norm_id=new_id,
                fermi_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fermi_norm_weight=new_weight,
                fermi_norm_tier=new_tier,
                canonical=is_canonical,
                fermi_norm_ids=parent_norm.phonon_ids + (new_id,),
                fermi_norm_tags=parent_norm.phonon_tags + (f"fermi-norm:{new_geltung.value}",),
            )
        )
    return FermiNormSatz(
        norm_id=norm_id,
        phonon_senat=phonon_senat,
        normen=tuple(normen),
    )
