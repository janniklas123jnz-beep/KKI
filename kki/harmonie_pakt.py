"""harmonie_pakt — Metaphysik & Kosmologie layer 6 (#256)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmos_ordnung import (
    KosmosOrdnung,
    KosmosOrdnungsGeltung,
    KosmosOrdnungsNorm,
    KosmosOrdnungsProzedur,
    KosmosOrdnungsTyp,
    build_kosmos_ordnung,
)

__all__ = [
    "HarmonieTyp",
    "HarmonieProzedur",
    "HarmonieGeltung",
    "HarmonieNorm",
    "HarmoniePakt",
    "build_harmonie_pakt",
]


class HarmonieTyp(str, Enum):
    SCHUTZ_HARMONIE = "schutz-harmonie"
    ORDNUNGS_HARMONIE = "ordnungs-harmonie"
    SOUVERAENITAETS_HARMONIE = "souveraenitaets-harmonie"


class HarmonieProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HarmonieGeltung(str, Enum):
    GESPERRT = "gesperrt"
    HARMONISIERT = "harmonisiert"
    GRUNDLEGEND_HARMONISIERT = "grundlegend-harmonisiert"


_TYP_MAP: dict[KosmosOrdnungsGeltung, HarmonieTyp] = {
    KosmosOrdnungsGeltung.GESPERRT: HarmonieTyp.SCHUTZ_HARMONIE,
    KosmosOrdnungsGeltung.GEORDNET: HarmonieTyp.ORDNUNGS_HARMONIE,
    KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET: HarmonieTyp.SOUVERAENITAETS_HARMONIE,
}
_PROZEDUR_MAP: dict[KosmosOrdnungsGeltung, HarmonieProzedur] = {
    KosmosOrdnungsGeltung.GESPERRT: HarmonieProzedur.NOTPROZEDUR,
    KosmosOrdnungsGeltung.GEORDNET: HarmonieProzedur.REGELPROTOKOLL,
    KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET: HarmonieProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KosmosOrdnungsGeltung, HarmonieGeltung] = {
    KosmosOrdnungsGeltung.GESPERRT: HarmonieGeltung.GESPERRT,
    KosmosOrdnungsGeltung.GEORDNET: HarmonieGeltung.HARMONISIERT,
    KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET: HarmonieGeltung.GRUNDLEGEND_HARMONISIERT,
}
_WEIGHT_BONUS: dict[KosmosOrdnungsGeltung, float] = {
    KosmosOrdnungsGeltung.GESPERRT: 0.0,
    KosmosOrdnungsGeltung.GEORDNET: 0.04,
    KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET: 0.08,
}
_TIER_BONUS: dict[KosmosOrdnungsGeltung, int] = {
    KosmosOrdnungsGeltung.GESPERRT: 0,
    KosmosOrdnungsGeltung.GEORDNET: 1,
    KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET: 2,
}


@dataclass(frozen=True)
class HarmonieNorm:
    harmonie_pakt_id: str
    harmonie_typ: HarmonieTyp
    prozedur: HarmonieProzedur
    geltung: HarmonieGeltung
    harmonie_weight: float
    harmonie_tier: int
    canonical: bool
    harmonie_pakt_ids: tuple[str, ...]
    harmonie_pakt_tags: tuple[str, ...]


@dataclass(frozen=True)
class HarmoniePakt:
    pakt_id: str
    kosmos_ordnung: KosmosOrdnung
    normen: tuple[HarmonieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.harmonie_pakt_id for n in self.normen if n.geltung is HarmonieGeltung.GESPERRT)

    @property
    def harmonisiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.harmonie_pakt_id for n in self.normen if n.geltung is HarmonieGeltung.HARMONISIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.harmonie_pakt_id for n in self.normen if n.geltung is HarmonieGeltung.GRUNDLEGEND_HARMONISIERT)

    @property
    def pakt_signal(self):
        if any(n.geltung is HarmonieGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is HarmonieGeltung.HARMONISIERT for n in self.normen):
            status = "pakt-harmonisiert"
            severity = "warning"
        else:
            status = "pakt-grundlegend-harmonisiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_harmonie_pakt(
    kosmos_ordnung: KosmosOrdnung | None = None,
    *,
    pakt_id: str = "harmonie-pakt",
) -> HarmoniePakt:
    if kosmos_ordnung is None:
        kosmos_ordnung = build_kosmos_ordnung(ordnung_id=f"{pakt_id}-ordnung")

    normen: list[HarmonieNorm] = []
    for parent_norm in kosmos_ordnung.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.kosmos_ordnung_id.removeprefix(f'{kosmos_ordnung.ordnung_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kosmos_ordnungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kosmos_ordnungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HarmonieGeltung.GRUNDLEGEND_HARMONISIERT)
        normen.append(
            HarmonieNorm(
                harmonie_pakt_id=new_id,
                harmonie_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                harmonie_weight=raw_weight,
                harmonie_tier=new_tier,
                canonical=is_canonical,
                harmonie_pakt_ids=parent_norm.kosmos_ordnung_ids + (new_id,),
                harmonie_pakt_tags=parent_norm.kosmos_ordnung_tags + (f"harmonie-pakt:{new_geltung.value}",),
            )
        )

    return HarmoniePakt(
        pakt_id=pakt_id,
        kosmos_ordnung=kosmos_ordnung,
        normen=tuple(normen),
    )
