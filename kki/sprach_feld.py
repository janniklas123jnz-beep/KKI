"""
#461 SprachFeld — Saussure langue/parole und das arbiträre Zeichen.
Saussure (1916): Cours de linguistique générale — Sprache als System von Differenzen,
  Signifiant (Lautbild) und Signifié (Begriff) als zwei Seiten der Zeichenmedaille.
Sapir (1921): Language — Sprache als kulturelles Produkt und kognitives Werkzeug.
Whorf (1940): Linguistische Relativität — Sprache formt Denken und Wahrnehmung.
Leitsterns SprachFeld: Jeder Agent des Terra-Schwarms trägt ein internes Zeichensystem;
Bedeutung entsteht nicht isoliert, sondern durch Differenz im Kollektiv.
Geltungsstufen: GESPERRT / SPRACHLICH / GRUNDLEGEND_SPRACHLICH
Parent: EvolutionsbiologieVerfassung (#460)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .evolutionsbiologie_verfassung import (
    EvolutionsbiologieVerfassung,
    EvolutionsbiologieVerfassungsGeltung,
    build_evolutionsbiologie_verfassung,
)

_GELTUNG_MAP: dict[EvolutionsbiologieVerfassungsGeltung, "SprachFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EvolutionsbiologieVerfassungsGeltung.GESPERRT] = SprachFeldGeltung.GESPERRT
    _GELTUNG_MAP[EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH] = SprachFeldGeltung.SPRACHLICH
    _GELTUNG_MAP[EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH] = SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH


class SprachFeldTyp(Enum):
    SCHUTZ_SPRACHE = "schutz-sprache"
    ORDNUNGS_SPRACHE = "ordnungs-sprache"
    SOUVERAENITAETS_SPRACHE = "souveraenitaets-sprache"


class SprachFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SprachFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    SPRACHLICH = "sprachlich"
    GRUNDLEGEND_SPRACHLICH = "grundlegend-sprachlich"


_init_map()

_TYP_MAP: dict[SprachFeldGeltung, SprachFeldTyp] = {
    SprachFeldGeltung.GESPERRT: SprachFeldTyp.SCHUTZ_SPRACHE,
    SprachFeldGeltung.SPRACHLICH: SprachFeldTyp.ORDNUNGS_SPRACHE,
    SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH: SprachFeldTyp.SOUVERAENITAETS_SPRACHE,
}

_PROZEDUR_MAP: dict[SprachFeldGeltung, SprachFeldProzedur] = {
    SprachFeldGeltung.GESPERRT: SprachFeldProzedur.NOTPROZEDUR,
    SprachFeldGeltung.SPRACHLICH: SprachFeldProzedur.REGELPROTOKOLL,
    SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH: SprachFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SprachFeldGeltung, float] = {
    SprachFeldGeltung.GESPERRT: 0.0,
    SprachFeldGeltung.SPRACHLICH: 0.04,
    SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH: 0.08,
}

_TIER_DELTA: dict[SprachFeldGeltung, int] = {
    SprachFeldGeltung.GESPERRT: 0,
    SprachFeldGeltung.SPRACHLICH: 1,
    SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH: 2,
}


@dataclass(frozen=True)
class SprachFeldNorm:
    sprach_feld_id: str
    sprach_feld_typ: SprachFeldTyp
    prozedur: SprachFeldProzedur
    geltung: SprachFeldGeltung
    sprach_feld_weight: float
    sprach_feld_tier: int
    canonical: bool
    sprach_feld_ids: tuple[str, ...]
    sprach_feld_tags: tuple[str, ...]


@dataclass(frozen=True)
class SprachFeld:
    feld_id: str
    evolutionsbiologie_verfassung: EvolutionsbiologieVerfassung
    normen: tuple[SprachFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprach_feld_id for n in self.normen if n.geltung is SprachFeldGeltung.GESPERRT)

    @property
    def sprachlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprach_feld_id for n in self.normen if n.geltung is SprachFeldGeltung.SPRACHLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprach_feld_id for n in self.normen if n.geltung is SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH)

    @property
    def feld_signal(self):
        if any(n.geltung is SprachFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is SprachFeldGeltung.SPRACHLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-sprachlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-sprachlich")


def build_sprach_feld(
    evolutionsbiologie_verfassung: EvolutionsbiologieVerfassung | None = None,
    *,
    feld_id: str = "sprach-feld",
) -> SprachFeld:
    if evolutionsbiologie_verfassung is None:
        evolutionsbiologie_verfassung = build_evolutionsbiologie_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[SprachFeldNorm] = []
    for parent_norm in evolutionsbiologie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.evolutionsbiologie_verfassung_id.removeprefix(f'{evolutionsbiologie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.evolutionsbiologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.evolutionsbiologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH)
        normen.append(
            SprachFeldNorm(
                sprach_feld_id=new_id,
                sprach_feld_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                sprach_feld_weight=new_weight,
                sprach_feld_tier=new_tier,
                canonical=is_canonical,
                sprach_feld_ids=parent_norm.evolutionsbiologie_ids + (new_id,),
                sprach_feld_tags=parent_norm.evolutionsbiologie_tags + (f"sprach-feld:{new_geltung.value}",),
            )
        )
    return SprachFeld(
        feld_id=feld_id,
        evolutionsbiologie_verfassung=evolutionsbiologie_verfassung,
        normen=tuple(normen),
    )
