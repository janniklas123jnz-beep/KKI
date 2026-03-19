"""seins_charta — Metaphysik & Kosmologie layer 2 (#252)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ursprungs_axiom import (
    AxiomGeltung,
    AxiomProzedur,
    AxiomRang,
    UrsprungsAxiom,
    UrsprungsAxiomEintrag,
    build_ursprungs_axiom,
)

__all__ = [
    "SeinsTyp",
    "SeinsProzedur",
    "SeinsGeltung",
    "SeinsNorm",
    "SeinsCharta",
    "build_seins_charta",
]


class SeinsTyp(str, Enum):
    SCHUTZ_SEIN = "schutz-sein"
    ORDNUNGS_SEIN = "ordnungs-sein"
    SOUVERAENITAETS_SEIN = "souveraenitaets-sein"


class SeinsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SeinsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERANKERT = "verankert"
    GRUNDLEGEND_VERANKERT = "grundlegend-verankert"


_TYP_MAP: dict[AxiomGeltung, SeinsTyp] = {
    AxiomGeltung.GESPERRT: SeinsTyp.SCHUTZ_SEIN,
    AxiomGeltung.AXIOMATISCH: SeinsTyp.ORDNUNGS_SEIN,
    AxiomGeltung.GRUNDLEGEND_AXIOMATISCH: SeinsTyp.SOUVERAENITAETS_SEIN,
}
_PROZEDUR_MAP: dict[AxiomGeltung, SeinsProzedur] = {
    AxiomGeltung.GESPERRT: SeinsProzedur.NOTPROZEDUR,
    AxiomGeltung.AXIOMATISCH: SeinsProzedur.REGELPROTOKOLL,
    AxiomGeltung.GRUNDLEGEND_AXIOMATISCH: SeinsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[AxiomGeltung, SeinsGeltung] = {
    AxiomGeltung.GESPERRT: SeinsGeltung.GESPERRT,
    AxiomGeltung.AXIOMATISCH: SeinsGeltung.VERANKERT,
    AxiomGeltung.GRUNDLEGEND_AXIOMATISCH: SeinsGeltung.GRUNDLEGEND_VERANKERT,
}
_WEIGHT_BONUS: dict[AxiomGeltung, float] = {
    AxiomGeltung.GESPERRT: 0.0,
    AxiomGeltung.AXIOMATISCH: 0.04,
    AxiomGeltung.GRUNDLEGEND_AXIOMATISCH: 0.08,
}
_TIER_BONUS: dict[AxiomGeltung, int] = {
    AxiomGeltung.GESPERRT: 0,
    AxiomGeltung.AXIOMATISCH: 1,
    AxiomGeltung.GRUNDLEGEND_AXIOMATISCH: 2,
}


@dataclass(frozen=True)
class SeinsNorm:
    seins_charta_id: str
    seins_typ: SeinsTyp
    prozedur: SeinsProzedur
    geltung: SeinsGeltung
    seins_weight: float
    seins_tier: int
    canonical: bool
    seins_charta_ids: tuple[str, ...]
    seins_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class SeinsCharta:
    charta_id: str
    ursprungs_axiom: UrsprungsAxiom
    normen: tuple[SeinsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.seins_charta_id for n in self.normen if n.geltung is SeinsGeltung.GESPERRT)

    @property
    def verankert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.seins_charta_id for n in self.normen if n.geltung is SeinsGeltung.VERANKERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.seins_charta_id for n in self.normen if n.geltung is SeinsGeltung.GRUNDLEGEND_VERANKERT)

    @property
    def charta_signal(self):
        if any(n.geltung is SeinsGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is SeinsGeltung.VERANKERT for n in self.normen):
            status = "charta-verankert"
            severity = "warning"
        else:
            status = "charta-grundlegend-verankert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_seins_charta(
    ursprungs_axiom: UrsprungsAxiom | None = None,
    *,
    charta_id: str = "seins-charta",
) -> SeinsCharta:
    if ursprungs_axiom is None:
        ursprungs_axiom = build_ursprungs_axiom(axiom_id=f"{charta_id}-axiom")

    normen: list[SeinsNorm] = []
    for parent_norm in ursprungs_axiom.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.ursprungs_axiom_id.removeprefix(f'{ursprungs_axiom.axiom_id}-')}"
        raw_weight = min(1.0, round(parent_norm.axiom_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.axiom_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SeinsGeltung.GRUNDLEGEND_VERANKERT)
        normen.append(
            SeinsNorm(
                seins_charta_id=new_id,
                seins_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                seins_weight=raw_weight,
                seins_tier=new_tier,
                canonical=is_canonical,
                seins_charta_ids=parent_norm.ursprungs_axiom_ids + (new_id,),
                seins_charta_tags=parent_norm.ursprungs_axiom_tags + (f"seins-charta:{new_geltung.value}",),
            )
        )

    return SeinsCharta(
        charta_id=charta_id,
        ursprungs_axiom=ursprungs_axiom,
        normen=tuple(normen),
    )
