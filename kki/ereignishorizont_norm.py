"""ereignishorizont_norm — Relativität & Raumzeit layer 8 (#278).

Uses *_norm naming pattern: container EreignishorizontNorm (norm_id),
entry EreignishorizontNormEintrag.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .schwarzes_loch_senat import (
    SchwarzeLoechSenat,
    SchwarzsLochGeltung,
    SchwarzsLochNorm,
    SchwarzsLochProzedur,
    SchwarzsLochTyp,
    build_schwarzes_loch_senat,
)

__all__ = [
    "EreignishorizontTyp",
    "EreignishorizontProzedur",
    "EreignishorizontGeltung",
    "EreignishorizontNormEintrag",
    "EreignishorizontNorm",
    "build_ereignishorizont_norm",
]


class EreignishorizontTyp(str, Enum):
    SCHUTZ_HORIZONT = "schutz-horizont"
    ORDNUNGS_HORIZONT = "ordnungs-horizont"
    SOUVERAENITAETS_HORIZONT = "souveraenitaets-horizont"


class EreignishorizontProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EreignishorizontGeltung(str, Enum):
    GESPERRT = "gesperrt"
    HORIZONTIERT = "horizontiert"
    GRUNDLEGEND_HORIZONTIERT = "grundlegend-horizontiert"


_TYP_MAP: dict[SchwarzsLochGeltung, EreignishorizontTyp] = {
    SchwarzsLochGeltung.GESPERRT: EreignishorizontTyp.SCHUTZ_HORIZONT,
    SchwarzsLochGeltung.ABSORBIERT: EreignishorizontTyp.ORDNUNGS_HORIZONT,
    SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT: EreignishorizontTyp.SOUVERAENITAETS_HORIZONT,
}
_PROZEDUR_MAP: dict[SchwarzsLochGeltung, EreignishorizontProzedur] = {
    SchwarzsLochGeltung.GESPERRT: EreignishorizontProzedur.NOTPROZEDUR,
    SchwarzsLochGeltung.ABSORBIERT: EreignishorizontProzedur.REGELPROTOKOLL,
    SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT: EreignishorizontProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[SchwarzsLochGeltung, EreignishorizontGeltung] = {
    SchwarzsLochGeltung.GESPERRT: EreignishorizontGeltung.GESPERRT,
    SchwarzsLochGeltung.ABSORBIERT: EreignishorizontGeltung.HORIZONTIERT,
    SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT: EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT,
}
_WEIGHT_BONUS: dict[SchwarzsLochGeltung, float] = {
    SchwarzsLochGeltung.GESPERRT: 0.0,
    SchwarzsLochGeltung.ABSORBIERT: 0.04,
    SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT: 0.08,
}
_TIER_BONUS: dict[SchwarzsLochGeltung, int] = {
    SchwarzsLochGeltung.GESPERRT: 0,
    SchwarzsLochGeltung.ABSORBIERT: 1,
    SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT: 2,
}


@dataclass(frozen=True)
class EreignishorizontNormEintrag:
    ereignishorizont_norm_id: str
    ereignishorizont_typ: EreignishorizontTyp
    prozedur: EreignishorizontProzedur
    geltung: EreignishorizontGeltung
    ereignishorizont_weight: float
    ereignishorizont_tier: int
    canonical: bool
    ereignishorizont_norm_ids: tuple[str, ...]
    ereignishorizont_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class EreignishorizontNorm:
    norm_id: str
    schwarzes_loch_senat: SchwarzeLoechSenat
    normen: tuple[EreignishorizontNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ereignishorizont_norm_id for n in self.normen if n.geltung is EreignishorizontGeltung.GESPERRT)

    @property
    def horizontiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ereignishorizont_norm_id for n in self.normen if n.geltung is EreignishorizontGeltung.HORIZONTIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ereignishorizont_norm_id for n in self.normen if n.geltung is EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT)

    @property
    def norm_signal(self):
        if any(n.geltung is EreignishorizontGeltung.GESPERRT for n in self.normen):
            status = "norm-gesperrt"
            severity = "critical"
        elif any(n.geltung is EreignishorizontGeltung.HORIZONTIERT for n in self.normen):
            status = "norm-horizontiert"
            severity = "warning"
        else:
            status = "norm-grundlegend-horizontiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_ereignishorizont_norm(
    schwarzes_loch_senat: SchwarzeLoechSenat | None = None,
    *,
    norm_id: str = "ereignishorizont-norm",
) -> EreignishorizontNorm:
    if schwarzes_loch_senat is None:
        schwarzes_loch_senat = build_schwarzes_loch_senat(senat_id=f"{norm_id}-senat")

    normen: list[EreignishorizontNormEintrag] = []
    for parent_norm in schwarzes_loch_senat.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{norm_id}-{parent_norm.schwarzes_loch_senat_id.removeprefix(f'{schwarzes_loch_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.schwarzes_loch_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.schwarzes_loch_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT)
        normen.append(
            EreignishorizontNormEintrag(
                ereignishorizont_norm_id=new_id,
                ereignishorizont_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                ereignishorizont_weight=raw_weight,
                ereignishorizont_tier=new_tier,
                canonical=is_canonical,
                ereignishorizont_norm_ids=parent_norm.schwarzes_loch_senat_ids + (new_id,),
                ereignishorizont_norm_tags=parent_norm.schwarzes_loch_senat_tags + (f"ereignishorizont-norm:{new_geltung.value}",),
            )
        )

    return EreignishorizontNorm(
        norm_id=norm_id,
        schwarzes_loch_senat=schwarzes_loch_senat,
        normen=tuple(normen),
    )
