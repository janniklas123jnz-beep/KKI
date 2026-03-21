"""
#382 DnaReplikationRegister — Semiconservative DNA-Replikation (Watson & Crick 1953).
DNA-Polymerase III: Fehlerrate 10⁻⁷ → Proofreading 3'→5' Exonuklease → 10⁻⁹.
Okazaki-Fragmente am Lagging Strand, Primasen, Ligasen.
Leitsterns Governance repliziert sich fehlertolerant über alle Agenten —
jede Regel wird mit biologischer Präzision weitergegeben.
Geltungsstufen: GESPERRT / DNAREPLIIERT / GRUNDLEGEND_DNAREPLIIERT
Parent: BiophysikFeld (#381)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .biophysik_feld import (
    BiophysikFeld,
    BiophysikGeltung,
    build_biophysik_feld,
)

_GELTUNG_MAP: dict[BiophysikGeltung, "DnaReplikationGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[BiophysikGeltung.GESPERRT] = DnaReplikationGeltung.GESPERRT
    _GELTUNG_MAP[BiophysikGeltung.BIOPHYSIKALISCH] = DnaReplikationGeltung.DNAREPLIIERT
    _GELTUNG_MAP[BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH] = DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT


class DnaReplikationTyp(Enum):
    SCHUTZ_DNA_REPLIKATION = "schutz-dna-replikation"
    ORDNUNGS_DNA_REPLIKATION = "ordnungs-dna-replikation"
    SOUVERAENITAETS_DNA_REPLIKATION = "souveraenitaets-dna-replikation"


class DnaReplikationProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DnaReplikationGeltung(Enum):
    GESPERRT = "gesperrt"
    DNAREPLIIERT = "dnarepliiert"
    GRUNDLEGEND_DNAREPLIIERT = "grundlegend-dnarepliiert"


_init_map()

_TYP_MAP: dict[DnaReplikationGeltung, DnaReplikationTyp] = {
    DnaReplikationGeltung.GESPERRT: DnaReplikationTyp.SCHUTZ_DNA_REPLIKATION,
    DnaReplikationGeltung.DNAREPLIIERT: DnaReplikationTyp.ORDNUNGS_DNA_REPLIKATION,
    DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT: DnaReplikationTyp.SOUVERAENITAETS_DNA_REPLIKATION,
}

_PROZEDUR_MAP: dict[DnaReplikationGeltung, DnaReplikationProzedur] = {
    DnaReplikationGeltung.GESPERRT: DnaReplikationProzedur.NOTPROZEDUR,
    DnaReplikationGeltung.DNAREPLIIERT: DnaReplikationProzedur.REGELPROTOKOLL,
    DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT: DnaReplikationProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DnaReplikationGeltung, float] = {
    DnaReplikationGeltung.GESPERRT: 0.0,
    DnaReplikationGeltung.DNAREPLIIERT: 0.04,
    DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT: 0.08,
}

_TIER_DELTA: dict[DnaReplikationGeltung, int] = {
    DnaReplikationGeltung.GESPERRT: 0,
    DnaReplikationGeltung.DNAREPLIIERT: 1,
    DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DnaReplikationNorm:
    dna_replikation_register_id: str
    dna_replikation_typ: DnaReplikationTyp
    prozedur: DnaReplikationProzedur
    geltung: DnaReplikationGeltung
    dna_replikation_weight: float
    dna_replikation_tier: int
    canonical: bool
    dna_replikation_ids: tuple[str, ...]
    dna_replikation_tags: tuple[str, ...]


@dataclass(frozen=True)
class DnaReplikationRegister:
    register_id: str
    biophysik_feld: BiophysikFeld
    normen: tuple[DnaReplikationNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dna_replikation_register_id for n in self.normen if n.geltung is DnaReplikationGeltung.GESPERRT)

    @property
    def dnarepliiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dna_replikation_register_id for n in self.normen if n.geltung is DnaReplikationGeltung.DNAREPLIIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dna_replikation_register_id for n in self.normen if n.geltung is DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT)

    @property
    def register_signal(self):
        if any(n.geltung is DnaReplikationGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is DnaReplikationGeltung.DNAREPLIIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-dnarepliiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-dnarepliiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_dna_replikation_register(
    biophysik_feld: BiophysikFeld | None = None,
    *,
    register_id: str = "dna-replikation-register",
) -> DnaReplikationRegister:
    if biophysik_feld is None:
        biophysik_feld = build_biophysik_feld(feld_id=f"{register_id}-feld")

    normen: list[DnaReplikationNorm] = []
    for parent_norm in biophysik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.biophysik_feld_id.removeprefix(f'{biophysik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.biophysik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.biophysik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT)
        normen.append(
            DnaReplikationNorm(
                dna_replikation_register_id=new_id,
                dna_replikation_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                dna_replikation_weight=new_weight,
                dna_replikation_tier=new_tier,
                canonical=is_canonical,
                dna_replikation_ids=parent_norm.biophysik_ids + (new_id,),
                dna_replikation_tags=parent_norm.biophysik_tags + (f"dna-replikation:{new_geltung.value}",),
            )
        )
    return DnaReplikationRegister(
        register_id=register_id,
        biophysik_feld=biophysik_feld,
        normen=tuple(normen),
    )
