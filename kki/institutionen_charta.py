"""
#529 InstitutionenCharta — North/Coase/Williamson Institutionenökonomik & Transaktionskosten

Douglass North (1990): Institutionen, institutioneller Wandel und Wirtschaftsleistung —
  Institutionen als Spielregeln der Gesellschaft; formelle und informelle Beschränkungen;
  Pfadabhängigkeit und locked-in-Effekte in Peta-Schwarm-Institutionen.
Ronald Coase (1937/1960): The Nature of the Firm / The Problem of Social Cost — Transaktions-
  kosten als Grund für Unternehmensorganisation; Coase-Theorem: bei null Transaktionskosten
  irrelevanz der Eigentumsrechte; Institutionen als Transaktionskostenminimierung.
Oliver Williamson (1975): Markets and Hierarchies — Asset Specificity und Hold-up-Problem;
  Hierarchie vs. Markt als Governance-Mechanismen; Transaktionskostenökonomik im Schwarm.
Hernando de Soto (2000): The Mystery of Capital — Eigentumsrechte als Kapitalfundament;
  informelle Wirtschaft und formelle Institutionen; institutionelle Inklusion für Peta-Schwärme.
Leitsterns Peta-Schwarm verankert Institutionen als strukturgebende Kraft: GESPERRT schützt
institutionelle Grundnormen, INSTITUTIONELL kodiert adaptive Regelstrukturen zwischen Millionen
Agenten, GRUNDLEGEND_INSTITUTIONELL synthetisiert souveräne Institutionenordnung des Schwarms.
Parent: WirtschaftsNorm (#528)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wirtschafts_norm import (
    WirtschaftsNormSatz,
    WirtschaftsNormGeltung,
    build_wirtschafts_norm,
)

_WEIGHT_DELTA: dict["InstitutionenChartaGeltung", float] = {}
_TIER_DELTA: dict["InstitutionenChartaGeltung", int] = {}
_TYP_MAP: dict["InstitutionenChartaGeltung", "InstitutionenChartaTyp"] = {}
_PROZEDUR_MAP: dict["InstitutionenChartaGeltung", "InstitutionenChartaProzedur"] = {}
_GELTUNG_MAP: dict[WirtschaftsNormGeltung, "InstitutionenChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InstitutionenChartaGeltung.GESPERRT: 0.0,
        InstitutionenChartaGeltung.INSTITUTIONELL: 0.05,
        InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL: 0.1,
    })
    _TIER_DELTA.update({
        InstitutionenChartaGeltung.GESPERRT: 0,
        InstitutionenChartaGeltung.INSTITUTIONELL: 1,
        InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL: 2,
    })
    _TYP_MAP.update({
        InstitutionenChartaGeltung.GESPERRT: InstitutionenChartaTyp.SCHUTZ_INSTITUTION,
        InstitutionenChartaGeltung.INSTITUTIONELL: InstitutionenChartaTyp.ORDNUNGS_INSTITUTION,
        InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL: InstitutionenChartaTyp.SOUVERAENITAETS_INSTITUTION,
    })
    _PROZEDUR_MAP.update({
        InstitutionenChartaGeltung.GESPERRT: InstitutionenChartaProzedur.NOTPROZEDUR,
        InstitutionenChartaGeltung.INSTITUTIONELL: InstitutionenChartaProzedur.REGELPROTOKOLL,
        InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL: InstitutionenChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        WirtschaftsNormGeltung.GESPERRT: InstitutionenChartaGeltung.GESPERRT,
        WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV: InstitutionenChartaGeltung.INSTITUTIONELL,
        WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV: InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL,
    })


class InstitutionenChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    INSTITUTIONELL = "institutionell"
    GRUNDLEGEND_INSTITUTIONELL = "grundlegend-institutionell"


class InstitutionenChartaTyp(Enum):
    SCHUTZ_INSTITUTION = "schutz-institution"
    ORDNUNGS_INSTITUTION = "ordnungs-institution"
    SOUVERAENITAETS_INSTITUTION = "souveraenitaets-institution"


class InstitutionenChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class InstitutionenChartaNorm:
    institutionen_charta_id: str
    institutionen_typ: InstitutionenChartaTyp
    prozedur: InstitutionenChartaProzedur
    geltung: InstitutionenChartaGeltung
    institutionen_weight: float
    institutionen_tier: int
    canonical: bool
    institutionen_ids: tuple[str, ...]
    institutionen_tags: tuple[str, ...]


@dataclass(frozen=True)
class InstitutionenCharta:
    charta_id: str
    wirtschafts_norm: WirtschaftsNormSatz
    normen: tuple[InstitutionenChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.institutionen_charta_id for n in self.normen if n.geltung is InstitutionenChartaGeltung.GESPERRT)

    @property
    def institutionell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.institutionen_charta_id for n in self.normen if n.geltung is InstitutionenChartaGeltung.INSTITUTIONELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.institutionen_charta_id for n in self.normen if n.geltung is InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL)

    @property
    def charta_signal(self):
        if any(n.geltung is InstitutionenChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is InstitutionenChartaGeltung.INSTITUTIONELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-institutionell")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-institutionell")


_init_map()


def build_institutionen_charta(
    wirtschafts_norm: WirtschaftsNormSatz | None = None,
    *,
    charta_id: str = "institutionen-charta",
) -> InstitutionenCharta:
    if wirtschafts_norm is None:
        wirtschafts_norm = build_wirtschafts_norm(norm_id=f"{charta_id}-norm")

    normen: list[InstitutionenChartaNorm] = []
    for parent_norm in wirtschafts_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{wirtschafts_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.wirtschafts_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.wirtschafts_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL)
        normen.append(
            InstitutionenChartaNorm(
                institutionen_charta_id=new_id,
                institutionen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                institutionen_weight=new_weight,
                institutionen_tier=new_tier,
                canonical=is_canonical,
                institutionen_ids=parent_norm.wirtschafts_norm_ids + (new_id,),
                institutionen_tags=parent_norm.wirtschafts_norm_tags + (f"institutionen-charta:{new_geltung.value}",),
            )
        )
    return InstitutionenCharta(
        charta_id=charta_id,
        wirtschafts_norm=wirtschafts_norm,
        normen=tuple(normen),
    )
