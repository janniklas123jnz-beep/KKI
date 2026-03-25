from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .tiefseekartierung_charta import TiefseekartierungCharta, build_tiefseekartierung_charta


class MarineBiologieKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class MarineBiologieKodexTyp(Enum):
    MARINEBIOLOGIE = auto()
    OEKOSYSTEMSYSTEM = auto()
    BIOLOGIEKOMPONENTE = auto()


class MarineBiologieKodexProzedur(Enum):
    BIOLOGIEANALYSE = auto()
    BIOLOGIESYNTHESE = auto()
    BIOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MarineBiologieKodexGeltung, float] = {
    MarineBiologieKodexGeltung.GESPERRT: 0.0,
    MarineBiologieKodexGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.5,
    MarineBiologieKodexGeltung.OZEANOGRAPHISCH: 3.0,
    MarineBiologieKodexGeltung.OZEANOGRAPHISCH_AKTIV: 4.5,
    MarineBiologieKodexGeltung.OZEAN_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    MarineBiologieKodexGeltung.GESPERRT: MarineBiologieKodexTyp.MARINEBIOLOGIE,
    MarineBiologieKodexGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: MarineBiologieKodexTyp.BIOLOGIEKOMPONENTE,
    MarineBiologieKodexGeltung.OZEANOGRAPHISCH: MarineBiologieKodexTyp.BIOLOGIEKOMPONENTE,
    MarineBiologieKodexGeltung.OZEANOGRAPHISCH_AKTIV: MarineBiologieKodexTyp.OEKOSYSTEMSYSTEM,
    MarineBiologieKodexGeltung.OZEAN_SOUVERAEN: MarineBiologieKodexTyp.OEKOSYSTEMSYSTEM,
}

_PROZEDUR_MAP = {
    MarineBiologieKodexGeltung.GESPERRT: MarineBiologieKodexProzedur.BIOLOGIEANALYSE,
    MarineBiologieKodexGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: MarineBiologieKodexProzedur.BIOLOGIEANALYSE,
    MarineBiologieKodexGeltung.OZEANOGRAPHISCH: MarineBiologieKodexProzedur.BIOLOGIESYNTHESE,
    MarineBiologieKodexGeltung.OZEANOGRAPHISCH_AKTIV: MarineBiologieKodexProzedur.BIOLOGIESYNTHESE,
    MarineBiologieKodexGeltung.OZEAN_SOUVERAEN: MarineBiologieKodexProzedur.BIOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class MarineBiologieKodexEintrag:
    geltung: MarineBiologieKodexGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: MarineBiologieKodexTyp
    prozedur: MarineBiologieKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MarineBiologieKodex:
    eintraege: tuple[MarineBiologieKodexEintrag, ...]
    parent: Optional[TiefseekartierungCharta] = None


def build_marine_biologie_kodex(parent: Optional[TiefseekartierungCharta] = None) -> MarineBiologieKodex:
    if parent is None:
        parent = build_tiefseekartierung_charta()
    base = sum(n.ozean_weight for n in parent.normen)
    eintraege = tuple(
        MarineBiologieKodexEintrag(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"marine-biologie-{g.name.lower()}-001",),
            ozean_tags=("ozean", "marine_biologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MarineBiologieKodexGeltung)
    )
    return MarineBiologieKodex(eintraege=eintraege, parent=parent)
