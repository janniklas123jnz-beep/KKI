"""ursprungs_axiom — Metaphysik & Kosmologie layer 1 (#251)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .transzendenz_kodex import (
    TranszendenzEbene,
    TranszendenzGeltung,
    TranszendenzKodex,
    TranszendenzNorm,
    TranszendenzProzedur,
    build_transzendenz_kodex,
)

__all__ = [
    "AxiomRang",
    "AxiomProzedur",
    "AxiomGeltung",
    "UrsprungsAxiomEintrag",
    "UrsprungsAxiom",
    "build_ursprungs_axiom",
]


class AxiomRang(str, Enum):
    SCHUTZ_AXIOM = "schutz-axiom"
    ORDNUNGS_AXIOM = "ordnungs-axiom"
    SOUVERAENITAETS_AXIOM = "souveraenitaets-axiom"


class AxiomProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AxiomGeltung(str, Enum):
    GESPERRT = "gesperrt"
    AXIOMATISCH = "axiomatisch"
    GRUNDLEGEND_AXIOMATISCH = "grundlegend-axiomatisch"


_RANG_MAP: dict[TranszendenzGeltung, AxiomRang] = {
    TranszendenzGeltung.GESPERRT: AxiomRang.SCHUTZ_AXIOM,
    TranszendenzGeltung.TRANSZENDIERT: AxiomRang.ORDNUNGS_AXIOM,
    TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT: AxiomRang.SOUVERAENITAETS_AXIOM,
}
_PROZEDUR_MAP: dict[TranszendenzGeltung, AxiomProzedur] = {
    TranszendenzGeltung.GESPERRT: AxiomProzedur.NOTPROZEDUR,
    TranszendenzGeltung.TRANSZENDIERT: AxiomProzedur.REGELPROTOKOLL,
    TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT: AxiomProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[TranszendenzGeltung, AxiomGeltung] = {
    TranszendenzGeltung.GESPERRT: AxiomGeltung.GESPERRT,
    TranszendenzGeltung.TRANSZENDIERT: AxiomGeltung.AXIOMATISCH,
    TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT: AxiomGeltung.GRUNDLEGEND_AXIOMATISCH,
}
_WEIGHT_BONUS: dict[TranszendenzGeltung, float] = {
    TranszendenzGeltung.GESPERRT: 0.0,
    TranszendenzGeltung.TRANSZENDIERT: 0.04,
    TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT: 0.08,
}
_TIER_BONUS: dict[TranszendenzGeltung, int] = {
    TranszendenzGeltung.GESPERRT: 0,
    TranszendenzGeltung.TRANSZENDIERT: 1,
    TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT: 2,
}


@dataclass(frozen=True)
class UrsprungsAxiomEintrag:
    ursprungs_axiom_id: str
    axiom_rang: AxiomRang
    prozedur: AxiomProzedur
    geltung: AxiomGeltung
    axiom_weight: float
    axiom_tier: int
    canonical: bool
    ursprungs_axiom_ids: tuple[str, ...]
    ursprungs_axiom_tags: tuple[str, ...]


@dataclass(frozen=True)
class UrsprungsAxiom:
    axiom_id: str
    transzendenz_kodex: TranszendenzKodex
    normen: tuple[UrsprungsAxiomEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ursprungs_axiom_id for n in self.normen if n.geltung is AxiomGeltung.GESPERRT)

    @property
    def axiomatisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ursprungs_axiom_id for n in self.normen if n.geltung is AxiomGeltung.AXIOMATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ursprungs_axiom_id for n in self.normen if n.geltung is AxiomGeltung.GRUNDLEGEND_AXIOMATISCH)

    @property
    def axiom_signal(self):
        if any(n.geltung is AxiomGeltung.GESPERRT for n in self.normen):
            status = "axiom-gesperrt"
            severity = "critical"
        elif any(n.geltung is AxiomGeltung.AXIOMATISCH for n in self.normen):
            status = "axiom-axiomatisch"
            severity = "warning"
        else:
            status = "axiom-grundlegend-axiomatisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_ursprungs_axiom(
    transzendenz_kodex: TranszendenzKodex | None = None,
    *,
    axiom_id: str = "ursprungs-axiom",
) -> UrsprungsAxiom:
    if transzendenz_kodex is None:
        transzendenz_kodex = build_transzendenz_kodex(kodex_id=f"{axiom_id}-kodex")

    normen: list[UrsprungsAxiomEintrag] = []
    for parent_norm in transzendenz_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{axiom_id}-{parent_norm.transzendenz_kodex_id.removeprefix(f'{transzendenz_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.transzendenz_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.transzendenz_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AxiomGeltung.GRUNDLEGEND_AXIOMATISCH)
        normen.append(
            UrsprungsAxiomEintrag(
                ursprungs_axiom_id=new_id,
                axiom_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                axiom_weight=raw_weight,
                axiom_tier=new_tier,
                canonical=is_canonical,
                ursprungs_axiom_ids=parent_norm.transzendenz_kodex_ids + (new_id,),
                ursprungs_axiom_tags=parent_norm.transzendenz_kodex_tags + (f"ursprungs-axiom:{new_geltung.value}",),
            )
        )

    return UrsprungsAxiom(
        axiom_id=axiom_id,
        transzendenz_kodex=transzendenz_kodex,
        normen=tuple(normen),
    )
