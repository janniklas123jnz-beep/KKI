"""
#584 DidaktikKodex — Comenius/Klafki/Bloom Didaktik Kodex

Jan Amos Comenius (1657): Didactica Magna — Alle alles gründlich zu lehren; Anschaulichkeit
  als didaktisches Grundprinzip; Schulstufen als entwicklungsgemäße Lernorganisation;
  Schulbuch als Unterrichtsmedium; Ordnung als Fundament aller Didaktik im
  Peta-Schwarm Leitstern.
Wolfgang Klafki (1958): Kategoriale Bildung — Material und formale Bildung als Dialektik;
  exemplarisches Lernen als didaktisches Prinzip; Bildungsinhalt und Bildungsgehalt als
  analytische Unterscheidung; kritisch-konstruktive Didaktik als Weiterentwicklung;
  Schlüsselprobleme als curriculare Grundkategorie im Peta-Schwarm Leitstern.
Benjamin Bloom (1956): Taxonomy of Educational Objectives — Lernzieltaxonomie als
  didaktisches Instrument; kognitive, affektive und psychomotorische Lernziele;
  Operationalisierung von Bildungszielen; Mastery Learning als Unterrichtskonzept;
  Revision der Taxonomie als Wissenskategorie im Peta-Schwarm Leitstern. 📋✏️
Parent: LerntheorieCharta (#583)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lerntheorie_charta import (
    LerntheorieCharta,
    LerntheorieChartaGeltung,
    build_lerntheorie_charta,
)

_WEIGHT_DELTA: dict["DidaktikKodexGeltung", float] = {}
_TIER_DELTA: dict["DidaktikKodexGeltung", int] = {}
_TYP_MAP: dict["DidaktikKodexGeltung", "DidaktikKodexTyp"] = {}
_PROZEDUR_MAP: dict["DidaktikKodexGeltung", "DidaktikKodexProzedur"] = {}
_GELTUNG_MAP: dict[LerntheorieChartaGeltung, "DidaktikKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DidaktikKodexGeltung.GESPERRT: 0.0,
        DidaktikKodexGeltung.DIDAKTISCH: 0.05,
        DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH: 0.1,
    })
    _TIER_DELTA.update({
        DidaktikKodexGeltung.GESPERRT: 0,
        DidaktikKodexGeltung.DIDAKTISCH: 1,
        DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH: 2,
    })
    _TYP_MAP.update({
        DidaktikKodexGeltung.GESPERRT: DidaktikKodexTyp.SCHUTZ_DIDAKTIK,
        DidaktikKodexGeltung.DIDAKTISCH: DidaktikKodexTyp.ORDNUNGS_DIDAKTIK,
        DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH: DidaktikKodexTyp.SOUVERAENITAETS_DIDAKTIK,
    })
    _PROZEDUR_MAP.update({
        DidaktikKodexGeltung.GESPERRT: DidaktikKodexProzedur.NOTPROZEDUR,
        DidaktikKodexGeltung.DIDAKTISCH: DidaktikKodexProzedur.REGELPROTOKOLL,
        DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH: DidaktikKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        LerntheorieChartaGeltung.GESPERRT: DidaktikKodexGeltung.GESPERRT,
        LerntheorieChartaGeltung.LERNTHEORETISCH: DidaktikKodexGeltung.DIDAKTISCH,
        LerntheorieChartaGeltung.GRUNDLEGEND_LERNTHEORETISCH: DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH,
    })


class DidaktikKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    DIDAKTISCH = "didaktisch"
    GRUNDLEGEND_DIDAKTISCH = "grundlegend-didaktisch"


class DidaktikKodexTyp(Enum):
    SCHUTZ_DIDAKTIK = "schutz-didaktik"
    ORDNUNGS_DIDAKTIK = "ordnungs-didaktik"
    SOUVERAENITAETS_DIDAKTIK = "souveraenitaets-didaktik"


class DidaktikKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class DidaktikKodexNorm:
    didaktik_kodex_id: str
    paedagogik_typ: DidaktikKodexTyp
    prozedur: DidaktikKodexProzedur
    geltung: DidaktikKodexGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class DidaktikKodex:
    kodex_id: str
    lerntheorie_charta: LerntheorieCharta
    normen: tuple[DidaktikKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.didaktik_kodex_id for n in self.normen
            if n.geltung is DidaktikKodexGeltung.GESPERRT
        )

    @property
    def didaktisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.didaktik_kodex_id for n in self.normen
            if n.geltung is DidaktikKodexGeltung.DIDAKTISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.didaktik_kodex_id for n in self.normen
            if n.geltung is DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH
        )

    @property
    def kodex_signal(self):
        if any(n.geltung is DidaktikKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is DidaktikKodexGeltung.DIDAKTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-didaktisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-didaktisch")


_init_map()


def build_didaktik_kodex(
    lerntheorie_charta: LerntheorieCharta | None = None,
    *,
    kodex_id: str = "didaktik-kodex",
) -> DidaktikKodex:
    if lerntheorie_charta is None:
        lerntheorie_charta = build_lerntheorie_charta(charta_id=f"{kodex_id}-charta")

    normen: list[DidaktikKodexNorm] = []
    for parent_norm in lerntheorie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.lerntheorie_charta_id.removeprefix(f'{lerntheorie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH)
        normen.append(
            DidaktikKodexNorm(
                didaktik_kodex_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"didaktik-kodex:{new_geltung.value}",),
            )
        )
    return DidaktikKodex(
        kodex_id=kodex_id,
        lerntheorie_charta=lerntheorie_charta,
        normen=tuple(normen),
    )
