"""#294 – InduktionsKodex: Elektromagnetische Induktion als Governance-Kodex.

Parent: maxwell_charta (#293)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .maxwell_charta import (
    MaxwellGeltung,
    MaxwellCharta,
    build_maxwell_charta,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class InduktionsTyp(Enum):
    SCHUTZ_INDUKTION = "schutz-induktion"
    ORDNUNGS_INDUKTION = "ordnungs-induktion"
    SOUVERAENITAETS_INDUKTION = "souveraenitaets-induktion"


class InduktionsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class InduktionsGeltung(Enum):
    GESPERRT = "gesperrt"
    INDUZIERT = "induziert"
    GRUNDLEGEND_INDUZIERT = "grundlegend-induziert"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[MaxwellGeltung, InduktionsGeltung] = {
    MaxwellGeltung.GESPERRT: InduktionsGeltung.GESPERRT,
    MaxwellGeltung.MAXWELLISCH: InduktionsGeltung.INDUZIERT,
    MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH: InduktionsGeltung.GRUNDLEGEND_INDUZIERT,
}

_TYP_MAP: dict[MaxwellGeltung, InduktionsTyp] = {
    MaxwellGeltung.GESPERRT: InduktionsTyp.SCHUTZ_INDUKTION,
    MaxwellGeltung.MAXWELLISCH: InduktionsTyp.ORDNUNGS_INDUKTION,
    MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH: InduktionsTyp.SOUVERAENITAETS_INDUKTION,
}

_PROZEDUR_MAP: dict[MaxwellGeltung, InduktionsProzedur] = {
    MaxwellGeltung.GESPERRT: InduktionsProzedur.NOTPROZEDUR,
    MaxwellGeltung.MAXWELLISCH: InduktionsProzedur.REGELPROTOKOLL,
    MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH: InduktionsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[MaxwellGeltung, float] = {
    MaxwellGeltung.GESPERRT: 0.0,
    MaxwellGeltung.MAXWELLISCH: 0.04,
    MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH: 0.08,
}

_TIER_BONUS: dict[MaxwellGeltung, int] = {
    MaxwellGeltung.GESPERRT: 0,
    MaxwellGeltung.MAXWELLISCH: 1,
    MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InduktionsNorm:
    induktions_kodex_id: str
    induktions_typ: InduktionsTyp
    prozedur: InduktionsProzedur
    geltung: InduktionsGeltung
    induktions_weight: float
    induktions_tier: int
    canonical: bool
    induktions_ids: tuple[str, ...]
    induktions_tags: tuple[str, ...]


@dataclass(frozen=True)
class InduktionsKodex:
    kodex_id: str
    maxwell_charta: MaxwellCharta
    normen: tuple[InduktionsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.induktions_kodex_id for n in self.normen if n.geltung is InduktionsGeltung.GESPERRT)

    @property
    def induziert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.induktions_kodex_id for n in self.normen if n.geltung is InduktionsGeltung.INDUZIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.induktions_kodex_id for n in self.normen if n.geltung is InduktionsGeltung.GRUNDLEGEND_INDUZIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is InduktionsGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is InduktionsGeltung.INDUZIERT for n in self.normen):
            status = "kodex-induziert"
            severity = "warning"
        else:
            status = "kodex-grundlegend-induziert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_induktions_kodex(
    maxwell_charta: MaxwellCharta | None = None,
    *,
    kodex_id: str = "induktions-kodex",
) -> InduktionsKodex:
    if maxwell_charta is None:
        maxwell_charta = build_maxwell_charta(charta_id=f"{kodex_id}-charta")

    normen: list[InduktionsNorm] = []
    for parent_norm in maxwell_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.maxwell_charta_id.removeprefix(f'{maxwell_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.maxwell_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.maxwell_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InduktionsGeltung.GRUNDLEGEND_INDUZIERT)
        normen.append(
            InduktionsNorm(
                induktions_kodex_id=new_id,
                induktions_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                induktions_weight=raw_weight,
                induktions_tier=new_tier,
                canonical=is_canonical,
                induktions_ids=parent_norm.maxwell_ids + (new_id,),
                induktions_tags=parent_norm.maxwell_tags + (f"induktions-kodex:{new_geltung.value}",),
            )
        )

    return InduktionsKodex(
        kodex_id=kodex_id,
        maxwell_charta=maxwell_charta,
        normen=tuple(normen),
    )
