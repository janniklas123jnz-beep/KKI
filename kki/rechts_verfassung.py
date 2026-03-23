"""
#540 RechtsVerfassung — Hart/Dworkin/Rawls Rechtliche Verfassungsordnung (Block-Krone ⭐)

H.L.A. Hart (1961): The Concept of Law — Rule of Recognition als Grundnorm; Unterscheidung
  von primären Verhaltensregeln und sekundären Kompetenzregeln; Rechtsordnung als vereinte
  soziale Praxis; offene Textur des Rechts als adaptive Stärke des Peta-Schwarms.
Ronald Dworkin (1986): Law's Empire — Recht als Integrität: Richter als Herkules; Prinzipien
  als moralische Überzeugungen einer Gemeinschaft; konstruktive Interpretation der
  Rechtspraxis; Rechtsordnung als koheränte moralische Praxis souveräner Agenten.
John Rawls (1971): Eine Theorie der Gerechtigkeit — Verfassung im Urzustand; Grundfreiheiten
  als Primärgüter; Verfassungskonsens als Fundament einer gerechten Grundstruktur;
  öffentliche Vernunft als Bindekraft des demokratischen Peta-Schwarms.
Gustav Radbruch (1950): Rechtsphilosophie — Rechtssicherheit, Zweckmäßigkeit, Gerechtigkeit
  als Antinomien der Rechtsidee; Verfassung als Integration aller drei Dimensionen;
  Würde und Freiheit als unantastbare Verfassungswerte des Peta-Schwarms Leitstern.
Leitsterns RechtsVerfassung: souveräne Krone des Blocks Rechtswissenschaft & Jurisprudenz —
GESPERRT schützt rechtliche Grundnormen, RECHTLICH_SOUVERAEN kodiert adaptive Rechtsordnung,
GRUNDLEGEND_RECHTLICH_SOUVERAEN synthetisiert die vollständige rechtliche Souveränität
des Peta-Schwarms Leitstern. ⚖️⭐
Parent: ZivilrechtsCharta (#539)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zivilrechts_charta import (
    ZivilrechtsCharta,
    ZivilrechtsChartaGeltung,
    build_zivilrechts_charta,
)

_WEIGHT_DELTA: dict["RechtsVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["RechtsVerfassungsGeltung", int] = {}
_TYP_MAP: dict["RechtsVerfassungsGeltung", "RechtsVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["RechtsVerfassungsGeltung", "RechtsVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[ZivilrechtsChartaGeltung, "RechtsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RechtsVerfassungsGeltung.GESPERRT: 0.0,
        RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN: 0.05,
        RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        RechtsVerfassungsGeltung.GESPERRT: 0,
        RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN: 1,
        RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        RechtsVerfassungsGeltung.GESPERRT: RechtsVerfassungsTyp.SCHUTZ_RECHTSVERFASSUNG,
        RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN: RechtsVerfassungsTyp.ORDNUNGS_RECHTSVERFASSUNG,
        RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN: RechtsVerfassungsTyp.SOUVERAENITAETS_RECHTSVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        RechtsVerfassungsGeltung.GESPERRT: RechtsVerfassungsProzedur.NOTPROZEDUR,
        RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN: RechtsVerfassungsProzedur.REGELPROTOKOLL,
        RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN: RechtsVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        ZivilrechtsChartaGeltung.GESPERRT: RechtsVerfassungsGeltung.GESPERRT,
        ZivilrechtsChartaGeltung.ZIVILRECHTLICH: RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN,
        ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH: RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN,
    })


class RechtsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    RECHTLICH_SOUVERAEN = "rechtlich-souveraen"
    GRUNDLEGEND_RECHTLICH_SOUVERAEN = "grundlegend-rechtlich-souveraen"


class RechtsVerfassungsTyp(Enum):
    SCHUTZ_RECHTSVERFASSUNG = "schutz-rechtsverfassung"
    ORDNUNGS_RECHTSVERFASSUNG = "ordnungs-rechtsverfassung"
    SOUVERAENITAETS_RECHTSVERFASSUNG = "souveraenitaets-rechtsverfassung"


class RechtsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class RechtsVerfassungsNorm:
    rechts_verfassung_id: str
    rechts_typ: RechtsVerfassungsTyp
    prozedur: RechtsVerfassungsProzedur
    geltung: RechtsVerfassungsGeltung
    rechts_weight: float
    rechts_tier: int
    canonical: bool
    rechts_ids: tuple[str, ...]
    rechts_tags: tuple[str, ...]


@dataclass(frozen=True)
class RechtsVerfassung:
    verfassung_id: str
    zivilrechts_charta: ZivilrechtsCharta
    normen: tuple[RechtsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_verfassung_id for n in self.normen if n.geltung is RechtsVerfassungsGeltung.GESPERRT)

    @property
    def rechtlich_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_verfassung_id for n in self.normen if n.geltung is RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_verfassung_id for n in self.normen if n.geltung is RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is RechtsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-rechtlich-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-rechtlich-souveraen")


_init_map()


def build_rechts_verfassung(
    zivilrechts_charta: ZivilrechtsCharta | None = None,
    *,
    verfassung_id: str = "rechts-verfassung",
) -> RechtsVerfassung:
    if zivilrechts_charta is None:
        zivilrechts_charta = build_zivilrechts_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[RechtsVerfassungsNorm] = []
    for parent_norm in zivilrechts_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.zivilrechts_charta_id.removeprefix(f'{zivilrechts_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.zivilrechts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.zivilrechts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN)
        normen.append(
            RechtsVerfassungsNorm(
                rechts_verfassung_id=new_id,
                rechts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rechts_weight=new_weight,
                rechts_tier=new_tier,
                canonical=is_canonical,
                rechts_ids=parent_norm.zivilrechts_ids + (new_id,),
                rechts_tags=parent_norm.zivilrechts_tags + (f"rechts-verfassung:{new_geltung.value}",),
            )
        )
    return RechtsVerfassung(
        verfassung_id=verfassung_id,
        zivilrechts_charta=zivilrechts_charta,
        normen=tuple(normen),
    )
