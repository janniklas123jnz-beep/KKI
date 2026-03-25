from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .bodenkunde_kodex import BodenkundeKodex, build_bodenkunde_kodex


class ErnaehrungswissenschaftManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_ERNAEHRUNGSWISSENSCHAFTLICH = auto()
    ERNAEHRUNGSWISSENSCHAFTLICH = auto()
    ERNAEHRUNGSWISSENSCHAFTLICH_AKTIV = auto()
    ERNAEHRUNGSWISSENSCHAFT_SOUVERAEN = auto()


class ErnaehrungswissenschaftManifestTyp(Enum):
    ERNAEHRUNGSMANIFEST = auto()
    NAEHRSTOFFPROFIL = auto()
    ERNAEHRUNGSEMPFEHLUNG = auto()


class ErnaehrungswissenschaftManifestProzedur(Enum):
    NAEHRSTOFFANALYSE = auto()
    ERNAEHRUNGSBEWERTUNG = auto()
    DIAETPLANUNG = auto()


_WEIGHT_DELTA: dict[ErnaehrungswissenschaftManifestGeltung, float] = {
    ErnaehrungswissenschaftManifestGeltung.GESPERRT: 0.0,
    ErnaehrungswissenschaftManifestGeltung.GRUNDLEGEND_ERNAEHRUNGSWISSENSCHAFTLICH: 1.6,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFTLICH: 3.2,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFTLICH_AKTIV: 4.8,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFT_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    ErnaehrungswissenschaftManifestGeltung.GESPERRT: ErnaehrungswissenschaftManifestTyp.ERNAEHRUNGSMANIFEST,
    ErnaehrungswissenschaftManifestGeltung.GRUNDLEGEND_ERNAEHRUNGSWISSENSCHAFTLICH: ErnaehrungswissenschaftManifestTyp.NAEHRSTOFFPROFIL,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFTLICH: ErnaehrungswissenschaftManifestTyp.NAEHRSTOFFPROFIL,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFTLICH_AKTIV: ErnaehrungswissenschaftManifestTyp.ERNAEHRUNGSEMPFEHLUNG,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFT_SOUVERAEN: ErnaehrungswissenschaftManifestTyp.ERNAEHRUNGSEMPFEHLUNG,
}

_PROZEDUR_MAP = {
    ErnaehrungswissenschaftManifestGeltung.GESPERRT: ErnaehrungswissenschaftManifestProzedur.NAEHRSTOFFANALYSE,
    ErnaehrungswissenschaftManifestGeltung.GRUNDLEGEND_ERNAEHRUNGSWISSENSCHAFTLICH: ErnaehrungswissenschaftManifestProzedur.NAEHRSTOFFANALYSE,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFTLICH: ErnaehrungswissenschaftManifestProzedur.ERNAEHRUNGSBEWERTUNG,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFTLICH_AKTIV: ErnaehrungswissenschaftManifestProzedur.ERNAEHRUNGSBEWERTUNG,
    ErnaehrungswissenschaftManifestGeltung.ERNAEHRUNGSWISSENSCHAFT_SOUVERAEN: ErnaehrungswissenschaftManifestProzedur.DIAETPLANUNG,
}


@dataclass(frozen=True)
class ErnaehrungswissenschaftManifestNorm:
    geltung: ErnaehrungswissenschaftManifestGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: ErnaehrungswissenschaftManifestTyp
    prozedur: ErnaehrungswissenschaftManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ErnaehrungswissenschaftManifest:
    normen: tuple[ErnaehrungswissenschaftManifestNorm, ...]
    parent: Optional[BodenkundeKodex] = None


def build_ernaehrungswissenschaft_manifest(parent: Optional[BodenkundeKodex] = None) -> ErnaehrungswissenschaftManifest:
    if parent is None:
        parent = build_bodenkunde_kodex()
    base = sum(e.agrar_weight for e in parent.eintraege)
    normen = tuple(
        ErnaehrungswissenschaftManifestNorm(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"ernaehrungswissenschaft-{g.name.lower()}-001",),
            agrar_tags=("ernaehrungswissenschaft", "manifest", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ErnaehrungswissenschaftManifestGeltung)
    )
    return ErnaehrungswissenschaftManifest(normen=normen, parent=parent)
