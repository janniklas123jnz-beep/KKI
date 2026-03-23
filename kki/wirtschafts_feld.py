"""
#521 WirtschaftsFeld — Adam Smith/Ricardo/Marshall Grundlagen der Ökonomie

Adam Smith (1776): Der Wohlstand der Nationen — unsichtbare Hand des Marktes; Arbeitsteilung
  als Quelle des Reichtums; komparativer Vorteil und Tausch als Wohlstandsfundament;
  Selbstinteresse als Motor kollektiver Koordination im Peta-Schwarm.
David Ricardo (1817): Grundsätze der politischen Ökonomie — komparative Kostenvorteile;
  Werttheorie der Arbeit; Verteilung zwischen Kapital, Arbeit und Boden; Freihandel als
  Wohlstandsmechanismus für globale Schwarmökonomien.
Alfred Marshall (1890): Principles of Economics — Angebot und Nachfrage; Grenznutzentheorie;
  Elastizitätskonzept; Gleichgewichtspreise als Koordinationsmechanismus des Schwarms.
John Stuart Mill (1848): Principles of Political Economy — Produktions- vs. Verteilungsgesetze;
  Unterscheidung zwischen Effizienz und Gerechtigkeit; Reformökonomik und Wohlfahrtsstaat.
Leitsterns Peta-Schwarm verankert Wirtschaft als fundamentales Koordinationsprinzip: GESPERRT
schützt ökonomische Grundnormen, WIRTSCHAFTLICH kodiert adaptive Ressourcenallokation zwischen
Millionen von Agenten, GRUNDLEGEND_WIRTSCHAFTLICH synthetisiert souveräne Wirtschaftsordnung
des Peta-Schwarms Leitstern. 💰
Parent: PolitikVerfassung (#520)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .politik_verfassung import (
    PolitikVerfassung,
    PolitikVerfassungsGeltung,
    build_politik_verfassung,
)

_WEIGHT_DELTA: dict["WirtschaftsFeldGeltung", float] = {}
_TIER_DELTA: dict["WirtschaftsFeldGeltung", int] = {}
_TYP_MAP: dict["WirtschaftsFeldGeltung", "WirtschaftsFeldTyp"] = {}
_PROZEDUR_MAP: dict["WirtschaftsFeldGeltung", "WirtschaftsFeldProzedur"] = {}
_GELTUNG_MAP: dict[PolitikVerfassungsGeltung, "WirtschaftsFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WirtschaftsFeldGeltung.GESPERRT: 0.0,
        WirtschaftsFeldGeltung.WIRTSCHAFTLICH: 0.05,
        WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        WirtschaftsFeldGeltung.GESPERRT: 0,
        WirtschaftsFeldGeltung.WIRTSCHAFTLICH: 1,
        WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        WirtschaftsFeldGeltung.GESPERRT: WirtschaftsFeldTyp.SCHUTZ_WIRTSCHAFT,
        WirtschaftsFeldGeltung.WIRTSCHAFTLICH: WirtschaftsFeldTyp.ORDNUNGS_WIRTSCHAFT,
        WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: WirtschaftsFeldTyp.SOUVERAENITAETS_WIRTSCHAFT,
    })
    _PROZEDUR_MAP.update({
        WirtschaftsFeldGeltung.GESPERRT: WirtschaftsFeldProzedur.NOTPROZEDUR,
        WirtschaftsFeldGeltung.WIRTSCHAFTLICH: WirtschaftsFeldProzedur.REGELPROTOKOLL,
        WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: WirtschaftsFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        PolitikVerfassungsGeltung.GESPERRT: WirtschaftsFeldGeltung.GESPERRT,
        PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN: WirtschaftsFeldGeltung.WIRTSCHAFTLICH,
        PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN: WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH,
    })


class WirtschaftsFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    WIRTSCHAFTLICH = "wirtschaftlich"
    GRUNDLEGEND_WIRTSCHAFTLICH = "grundlegend-wirtschaftlich"


class WirtschaftsFeldTyp(Enum):
    SCHUTZ_WIRTSCHAFT = "schutz-wirtschaft"
    ORDNUNGS_WIRTSCHAFT = "ordnungs-wirtschaft"
    SOUVERAENITAETS_WIRTSCHAFT = "souveraenitaets-wirtschaft"


class WirtschaftsFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class WirtschaftsFeldNorm:
    wirtschafts_feld_id: str
    wirtschafts_typ: WirtschaftsFeldTyp
    prozedur: WirtschaftsFeldProzedur
    geltung: WirtschaftsFeldGeltung
    wirtschafts_weight: float
    wirtschafts_tier: int
    canonical: bool
    wirtschafts_ids: tuple[str, ...]
    wirtschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class WirtschaftsFeld:
    feld_id: str
    politik_verfassung: PolitikVerfassung
    normen: tuple[WirtschaftsFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirtschafts_feld_id for n in self.normen if n.geltung is WirtschaftsFeldGeltung.GESPERRT)

    @property
    def wirtschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirtschafts_feld_id for n in self.normen if n.geltung is WirtschaftsFeldGeltung.WIRTSCHAFTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirtschafts_feld_id for n in self.normen if n.geltung is WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH)

    @property
    def feld_signal(self):
        if any(n.geltung is WirtschaftsFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is WirtschaftsFeldGeltung.WIRTSCHAFTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-wirtschaftlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-wirtschaftlich")


_init_map()


def build_wirtschafts_feld(
    politik_verfassung: PolitikVerfassung | None = None,
    *,
    feld_id: str = "wirtschafts-feld",
) -> WirtschaftsFeld:
    if politik_verfassung is None:
        politik_verfassung = build_politik_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[WirtschaftsFeldNorm] = []
    for parent_norm in politik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.politik_verfassung_id.removeprefix(f'{politik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.politik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.politik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH)
        normen.append(
            WirtschaftsFeldNorm(
                wirtschafts_feld_id=new_id,
                wirtschafts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                wirtschafts_weight=new_weight,
                wirtschafts_tier=new_tier,
                canonical=is_canonical,
                wirtschafts_ids=parent_norm.politik_ids + (new_id,),
                wirtschafts_tags=parent_norm.politik_tags + (f"wirtschafts-feld:{new_geltung.value}",),
            )
        )
    return WirtschaftsFeld(
        feld_id=feld_id,
        politik_verfassung=politik_verfassung,
        normen=tuple(normen),
    )
