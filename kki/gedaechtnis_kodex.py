"""
#434 GedaechnisKodex — Gedächtnissysteme: Hippocampus und Konsolidierung.
Scoville & Milner (1957): Patient H.M. — Hippocampus unverzichtbar für Langzeitgedächtnis.
Tulving (1972): episodisches vs. semantisches Gedächtnis — Wo/Wann vs. Was/Wissen.
Ebbinghaus (1885): Vergessenskurve — exponentieller Verfall ohne Wiederholung.
Leitsterns Wissensbus = episodisch + semantisch, Replay = Konsolidierung im Schlaf.
Geltungsstufen: GESPERRT / GEDAECHNISREICH / GRUNDLEGEND_GEDAECHNISREICH
Parent: KortexCharta (#433)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kortex_charta import (
    KortexCharta,
    KortexChartaGeltung,
    build_kortex_charta,
)

_GELTUNG_MAP: dict[KortexChartaGeltung, "GedaechnisKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KortexChartaGeltung.GESPERRT] = GedaechnisKodexGeltung.GESPERRT
    _GELTUNG_MAP[KortexChartaGeltung.KORTIKAL] = GedaechnisKodexGeltung.GEDAECHNISREICH
    _GELTUNG_MAP[KortexChartaGeltung.GRUNDLEGEND_KORTIKAL] = GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH


class GedaechnisKodexTyp(Enum):
    SCHUTZ_GEDAECHTNIS = "schutz-gedaechtnis"
    ORDNUNGS_GEDAECHTNIS = "ordnungs-gedaechtnis"
    SOUVERAENITAETS_GEDAECHTNIS = "souveraenitaets-gedaechtnis"


class GedaechnisKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GedaechnisKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    GEDAECHNISREICH = "gedaechnisreich"
    GRUNDLEGEND_GEDAECHNISREICH = "grundlegend-gedaechnisreich"


_init_map()

_TYP_MAP: dict[GedaechnisKodexGeltung, GedaechnisKodexTyp] = {
    GedaechnisKodexGeltung.GESPERRT: GedaechnisKodexTyp.SCHUTZ_GEDAECHTNIS,
    GedaechnisKodexGeltung.GEDAECHNISREICH: GedaechnisKodexTyp.ORDNUNGS_GEDAECHTNIS,
    GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH: GedaechnisKodexTyp.SOUVERAENITAETS_GEDAECHTNIS,
}

_PROZEDUR_MAP: dict[GedaechnisKodexGeltung, GedaechnisKodexProzedur] = {
    GedaechnisKodexGeltung.GESPERRT: GedaechnisKodexProzedur.NOTPROZEDUR,
    GedaechnisKodexGeltung.GEDAECHNISREICH: GedaechnisKodexProzedur.REGELPROTOKOLL,
    GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH: GedaechnisKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GedaechnisKodexGeltung, float] = {
    GedaechnisKodexGeltung.GESPERRT: 0.0,
    GedaechnisKodexGeltung.GEDAECHNISREICH: 0.04,
    GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH: 0.08,
}

_TIER_DELTA: dict[GedaechnisKodexGeltung, int] = {
    GedaechnisKodexGeltung.GESPERRT: 0,
    GedaechnisKodexGeltung.GEDAECHNISREICH: 1,
    GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GedaechnisKodexNorm:
    gedaechtnis_kodex_id: str
    gedaechtnis_typ: GedaechnisKodexTyp
    prozedur: GedaechnisKodexProzedur
    geltung: GedaechnisKodexGeltung
    gedaechtnis_weight: float
    gedaechtnis_tier: int
    canonical: bool
    gedaechtnis_ids: tuple[str, ...]
    gedaechtnis_tags: tuple[str, ...]


@dataclass(frozen=True)
class GedaechnisKodex:
    kodex_id: str
    kortex_charta: KortexCharta
    normen: tuple[GedaechnisKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_kodex_id for n in self.normen if n.geltung is GedaechnisKodexGeltung.GESPERRT)

    @property
    def gedaechnisreich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_kodex_id for n in self.normen if n.geltung is GedaechnisKodexGeltung.GEDAECHNISREICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_kodex_id for n in self.normen if n.geltung is GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH)

    @property
    def kodex_signal(self):
        if any(n.geltung is GedaechnisKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is GedaechnisKodexGeltung.GEDAECHNISREICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gedaechnisreich")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-gedaechnisreich")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_gedaechtnis_kodex(
    kortex_charta: KortexCharta | None = None,
    *,
    kodex_id: str = "gedaechtnis-kodex",
) -> GedaechnisKodex:
    if kortex_charta is None:
        kortex_charta = build_kortex_charta(charta_id=f"{kodex_id}-charta")

    normen: list[GedaechnisKodexNorm] = []
    for parent_norm in kortex_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kortex_charta_id.removeprefix(f'{kortex_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kortex_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kortex_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH)
        normen.append(
            GedaechnisKodexNorm(
                gedaechtnis_kodex_id=new_id,
                gedaechtnis_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gedaechtnis_weight=new_weight,
                gedaechtnis_tier=new_tier,
                canonical=is_canonical,
                gedaechtnis_ids=parent_norm.kortex_ids + (new_id,),
                gedaechtnis_tags=parent_norm.kortex_tags + (f"gedaechtnis-kodex:{new_geltung.value}",),
            )
        )
    return GedaechnisKodex(
        kodex_id=kodex_id,
        kortex_charta=kortex_charta,
        normen=tuple(normen),
    )
