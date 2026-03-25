"""#710 — BiologieVerfassung ⭐: Block-Krone Biologie & Genetik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.synthetische_biologie_charta import SynthetischeBiologieCharta, build_synthetische_biologie_charta


class BiologieVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BIO_SOUVERAEN = "bio-souveraen"
    GRUNDLEGEND_BIO_SOUVERAEN = "grundlegend-bio-souveraen"


class BiologieVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class BiologieVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class BiologieVerfassungsNorm:
    bio_verfassung_id: str
    geltung: BiologieVerfassungGeltung
    typ: BiologieVerfassungTyp
    prozedur: BiologieVerfassungProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BiologieVerfassung:
    verfassung_id: str
    normen: List[BiologieVerfassungsNorm]
    parent: SynthetischeBiologieCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.bio_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BiologieVerfassungGeltung.GESPERRT: 0.0,
        BiologieVerfassungGeltung.BIO_SOUVERAEN: 0.05,
        BiologieVerfassungGeltung.GRUNDLEGEND_BIO_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        BiologieVerfassungGeltung.GESPERRT: 0,
        BiologieVerfassungGeltung.BIO_SOUVERAEN: 1,
        BiologieVerfassungGeltung.GRUNDLEGEND_BIO_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        BiologieVerfassungGeltung.GESPERRT: BiologieVerfassungTyp.BEOBACHTUNG,
        BiologieVerfassungGeltung.BIO_SOUVERAEN: BiologieVerfassungTyp.ANALYSE,
        BiologieVerfassungGeltung.GRUNDLEGEND_BIO_SOUVERAEN: BiologieVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        BiologieVerfassungGeltung.GESPERRT: BiologieVerfassungProzedur.INITIALISIEREN,
        BiologieVerfassungGeltung.BIO_SOUVERAEN: BiologieVerfassungProzedur.AKTIVIEREN,
        BiologieVerfassungGeltung.GRUNDLEGEND_BIO_SOUVERAEN: BiologieVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        BiologieVerfassungGeltung.GESPERRT: [BiologieVerfassungGeltung.GESPERRT],
        BiologieVerfassungGeltung.BIO_SOUVERAEN: [BiologieVerfassungGeltung.BIO_SOUVERAEN],
        BiologieVerfassungGeltung.GRUNDLEGEND_BIO_SOUVERAEN: [BiologieVerfassungGeltung.GRUNDLEGEND_BIO_SOUVERAEN],
    })


_init_map()


def build_biologie_verfassung(*, verfassung_id: str = "biologie-verfassung") -> BiologieVerfassung:
    parent = build_synthetische_biologie_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[BiologieVerfassungsNorm] = []
    for g in BiologieVerfassungGeltung:
        normen.append(BiologieVerfassungsNorm(
            bio_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(n.bio_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(n.bio_tier for n in parent.normen) + _TIER_DELTA[g],
            bio_ids=[f"bv-{verfassung_id}-{g.value}-001", f"bv-{verfassung_id}-{g.value}-002"],
            bio_tags=["bio", "biologie", "verfassung", g.value],
        ))
    return BiologieVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
