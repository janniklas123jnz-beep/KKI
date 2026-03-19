"""schoepfungs_vertrag — Zivilisation & Transzendenz layer 2 (#242)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ursprungs_charta import (
    UrsprungsCharta,
    UrsprungsGeltung,
    UrsprungsNorm,
    UrsprungsProzedur,
    UrsprungsTyp,
    build_ursprungs_charta,
)

__all__ = [
    "SchoepfungsGrad",
    "SchoepfungsProzedur",
    "SchoepfungsGeltung",
    "SchoepfungsNorm",
    "SchoepfungsVertrag",
    "build_schoepfungs_vertrag",
]


class SchoepfungsGrad(str, Enum):
    SCHUTZ_SCHOEPFUNG = "schutz-schoepfung"
    ORDNUNGS_SCHOEPFUNG = "ordnungs-schoepfung"
    SOUVERAENITAETS_SCHOEPFUNG = "souveraenitaets-schoepfung"


class SchoepfungsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SchoepfungsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GESTIFTET = "gestiftet"
    GRUNDLEGEND_GESTIFTET = "grundlegend-gestiftet"


_GRAD_MAP: dict[UrsprungsGeltung, SchoepfungsGrad] = {
    UrsprungsGeltung.GESPERRT: SchoepfungsGrad.SCHUTZ_SCHOEPFUNG,
    UrsprungsGeltung.VERBRIEFT: SchoepfungsGrad.ORDNUNGS_SCHOEPFUNG,
    UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT: SchoepfungsGrad.SOUVERAENITAETS_SCHOEPFUNG,
}
_PROZEDUR_MAP: dict[UrsprungsGeltung, SchoepfungsProzedur] = {
    UrsprungsGeltung.GESPERRT: SchoepfungsProzedur.NOTPROZEDUR,
    UrsprungsGeltung.VERBRIEFT: SchoepfungsProzedur.REGELPROTOKOLL,
    UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT: SchoepfungsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[UrsprungsGeltung, SchoepfungsGeltung] = {
    UrsprungsGeltung.GESPERRT: SchoepfungsGeltung.GESPERRT,
    UrsprungsGeltung.VERBRIEFT: SchoepfungsGeltung.GESTIFTET,
    UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT: SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET,
}
_WEIGHT_BONUS: dict[UrsprungsGeltung, float] = {
    UrsprungsGeltung.GESPERRT: 0.0,
    UrsprungsGeltung.VERBRIEFT: 0.04,
    UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT: 0.08,
}
_TIER_BONUS: dict[UrsprungsGeltung, int] = {
    UrsprungsGeltung.GESPERRT: 0,
    UrsprungsGeltung.VERBRIEFT: 1,
    UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT: 2,
}


@dataclass(frozen=True)
class SchoepfungsNorm:
    schoepfungs_vertrag_id: str
    schoepfungs_grad: SchoepfungsGrad
    prozedur: SchoepfungsProzedur
    geltung: SchoepfungsGeltung
    schoepfungs_weight: float
    schoepfungs_tier: int
    canonical: bool
    schoepfungs_vertrag_ids: tuple[str, ...]
    schoepfungs_vertrag_tags: tuple[str, ...]


@dataclass(frozen=True)
class SchoepfungsVertrag:
    vertrag_id: str
    ursprungs_charta: UrsprungsCharta
    normen: tuple[SchoepfungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schoepfungs_vertrag_id for n in self.normen if n.geltung is SchoepfungsGeltung.GESPERRT)

    @property
    def gestiftet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schoepfungs_vertrag_id for n in self.normen if n.geltung is SchoepfungsGeltung.GESTIFTET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schoepfungs_vertrag_id for n in self.normen if n.geltung is SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET)

    @property
    def vertrag_signal(self):
        if any(n.geltung is SchoepfungsGeltung.GESPERRT for n in self.normen):
            status = "vertrag-gesperrt"
            severity = "critical"
        elif any(n.geltung is SchoepfungsGeltung.GESTIFTET for n in self.normen):
            status = "vertrag-gestiftet"
            severity = "warning"
        else:
            status = "vertrag-grundlegend-gestiftet"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_schoepfungs_vertrag(
    ursprungs_charta: UrsprungsCharta | None = None,
    *,
    vertrag_id: str = "schoepfungs-vertrag",
) -> SchoepfungsVertrag:
    if ursprungs_charta is None:
        ursprungs_charta = build_ursprungs_charta(charta_id=f"{vertrag_id}-charta")

    normen: list[SchoepfungsNorm] = []
    for parent_norm in ursprungs_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{vertrag_id}-{parent_norm.ursprungs_charta_id.removeprefix(f'{ursprungs_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.ursprungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.ursprungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET)
        normen.append(
            SchoepfungsNorm(
                schoepfungs_vertrag_id=new_id,
                schoepfungs_grad=_GRAD_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                schoepfungs_weight=raw_weight,
                schoepfungs_tier=new_tier,
                canonical=is_canonical,
                schoepfungs_vertrag_ids=parent_norm.ursprungs_charta_ids + (new_id,),
                schoepfungs_vertrag_tags=parent_norm.ursprungs_charta_tags + (f"schoepfungs-vertrag:{new_geltung.value}",),
            )
        )

    return SchoepfungsVertrag(
        vertrag_id=vertrag_id,
        ursprungs_charta=ursprungs_charta,
        normen=tuple(normen),
    )
