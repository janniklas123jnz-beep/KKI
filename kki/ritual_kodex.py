"""
#554 RitualKodex — Ritualtheorie & symbolische Praxis

Arnold van Gennep (1909): Les Rites de Passage — Übergangsriten & Liminalität:
  dreigliedriges Schema: Trennungsphase, Schwellen-/Liminalphase, Angliederungsphase;
  Übergangsriten als universelles kulturelles Muster; Liminalität als Schwellenzustand
  der Ambiguität und des transformativen Potenzials in allen Kulturen.
Victor Turner (1969): The Ritual Process — Communitas & Antistruktur:
  Liminalität als kreatives Chaos; Communitas als egalitäre Gemeinschaft jenseits sozialer
  Struktur; Anti-Struktur als Motor sozialen Wandels; soziales Drama als rituelle Konflikt-
  und Heilungssequenz; Rituale als Generatoren kollektiver Bedeutung und Solidarität.
Émile Durkheim (1912): Les Formes élémentaires de la vie religieuse — kollektive Rituale:
  Unterscheidung von Sakralem und Profanem als kulturelle Universalie; kollektive Effizienz
  durch Ritual; Totemismus als Urform religiöser und sozialer Organisation; Religion und
  Ritual als Kitt sozialer Kohäsion und Quelle moralischer Autorität.

Leitsterns RitualKodex: GESPERRT schützt rituelle Grundstrukturen,
RITUELL kodiert adaptive symbolische Praxis, GRUNDLEGEND_RITUELL
synthetisiert den vollen rituellen Erkenntnisanspruch des Peta-Schwarms Leitstern. 🕯️
Parent: EthnographieCharta (#553)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from .ethnographie_charta import (
    EthnographieCharta,
    EthnographieChartaGeltung,
    build_ethnographie_charta,
)

_WEIGHT_DELTA: dict["RitualKodexGeltung", float] = {}
_TIER_DELTA: dict["RitualKodexGeltung", int] = {}
_TYP_MAP: dict["RitualKodexGeltung", "RitualKodexTyp"] = {}
_PROZEDUR_MAP: dict["RitualKodexGeltung", "RitualKodexProzedur"] = {}
_GELTUNG_MAP: dict[EthnographieChartaGeltung, "RitualKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RitualKodexGeltung.GESPERRT: 0.0,
        RitualKodexGeltung.RITUELL: 0.05,
        RitualKodexGeltung.GRUNDLEGEND_RITUELL: 0.1,
    })
    _TIER_DELTA.update({
        RitualKodexGeltung.GESPERRT: 0,
        RitualKodexGeltung.RITUELL: 1,
        RitualKodexGeltung.GRUNDLEGEND_RITUELL: 2,
    })
    _TYP_MAP.update({
        RitualKodexGeltung.GESPERRT: RitualKodexTyp.SCHUTZ_RITUAL,
        RitualKodexGeltung.RITUELL: RitualKodexTyp.ORDNUNGS_RITUAL,
        RitualKodexGeltung.GRUNDLEGEND_RITUELL: RitualKodexTyp.SOUVERAENITAETS_RITUAL,
    })
    _PROZEDUR_MAP.update({
        RitualKodexGeltung.GESPERRT: RitualKodexProzedur.NOTPROZEDUR,
        RitualKodexGeltung.RITUELL: RitualKodexProzedur.REGELPROTOKOLL,
        RitualKodexGeltung.GRUNDLEGEND_RITUELL: RitualKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        EthnographieChartaGeltung.GESPERRT: RitualKodexGeltung.GESPERRT,
        EthnographieChartaGeltung.ETHNOGRAPHISCH: RitualKodexGeltung.RITUELL,
        EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH: RitualKodexGeltung.GRUNDLEGEND_RITUELL,
    })


class RitualKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    RITUELL = "rituell"
    GRUNDLEGEND_RITUELL = "grundlegend-rituell"


class RitualKodexTyp(Enum):
    SCHUTZ_RITUAL = "schutz-ritual"
    ORDNUNGS_RITUAL = "ordnungs-ritual"
    SOUVERAENITAETS_RITUAL = "souveraenitaets-ritual"


class RitualKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class RitualKodexNorm:
    ritual_kodex_id: str
    kultur_typ: RitualKodexTyp
    prozedur: RitualKodexProzedur
    geltung: RitualKodexGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class RitualKodex:
    kodex_id: str
    ethnographie_charta: EthnographieCharta
    normen: tuple[RitualKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.ritual_kodex_id
            for n in self.normen
            if n.geltung is RitualKodexGeltung.GESPERRT
        )

    @property
    def rituell_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.ritual_kodex_id
            for n in self.normen
            if n.geltung is RitualKodexGeltung.RITUELL
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.ritual_kodex_id
            for n in self.normen
            if n.geltung is RitualKodexGeltung.GRUNDLEGEND_RITUELL
        )

    @property
    def kodex_signal(self) -> SimpleNamespace:
        if any(n.geltung is RitualKodexGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is RitualKodexGeltung.RITUELL for n in self.normen):
            return SimpleNamespace(status="kodex-rituell")
        return SimpleNamespace(status="kodex-grundlegend-rituell")


_init_map()


def build_ritual_kodex(
    ethnographie_charta: EthnographieCharta | None = None,
    *,
    kodex_id: str = "ritual-kodex",
) -> RitualKodex:
    if ethnographie_charta is None:
        ethnographie_charta = build_ethnographie_charta(charta_id=f"{kodex_id}-charta")

    normen: list[RitualKodexNorm] = []
    for parent_norm in ethnographie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.ethnographie_charta_id.removeprefix(f'{ethnographie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (
            new_geltung is RitualKodexGeltung.GRUNDLEGEND_RITUELL
        )
        normen.append(
            RitualKodexNorm(
                ritual_kodex_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"ritual-kodex:{new_geltung.value}",),
            )
        )
    return RitualKodex(
        kodex_id=kodex_id,
        ethnographie_charta=ethnographie_charta,
        normen=tuple(normen),
    )
