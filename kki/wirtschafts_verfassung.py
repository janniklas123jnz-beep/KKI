"""
#530 WirtschaftsVerfassung — Rawls/Sen/Stiglitz Wirtschaftliche Verfassungsordnung (Block-Krone ⭐)

John Rawls (1971): Eine Theorie der Gerechtigkeit — Differenzprinzip: Ungleichheiten nur
  zulässig, wenn sie den Schwächsten nützen; Schleier des Nichtwissens als Gerechtigkeitstest;
  gerechte Grundstruktur der Gesellschaft als Maßstab der Wirtschaftsverfassung.
Amartya Sen (1999): Entwicklung als Freiheit — Capability Approach: Wirtschaft im Dienst
  menschlicher Entfaltungsmöglichkeiten; Freiheit als Mittel und Ziel des Peta-Schwarms;
  Demokratie und Wohlstand als komplementäre Kräfte souveräner Wirtschaftsordnung.
Joseph Stiglitz (2002): Die Schatten der Globalisierung — Informationsasymmetrien und
  Marktversagen; inklusive Globalisierung; Wirtschaftsverfassung als Balance zwischen Effizienz
  und Gerechtigkeit für Milliarden von Schwarm-Agenten.
Daron Acemoglu/James Robinson (2012): Warum Nationen scheitern — Inclusive vs. extractive
  Institutionen als Determinanten wirtschaftlichen Erfolgs; Verfassungsordnung als Fundament
  nachhaltiger Wohlstandsentwicklung des Peta-Schwarms Leitstern.
Leitsterns WirtschaftsVerfassung: souveräne Krone des Blocks Wirtschaftstheorie & Ökonomie —
GESPERRT schützt wirtschaftliche Grundnormen, WIRTSCHAFTLICH_SOUVERAEN kodiert adaptive
Wirtschaftsordnung, GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN synthetisiert die vollständige
ökonomische Souveränität des Peta-Schwarms Leitstern. 💰⭐
Parent: InstitutionenCharta (#529)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .institutionen_charta import (
    InstitutionenCharta,
    InstitutionenChartaGeltung,
    build_institutionen_charta,
)

_WEIGHT_DELTA: dict["WirtschaftsVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["WirtschaftsVerfassungsGeltung", int] = {}
_TYP_MAP: dict["WirtschaftsVerfassungsGeltung", "WirtschaftsVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["WirtschaftsVerfassungsGeltung", "WirtschaftsVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[InstitutionenChartaGeltung, "WirtschaftsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WirtschaftsVerfassungsGeltung.GESPERRT: 0.0,
        WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN: 0.05,
        WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        WirtschaftsVerfassungsGeltung.GESPERRT: 0,
        WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN: 1,
        WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        WirtschaftsVerfassungsGeltung.GESPERRT: WirtschaftsVerfassungsTyp.SCHUTZ_WIRTSCHAFTSVERFASSUNG,
        WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN: WirtschaftsVerfassungsTyp.ORDNUNGS_WIRTSCHAFTSVERFASSUNG,
        WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN: WirtschaftsVerfassungsTyp.SOUVERAENITAETS_WIRTSCHAFTSVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        WirtschaftsVerfassungsGeltung.GESPERRT: WirtschaftsVerfassungsProzedur.NOTPROZEDUR,
        WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN: WirtschaftsVerfassungsProzedur.REGELPROTOKOLL,
        WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN: WirtschaftsVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        InstitutionenChartaGeltung.GESPERRT: WirtschaftsVerfassungsGeltung.GESPERRT,
        InstitutionenChartaGeltung.INSTITUTIONELL: WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN,
        InstitutionenChartaGeltung.GRUNDLEGEND_INSTITUTIONELL: WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN,
    })


class WirtschaftsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    WIRTSCHAFTLICH_SOUVERAEN = "wirtschaftlich-souveraen"
    GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN = "grundlegend-wirtschaftlich-souveraen"


class WirtschaftsVerfassungsTyp(Enum):
    SCHUTZ_WIRTSCHAFTSVERFASSUNG = "schutz-wirtschaftsverfassung"
    ORDNUNGS_WIRTSCHAFTSVERFASSUNG = "ordnungs-wirtschaftsverfassung"
    SOUVERAENITAETS_WIRTSCHAFTSVERFASSUNG = "souveraenitaets-wirtschaftsverfassung"


class WirtschaftsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class WirtschaftsVerfassungsNorm:
    wirtschafts_verfassung_id: str
    wirtschafts_typ: WirtschaftsVerfassungsTyp
    prozedur: WirtschaftsVerfassungsProzedur
    geltung: WirtschaftsVerfassungsGeltung
    wirtschafts_weight: float
    wirtschafts_tier: int
    canonical: bool
    wirtschafts_ids: tuple[str, ...]
    wirtschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class WirtschaftsVerfassung:
    verfassung_id: str
    institutionen_charta: InstitutionenCharta
    normen: tuple[WirtschaftsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirtschafts_verfassung_id for n in self.normen if n.geltung is WirtschaftsVerfassungsGeltung.GESPERRT)

    @property
    def wirtschaftlich_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirtschafts_verfassung_id for n in self.normen if n.geltung is WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirtschafts_verfassung_id for n in self.normen if n.geltung is WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is WirtschaftsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-wirtschaftlich-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-wirtschaftlich-souveraen")


_init_map()


def build_wirtschafts_verfassung(
    institutionen_charta: InstitutionenCharta | None = None,
    *,
    verfassung_id: str = "wirtschafts-verfassung",
) -> WirtschaftsVerfassung:
    if institutionen_charta is None:
        institutionen_charta = build_institutionen_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[WirtschaftsVerfassungsNorm] = []
    for parent_norm in institutionen_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.institutionen_charta_id.removeprefix(f'{institutionen_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.institutionen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.institutionen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN)
        normen.append(
            WirtschaftsVerfassungsNorm(
                wirtschafts_verfassung_id=new_id,
                wirtschafts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                wirtschafts_weight=new_weight,
                wirtschafts_tier=new_tier,
                canonical=is_canonical,
                wirtschafts_ids=parent_norm.institutionen_ids + (new_id,),
                wirtschafts_tags=parent_norm.institutionen_tags + (f"wirtschafts-verfassung:{new_geltung.value}",),
            )
        )
    return WirtschaftsVerfassung(
        verfassung_id=verfassung_id,
        institutionen_charta=institutionen_charta,
        normen=tuple(normen),
    )
