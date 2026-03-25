"""#661 OekologieFeld — Wurzel Ökologie & Umweltwissenschaft (parent: InternetkapazitaetVerfassung)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .internetkapazitaet_verfassung import InternetkapazitaetVerfassung, build_internetkapazitaet_verfassung

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class OekologieFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    OEKOLOGISCH_AKTIV = "oekologisch-aktiv"
    GRUNDLEGEND_OEKOLOGISCH_AKTIV = "grundlegend-oekologisch-aktiv"


class OekologieFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class OekologieFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class OekologieFeldNorm:
    oekologie_feld_id: str
    geltung: OekologieFeldGeltung
    typ: OekologieFeldTyp
    prozedur: OekologieFeldProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class OekologieFeld:
    feld_id: str
    normen: List[OekologieFeldNorm]
    parent: InternetkapazitaetVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        OekologieFeldGeltung.GESPERRT: 0.0,
        OekologieFeldGeltung.OEKOLOGISCH_AKTIV: 0.05,
        OekologieFeldGeltung.GRUNDLEGEND_OEKOLOGISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        OekologieFeldGeltung.GESPERRT: 0,
        OekologieFeldGeltung.OEKOLOGISCH_AKTIV: 1,
        OekologieFeldGeltung.GRUNDLEGEND_OEKOLOGISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        OekologieFeldGeltung.GESPERRT: OekologieFeldTyp.BEOBACHTUNG,
        OekologieFeldGeltung.OEKOLOGISCH_AKTIV: OekologieFeldTyp.ANALYSE,
        OekologieFeldGeltung.GRUNDLEGEND_OEKOLOGISCH_AKTIV: OekologieFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        OekologieFeldGeltung.GESPERRT: OekologieFeldProzedur.INITIALISIEREN,
        OekologieFeldGeltung.OEKOLOGISCH_AKTIV: OekologieFeldProzedur.AKTIVIEREN,
        OekologieFeldGeltung.GRUNDLEGEND_OEKOLOGISCH_AKTIV: OekologieFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        OekologieFeldGeltung.GESPERRT: [OekologieFeldGeltung.GESPERRT],
        OekologieFeldGeltung.OEKOLOGISCH_AKTIV: [OekologieFeldGeltung.OEKOLOGISCH_AKTIV],
        OekologieFeldGeltung.GRUNDLEGEND_OEKOLOGISCH_AKTIV: [OekologieFeldGeltung.GRUNDLEGEND_OEKOLOGISCH_AKTIV],
    })


_init_map()


def build_oekologie_feld(*, feld_id: str = "oekologie-feld") -> OekologieFeld:
    parent = build_internetkapazitaet_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[OekologieFeldNorm] = []
    for g in OekologieFeldGeltung:
        normen.append(OekologieFeldNorm(
            oekologie_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(n.internet_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(n.internet_tier for n in parent.normen) + _TIER_DELTA[g],
            oekologie_ids=[f"of-{feld_id}-{g.value}-001", f"of-{feld_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "feld", g.value],
        ))
    return OekologieFeld(feld_id=feld_id, normen=normen, parent=parent)
