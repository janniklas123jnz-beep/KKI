"""#709 — SynthetischeBiologieCharta: CRISPR, Gentechnik & Synthetic Biology."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.biologie_norm import BiologieNormSatz, build_biologie_norm


class SynthetischeBiologieChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SYNTHETISCH_BIO_AKTIV = "synthetisch-bio-aktiv"
    GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV = "grundlegend-synthetisch-bio-aktiv"


class SynthetischeBiologieChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class SynthetischeBiologieChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class SynthetischeBiologieChartaNorm:
    charta_id: str
    geltung: SynthetischeBiologieChartaGeltung
    typ: SynthetischeBiologieChartaTyp
    prozedur: SynthetischeBiologieChartaProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class SynthetischeBiologieCharta:
    charta_id: str
    normen: List[SynthetischeBiologieChartaNorm]
    parent: BiologieNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SynthetischeBiologieChartaGeltung.GESPERRT: 0.0,
        SynthetischeBiologieChartaGeltung.SYNTHETISCH_BIO_AKTIV: 0.05,
        SynthetischeBiologieChartaGeltung.GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        SynthetischeBiologieChartaGeltung.GESPERRT: 0,
        SynthetischeBiologieChartaGeltung.SYNTHETISCH_BIO_AKTIV: 1,
        SynthetischeBiologieChartaGeltung.GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV: 2,
    })
    _TYP_MAP.update({
        SynthetischeBiologieChartaGeltung.GESPERRT: SynthetischeBiologieChartaTyp.BEOBACHTUNG,
        SynthetischeBiologieChartaGeltung.SYNTHETISCH_BIO_AKTIV: SynthetischeBiologieChartaTyp.ANALYSE,
        SynthetischeBiologieChartaGeltung.GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV: SynthetischeBiologieChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        SynthetischeBiologieChartaGeltung.GESPERRT: SynthetischeBiologieChartaProzedur.INITIALISIEREN,
        SynthetischeBiologieChartaGeltung.SYNTHETISCH_BIO_AKTIV: SynthetischeBiologieChartaProzedur.AKTIVIEREN,
        SynthetischeBiologieChartaGeltung.GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV: SynthetischeBiologieChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        SynthetischeBiologieChartaGeltung.GESPERRT: [SynthetischeBiologieChartaGeltung.GESPERRT],
        SynthetischeBiologieChartaGeltung.SYNTHETISCH_BIO_AKTIV: [SynthetischeBiologieChartaGeltung.SYNTHETISCH_BIO_AKTIV],
        SynthetischeBiologieChartaGeltung.GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV: [SynthetischeBiologieChartaGeltung.GRUNDLEGEND_SYNTHETISCH_BIO_AKTIV],
    })


_init_map()


def build_synthetische_biologie_charta(*, charta_id: str = "synthetische-biologie-charta") -> SynthetischeBiologieCharta:
    parent = build_biologie_norm(norm_id=f"{charta_id}-parent")
    normen: List[SynthetischeBiologieChartaNorm] = []
    for g in SynthetischeBiologieChartaGeltung:
        normen.append(SynthetischeBiologieChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(e.bio_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(e.bio_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            bio_ids=[f"sb-{charta_id}-{g.value}-001", f"sb-{charta_id}-{g.value}-002"],
            bio_tags=["bio", "synthetische-biologie", g.value],
        ))
    return SynthetischeBiologieCharta(charta_id=charta_id, normen=normen, parent=parent)
