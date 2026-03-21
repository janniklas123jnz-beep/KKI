"""
#321 KosmologieFeld — Das kosmologische Feld als Governance-Wurzel des Universums.
Geltungsstufen: GESPERRT / KOSMOLOGISCH / GRUNDLEGEND_KOSMOLOGISCH
Parent: TeilchenphysikVerfassung (#320)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .teilchenphysik_verfassung import (
    TeilchenphysikGeltung,
    TeilchenphysikVerfassung,
    build_teilchenphysik_verfassung,
)

_GELTUNG_MAP: dict[TeilchenphysikGeltung, "KosmologieGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[TeilchenphysikGeltung.GESPERRT] = KosmologieGeltung.GESPERRT
    _GELTUNG_MAP[TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST] = KosmologieGeltung.KOSMOLOGISCH
    _GELTUNG_MAP[TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST] = KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH


class KosmologieTyp(Enum):
    SCHUTZ_KOSMOLOGIE = "schutz-kosmologie"
    ORDNUNGS_KOSMOLOGIE = "ordnungs-kosmologie"
    SOUVERAENITAETS_KOSMOLOGIE = "souveraenitaets-kosmologie"


class KosmologieProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KosmologieGeltung(Enum):
    GESPERRT = "gesperrt"
    KOSMOLOGISCH = "kosmologisch"
    GRUNDLEGEND_KOSMOLOGISCH = "grundlegend-kosmologisch"


_init_map()

_TYP_MAP: dict[KosmologieGeltung, KosmologieTyp] = {
    KosmologieGeltung.GESPERRT: KosmologieTyp.SCHUTZ_KOSMOLOGIE,
    KosmologieGeltung.KOSMOLOGISCH: KosmologieTyp.ORDNUNGS_KOSMOLOGIE,
    KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH: KosmologieTyp.SOUVERAENITAETS_KOSMOLOGIE,
}

_PROZEDUR_MAP: dict[KosmologieGeltung, KosmologieProzedur] = {
    KosmologieGeltung.GESPERRT: KosmologieProzedur.NOTPROZEDUR,
    KosmologieGeltung.KOSMOLOGISCH: KosmologieProzedur.REGELPROTOKOLL,
    KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH: KosmologieProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KosmologieGeltung, float] = {
    KosmologieGeltung.GESPERRT: 0.0,
    KosmologieGeltung.KOSMOLOGISCH: 0.04,
    KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH: 0.08,
}

_TIER_DELTA: dict[KosmologieGeltung, int] = {
    KosmologieGeltung.GESPERRT: 0,
    KosmologieGeltung.KOSMOLOGISCH: 1,
    KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KosmologieNorm:
    kosmologie_feld_id: str
    kosmologie_typ: KosmologieTyp
    prozedur: KosmologieProzedur
    geltung: KosmologieGeltung
    kosmologie_weight: float
    kosmologie_tier: int
    canonical: bool
    kosmologie_ids: tuple[str, ...]
    kosmologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class KosmologieFeld:
    feld_id: str
    teilchenphysik_verfassung: TeilchenphysikVerfassung
    normen: tuple[KosmologieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmologie_feld_id for n in self.normen if n.geltung is KosmologieGeltung.GESPERRT)

    @property
    def kosmologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmologie_feld_id for n in self.normen if n.geltung is KosmologieGeltung.KOSMOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmologie_feld_id for n in self.normen if n.geltung is KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is KosmologieGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is KosmologieGeltung.KOSMOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-kosmologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-kosmologisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kosmologie_feld(
    teilchenphysik_verfassung: TeilchenphysikVerfassung | None = None,
    *,
    feld_id: str = "kosmologie-feld",
) -> KosmologieFeld:
    if teilchenphysik_verfassung is None:
        teilchenphysik_verfassung = build_teilchenphysik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[KosmologieNorm] = []
    for parent_norm in teilchenphysik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.teilchenphysik_verfassung_id.removeprefix(f'{teilchenphysik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.teilchenphysik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.teilchenphysik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KosmologieGeltung.GRUNDLEGEND_KOSMOLOGISCH)
        normen.append(
            KosmologieNorm(
                kosmologie_feld_id=new_id,
                kosmologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kosmologie_weight=new_weight,
                kosmologie_tier=new_tier,
                canonical=is_canonical,
                kosmologie_ids=parent_norm.teilchenphysik_ids + (new_id,),
                kosmologie_tags=parent_norm.teilchenphysik_tags + (f"kosmologie-feld:{new_geltung.value}",),
            )
        )
    return KosmologieFeld(
        feld_id=feld_id,
        teilchenphysik_verfassung=teilchenphysik_verfassung,
        normen=tuple(normen),
    )
