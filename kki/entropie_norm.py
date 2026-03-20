"""#288 – EntropieNorm (*_norm-Muster): Entropienormierung als Governance-Satzung.

Parent: boltzmann_senat (#287)
Hinweis: Container heißt EntropieNormSatz (norm_id), da EntropieNorm bereits
in entropie_register.py als Entry-Klasse vergeben ist.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .boltzmann_senat import (
    BoltzmannGeltung,
    BoltzmannSenat,
    build_boltzmann_senat,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EntropieNormTyp(Enum):
    SCHUTZ_ENTROPIENORM = "schutz-entropienorm"
    ORDNUNGS_ENTROPIENORM = "ordnungs-entropienorm"
    SOUVERAENITAETS_ENTROPIENORM = "souveraenitaets-entropienorm"


class EntropieNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EntropieNormGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTROPIENORMIERT = "entropienormiert"
    GRUNDLEGEND_ENTROPIENORMIERT = "grundlegend-entropienormiert"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[BoltzmannGeltung, EntropieNormGeltung] = {
    BoltzmannGeltung.GESPERRT: EntropieNormGeltung.GESPERRT,
    BoltzmannGeltung.STATISTISCH: EntropieNormGeltung.ENTROPIENORMIERT,
    BoltzmannGeltung.GRUNDLEGEND_STATISTISCH: EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT,
}

_TYP_MAP: dict[BoltzmannGeltung, EntropieNormTyp] = {
    BoltzmannGeltung.GESPERRT: EntropieNormTyp.SCHUTZ_ENTROPIENORM,
    BoltzmannGeltung.STATISTISCH: EntropieNormTyp.ORDNUNGS_ENTROPIENORM,
    BoltzmannGeltung.GRUNDLEGEND_STATISTISCH: EntropieNormTyp.SOUVERAENITAETS_ENTROPIENORM,
}

_PROZEDUR_MAP: dict[BoltzmannGeltung, EntropieNormProzedur] = {
    BoltzmannGeltung.GESPERRT: EntropieNormProzedur.NOTPROZEDUR,
    BoltzmannGeltung.STATISTISCH: EntropieNormProzedur.REGELPROTOKOLL,
    BoltzmannGeltung.GRUNDLEGEND_STATISTISCH: EntropieNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[BoltzmannGeltung, float] = {
    BoltzmannGeltung.GESPERRT: 0.0,
    BoltzmannGeltung.STATISTISCH: 0.04,
    BoltzmannGeltung.GRUNDLEGEND_STATISTISCH: 0.08,
}

_TIER_BONUS: dict[BoltzmannGeltung, int] = {
    BoltzmannGeltung.GESPERRT: 0,
    BoltzmannGeltung.STATISTISCH: 1,
    BoltzmannGeltung.GRUNDLEGEND_STATISTISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntropieNormEintrag:
    entropie_norm_id: str
    entropie_norm_typ: EntropieNormTyp
    prozedur: EntropieNormProzedur
    geltung: EntropieNormGeltung
    entropie_norm_weight: float
    entropie_norm_tier: int
    canonical: bool
    entropie_norm_ids: tuple[str, ...]
    entropie_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntropieNormSatz:
    norm_id: str
    boltzmann_senat: BoltzmannSenat
    normen: tuple[EntropieNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_norm_id for n in self.normen if n.geltung is EntropieNormGeltung.GESPERRT)

    @property
    def entropienormiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_norm_id for n in self.normen if n.geltung is EntropieNormGeltung.ENTROPIENORMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_norm_id for n in self.normen if n.geltung is EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT)

    @property
    def norm_signal(self):
        if any(n.geltung is EntropieNormGeltung.GESPERRT for n in self.normen):
            status = "norm-gesperrt"
            severity = "critical"
        elif any(n.geltung is EntropieNormGeltung.ENTROPIENORMIERT for n in self.normen):
            status = "norm-entropienormiert"
            severity = "warning"
        else:
            status = "norm-grundlegend-entropienormiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_entropie_norm(
    boltzmann_senat: BoltzmannSenat | None = None,
    *,
    norm_id: str = "entropie-norm",
) -> EntropieNormSatz:
    if boltzmann_senat is None:
        boltzmann_senat = build_boltzmann_senat(senat_id=f"{norm_id}-senat")

    normen: list[EntropieNormEintrag] = []
    for parent_norm in boltzmann_senat.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{norm_id}-{parent_norm.boltzmann_senat_id.removeprefix(f'{boltzmann_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.boltzmann_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.boltzmann_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT)
        normen.append(
            EntropieNormEintrag(
                entropie_norm_id=new_id,
                entropie_norm_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                entropie_norm_weight=raw_weight,
                entropie_norm_tier=new_tier,
                canonical=is_canonical,
                entropie_norm_ids=parent_norm.boltzmann_ids + (new_id,),
                entropie_norm_tags=parent_norm.boltzmann_tags + (f"entropie-norm:{new_geltung.value}",),
            )
        )

    return EntropieNormSatz(
        norm_id=norm_id,
        boltzmann_senat=boltzmann_senat,
        normen=tuple(normen),
    )
