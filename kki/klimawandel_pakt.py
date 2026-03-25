from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klimamodell_manifest import KlimamodellManifest, build_klimamodell_manifest


class KlimawandelPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMAWANDELHAFT = auto()
    KLIMAWANDELHAFT = auto()
    KLIMAWANDELHAFT_AKTIV = auto()
    KLIMAWANDEL_SOUVERAEN = auto()


class KlimawandelPaktTyp(Enum):
    KLIMAWANDELPAKT = auto()
    TREIBHAUSEFFEKT = auto()
    KLIMAFOLGE = auto()


class KlimawandelPaktProzedur(Enum):
    KLIMAWANDELANALYSE = auto()
    KLIMAWANDELBEWERTUNG = auto()
    KLIMAWANDELPROGNOSE = auto()


_WEIGHT_DELTA: dict[KlimawandelPaktGeltung, float] = {
    KlimawandelPaktGeltung.GESPERRT: 0.0,
    KlimawandelPaktGeltung.GRUNDLEGEND_KLIMAWANDELHAFT: 1.7,
    KlimawandelPaktGeltung.KLIMAWANDELHAFT: 3.4,
    KlimawandelPaktGeltung.KLIMAWANDELHAFT_AKTIV: 5.1,
    KlimawandelPaktGeltung.KLIMAWANDEL_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    KlimawandelPaktGeltung.GESPERRT: KlimawandelPaktTyp.KLIMAWANDELPAKT,
    KlimawandelPaktGeltung.GRUNDLEGEND_KLIMAWANDELHAFT: KlimawandelPaktTyp.KLIMAFOLGE,
    KlimawandelPaktGeltung.KLIMAWANDELHAFT: KlimawandelPaktTyp.KLIMAFOLGE,
    KlimawandelPaktGeltung.KLIMAWANDELHAFT_AKTIV: KlimawandelPaktTyp.TREIBHAUSEFFEKT,
    KlimawandelPaktGeltung.KLIMAWANDEL_SOUVERAEN: KlimawandelPaktTyp.TREIBHAUSEFFEKT,
}

_PROZEDUR_MAP = {
    KlimawandelPaktGeltung.GESPERRT: KlimawandelPaktProzedur.KLIMAWANDELANALYSE,
    KlimawandelPaktGeltung.GRUNDLEGEND_KLIMAWANDELHAFT: KlimawandelPaktProzedur.KLIMAWANDELANALYSE,
    KlimawandelPaktGeltung.KLIMAWANDELHAFT: KlimawandelPaktProzedur.KLIMAWANDELBEWERTUNG,
    KlimawandelPaktGeltung.KLIMAWANDELHAFT_AKTIV: KlimawandelPaktProzedur.KLIMAWANDELBEWERTUNG,
    KlimawandelPaktGeltung.KLIMAWANDEL_SOUVERAEN: KlimawandelPaktProzedur.KLIMAWANDELPROGNOSE,
}


@dataclass(frozen=True)
class KlimawandelPaktEintrag:
    geltung: KlimawandelPaktGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: KlimawandelPaktTyp
    prozedur: KlimawandelPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimawandelPakt:
    eintraege: tuple[KlimawandelPaktEintrag, ...]
    parent: Optional[KlimamodellManifest] = None


def build_klimawandel_pakt(parent: Optional[KlimamodellManifest] = None) -> KlimawandelPakt:
    if parent is None:
        parent = build_klimamodell_manifest()
    base = sum(n.klima_weight for n in parent.normen)
    eintraege = tuple(
        KlimawandelPaktEintrag(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"klimawandel-pakt-{g.name.lower()}-001",),
            klima_tags=("klimawandel", "pakt", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimawandelPaktGeltung)
    )
    return KlimawandelPakt(eintraege=eintraege, parent=parent)
