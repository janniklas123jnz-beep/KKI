from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .gravitationsfeld_kodex import GravitationsfeldKodex, build_gravitationsfeld_kodex


class GeomagnetismusManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class GeomagnetismusManifestTyp(Enum):
    GEOMAGNETISMUS = auto()
    MAGNETFELDSYSTEM = auto()
    MAGNETKOMPONENTE = auto()


class GeomagnetismusManifestProzedur(Enum):
    MAGNETANALYSE = auto()
    MAGNETSYNTHESE = auto()
    MAGNETBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GeomagnetismusManifestGeltung, float] = {
    GeomagnetismusManifestGeltung.GESPERRT: 0.0,
    GeomagnetismusManifestGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.6,
    GeomagnetismusManifestGeltung.GEOPHYSIKALISCH: 3.2,
    GeomagnetismusManifestGeltung.GEOPHYSIKALISCH_AKTIV: 4.8,
    GeomagnetismusManifestGeltung.GEOPHYSIK_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    GeomagnetismusManifestGeltung.GESPERRT: GeomagnetismusManifestTyp.GEOMAGNETISMUS,
    GeomagnetismusManifestGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GeomagnetismusManifestTyp.MAGNETKOMPONENTE,
    GeomagnetismusManifestGeltung.GEOPHYSIKALISCH: GeomagnetismusManifestTyp.MAGNETKOMPONENTE,
    GeomagnetismusManifestGeltung.GEOPHYSIKALISCH_AKTIV: GeomagnetismusManifestTyp.MAGNETFELDSYSTEM,
    GeomagnetismusManifestGeltung.GEOPHYSIK_SOUVERAEN: GeomagnetismusManifestTyp.MAGNETFELDSYSTEM,
}

_PROZEDUR_MAP = {
    GeomagnetismusManifestGeltung.GESPERRT: GeomagnetismusManifestProzedur.MAGNETANALYSE,
    GeomagnetismusManifestGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GeomagnetismusManifestProzedur.MAGNETANALYSE,
    GeomagnetismusManifestGeltung.GEOPHYSIKALISCH: GeomagnetismusManifestProzedur.MAGNETSYNTHESE,
    GeomagnetismusManifestGeltung.GEOPHYSIKALISCH_AKTIV: GeomagnetismusManifestProzedur.MAGNETSYNTHESE,
    GeomagnetismusManifestGeltung.GEOPHYSIK_SOUVERAEN: GeomagnetismusManifestProzedur.MAGNETBEWERTUNG,
}


@dataclass(frozen=True)
class GeomagnetismusManifestNorm:
    geltung: GeomagnetismusManifestGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: GeomagnetismusManifestTyp
    prozedur: GeomagnetismusManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeomagnetismusManifest:
    normen: tuple[GeomagnetismusManifestNorm, ...]
    parent: Optional[GravitationsfeldKodex] = None


def build_geomagnetismus_manifest(parent: Optional[GravitationsfeldKodex] = None) -> GeomagnetismusManifest:
    if parent is None:
        parent = build_gravitationsfeld_kodex()
    base = sum(e.geophysik_weight for e in parent.eintraege)
    normen = tuple(
        GeomagnetismusManifestNorm(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"geomagnetismus-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "geomagnetismus", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeomagnetismusManifestGeltung)
    )
    return GeomagnetismusManifest(normen=normen, parent=parent)
