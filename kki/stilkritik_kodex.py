"""
#574 StilkritikKodex — Winckelmann/Vasari/Schopenhauer Kunstwissenschaft Stilkritik

Johann Joachim Winckelmann (1764): Geschichte der Kunst des Altertums — edle Einfalt
  und stille Größe als Ideal griechischer Schönheit; Periodisierung der antiken Kunst
  als Entwicklungsmodell; Nachahmung als Weg zur Vollkommenheit; Begründung der
  Klassischen Archäologie als Wissenschaft im Peta-Schwarm Leitstern.
Giorgio Vasari (1550): Le Vite de' più eccellenti pittori — Biographie als
  kunsthistorische Methode; Entwicklungsmodell der Kunst als Organismus mit Geburt,
  Wachstum und Vollendung; Maniera als Stilbegriff; Begründung der Kunstgeschichte
  als narrativer Disziplin im Peta-Schwarm Leitstern.
Arthur Schopenhauer (1818): Die Welt als Wille und Vorstellung — Kunst als
  willensfreie Kontemplation; ästhetische Erfahrung als temporäre Erlösung vom
  Willensdrang; Musik als unmittelbarster Ausdruck des Willens; Genie als Fähigkeit
  zur reinen Anschauung im Peta-Schwarm Leitstern. 🏛️✍️
Parent: KunsttheorieCharta (#573)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kunsttheorie_charta import (
    KunsttheorieCharta,
    KunsttheorieChartaGeltung,
    build_kunsttheorie_charta,
)

_WEIGHT_DELTA: dict["StilkritikKodexGeltung", float] = {}
_TIER_DELTA: dict["StilkritikKodexGeltung", int] = {}
_TYP_MAP: dict["StilkritikKodexGeltung", "StilkritikKodexTyp"] = {}
_PROZEDUR_MAP: dict["StilkritikKodexGeltung", "StilkritikKodexProzedur"] = {}
_GELTUNG_MAP: dict[KunsttheorieChartaGeltung, "StilkritikKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        StilkritikKodexGeltung.GESPERRT: 0.0,
        StilkritikKodexGeltung.STILKRITISCH: 0.05,
        StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH: 0.1,
    })
    _TIER_DELTA.update({
        StilkritikKodexGeltung.GESPERRT: 0,
        StilkritikKodexGeltung.STILKRITISCH: 1,
        StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH: 2,
    })
    _TYP_MAP.update({
        StilkritikKodexGeltung.GESPERRT: StilkritikKodexTyp.SCHUTZ_STILKRITIK,
        StilkritikKodexGeltung.STILKRITISCH: StilkritikKodexTyp.ORDNUNGS_STILKRITIK,
        StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH: StilkritikKodexTyp.SOUVERAENITAETS_STILKRITIK,
    })
    _PROZEDUR_MAP.update({
        StilkritikKodexGeltung.GESPERRT: StilkritikKodexProzedur.NOTPROZEDUR,
        StilkritikKodexGeltung.STILKRITISCH: StilkritikKodexProzedur.REGELPROTOKOLL,
        StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH: StilkritikKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KunsttheorieChartaGeltung.GESPERRT: StilkritikKodexGeltung.GESPERRT,
        KunsttheorieChartaGeltung.KUNSTTHEORETISCH: StilkritikKodexGeltung.STILKRITISCH,
        KunsttheorieChartaGeltung.GRUNDLEGEND_KUNSTTHEORETISCH: StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH,
    })


class StilkritikKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    STILKRITISCH = "stilkritisch"
    GRUNDLEGEND_STILKRITISCH = "grundlegend-stilkritisch"


class StilkritikKodexTyp(Enum):
    SCHUTZ_STILKRITIK = "schutz-stilkritik"
    ORDNUNGS_STILKRITIK = "ordnungs-stilkritik"
    SOUVERAENITAETS_STILKRITIK = "souveraenitaets-stilkritik"


class StilkritikKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class StilkritikKodexNorm:
    stilkritik_kodex_id: str
    kunst_typ: StilkritikKodexTyp
    prozedur: StilkritikKodexProzedur
    geltung: StilkritikKodexGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class StilkritikKodex:
    kodex_id: str
    kunsttheorie_charta: KunsttheorieCharta
    normen: tuple[StilkritikKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stilkritik_kodex_id for n in self.normen if n.geltung is StilkritikKodexGeltung.GESPERRT)

    @property
    def stilkritisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stilkritik_kodex_id for n in self.normen if n.geltung is StilkritikKodexGeltung.STILKRITISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stilkritik_kodex_id for n in self.normen if n.geltung is StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is StilkritikKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is StilkritikKodexGeltung.STILKRITISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-stilkritisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-stilkritisch")


_init_map()


def build_stilkritik_kodex(
    kunsttheorie_charta: KunsttheorieCharta | None = None,
    *,
    kodex_id: str = "stilkritik-kodex",
) -> StilkritikKodex:
    if kunsttheorie_charta is None:
        kunsttheorie_charta = build_kunsttheorie_charta(charta_id=f"{kodex_id}-charta")

    normen: list[StilkritikKodexNorm] = []
    for parent_norm in kunsttheorie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kunsttheorie_charta_id.removeprefix(f'{kunsttheorie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH)
        normen.append(
            StilkritikKodexNorm(
                stilkritik_kodex_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"stilkritik-kodex:{new_geltung.value}",),
            )
        )
    return StilkritikKodex(
        kodex_id=kodex_id,
        kunsttheorie_charta=kunsttheorie_charta,
        normen=tuple(normen),
    )
