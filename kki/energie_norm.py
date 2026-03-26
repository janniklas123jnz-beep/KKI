"""
#958 EnergieNorm — Energiestandards: ISO 50001, EU-Taxonomie & GHG-Protokoll (*_norm-Muster).
ISO 50001 (2018): Energy Management Systems — internationaler Standard für
  Energiemanagementsysteme; systematische Energieeffizienzverbesserung in Organisationen.
EU Taxonomie-Verordnung (2020): Sustainable Finance Taxonomy — Klassifizierung
  nachhaltiger Wirtschaftsaktivitäten; Grundlage für grüne Investitionen und ESG.
GHG Protocol (2001): Corporate Standard — Treibhausgasbilanzierung nach Scope 1/2/3;
  Weltstandard für Corporate Carbon Footprint; Basis aller Klimaberichterstattung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .smart_grid_senat import SmartGridSenat, build_smart_grid_senat


class EnergieNormTyp(Enum):
    ISO_ENERGIEMANAGEMENT = auto()
    EU_TAXONOMIE = auto()
    GHG_PROTOKOLL = auto()
    ERNEUERBARE_ZERTIFIKAT = auto()
    GEBAEUDE_ENERGIENORM = auto()


class EnergieNormProzedur(Enum):
    NORMIERUNG = auto()
    BILANZIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    BERICHTERSTATTUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "ISO_ENERGIEMANAGEMENT": 0.0,
    "EU_TAXONOMIE": 2.0,
    "GHG_PROTOKOLL": 4.0,
    "ERNEUERBARE_ZERTIFIKAT": 6.0,
    "GEBAEUDE_ENERGIENORM": 8.0,
}
_TYP_MAP = {
    "ISO_ENERGIEMANAGEMENT": "iso_energiemanagement",
    "EU_TAXONOMIE": "eu_taxonomie",
    "GHG_PROTOKOLL": "ghg_protokoll",
    "ERNEUERBARE_ZERTIFIKAT": "erneuerbare_zertifikat",
    "GEBAEUDE_ENERGIENORM": "gebaeude_energienorm",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "BILANZIERUNG": "bilanzierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "BERICHTERSTATTUNG": "berichterstattung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class EnergieNormEintrag:
    typ: EnergieNormTyp
    prozedur: EnergieNormProzedur
    energie_norm_weight: float
    energie_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class EnergieNorm:
    normen: tuple[EnergieNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "energie-norm-958",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_energie_norm(parent: Optional[SmartGridSenat] = None) -> EnergieNorm:
    if parent is None:
        parent = build_smart_grid_senat()
    base = sum(n.energie_weight for n in parent.normen)
    normen = tuple(
        EnergieNormEintrag(
            typ=t,
            prozedur=list(EnergieNormProzedur)[i],
            energie_norm_weight=base + _WEIGHT_DELTA[t.name],
            energie_norm_tier=i + 1,
        )
        for i, t in enumerate(EnergieNormTyp)
    )
    return EnergieNorm(normen=normen)
