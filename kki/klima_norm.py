from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klimaanpassung_senat import KlimaanpassungSenat, build_klimaanpassung_senat


class KlimaNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMA_NORMATIV = auto()
    KLIMA_NORMATIV = auto()
    KLIMA_NORMATIV_AKTIV = auto()
    KLIMA_NORMATIV_SOUVERAEN = auto()


class KlimaNormTyp(Enum):
    KLIMANORM = auto()
    KLIMASTANDARD = auto()
    KLIMARICHTLINIE = auto()


class KlimaNormProzedur(Enum):
    KLIMANORMIERUNG = auto()
    KLIMASTANDARDISIERUNG = auto()
    KLIMAZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_KLIMA_NORMATIV": 1.9,
    "KLIMA_NORMATIV": 3.8,
    "KLIMA_NORMATIV_AKTIV": 5.7,
    "KLIMA_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, KlimaNormTyp] = {
    "GESPERRT": KlimaNormTyp.KLIMANORM,
    "GRUNDLEGEND_KLIMA_NORMATIV": KlimaNormTyp.KLIMARICHTLINIE,
    "KLIMA_NORMATIV": KlimaNormTyp.KLIMARICHTLINIE,
    "KLIMA_NORMATIV_AKTIV": KlimaNormTyp.KLIMASTANDARD,
    "KLIMA_NORMATIV_SOUVERAEN": KlimaNormTyp.KLIMASTANDARD,
}

_PROZEDUR_MAP: dict[str, KlimaNormProzedur] = {
    "GESPERRT": KlimaNormProzedur.KLIMANORMIERUNG,
    "GRUNDLEGEND_KLIMA_NORMATIV": KlimaNormProzedur.KLIMANORMIERUNG,
    "KLIMA_NORMATIV": KlimaNormProzedur.KLIMASTANDARDISIERUNG,
    "KLIMA_NORMATIV_AKTIV": KlimaNormProzedur.KLIMASTANDARDISIERUNG,
    "KLIMA_NORMATIV_SOUVERAEN": KlimaNormProzedur.KLIMAZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[KlimaNormGeltung, str] = {g: g.name for g in KlimaNormGeltung}

_GELTUNG_MAP: dict[str, KlimaNormGeltung] = {
    "gesperrt": KlimaNormGeltung.GESPERRT,
    "grundlegend_klimaanpassend": KlimaNormGeltung.GRUNDLEGEND_KLIMA_NORMATIV,
    "klimaanpassend": KlimaNormGeltung.KLIMA_NORMATIV,
    "klimaanpassend_aktiv": KlimaNormGeltung.KLIMA_NORMATIV_AKTIV,
    "klimaanpassung_souveraen": KlimaNormGeltung.KLIMA_NORMATIV_SOUVERAEN,
}


@dataclass(frozen=True)
class KlimaNormEintrag:
    geltung: KlimaNormGeltung
    klima_norm_weight: float
    klima_norm_tier: int
    klima_norm_ids: tuple[str, ...]
    klima_norm_tags: tuple[str, ...]
    typ: KlimaNormTyp
    prozedur: KlimaNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimaNormSatz:
    normen: tuple[KlimaNormEintrag, ...]
    parent: Optional[KlimaanpassungSenat] = None


def build_klima_norm(parent: Optional[KlimaanpassungSenat] = None) -> KlimaNormSatz:
    if parent is None:
        parent = build_klimaanpassung_senat()
    base = sum(n.klima_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(KlimaNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(KlimaNormEintrag(
            geltung=g,
            klima_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            klima_norm_tier=i + 1,
            klima_norm_ids=(f"klima-norm-{key.lower()}-001",),
            klima_norm_tags=("klima", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return KlimaNormSatz(normen=tuple(eintraege), parent=parent)
