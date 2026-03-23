"""
#570 MedienVerfassung — McLuhan/Habermas/Luhmann Medienwissenschaft Verfassung (Block-Krone ⭐)

Marshall McLuhan (1964): Understanding Media — Das Medium ist die Botschaft als
  medientheoretische Grundformel; Tetrade der Medieneffekte (Enhancement/Obsolescence/
  Retrieval/Reversal); elektrisches Licht als reines Medium; globales Dorf als
  vernetzte Wahrnehmungsgemeinschaft; Medien als Verfassungsgrundlage des
  Peta-Schwarms Leitstern.
Jürgen Habermas (1981): Theorie des kommunikativen Handelns — ideale Sprechsituation
  als Verfassungsideal kommunikativer Rationalität; Diskursprinzip als Grundnorm;
  kommunikative Macht als demokratische Souveränität; Öffentlichkeit als
  Kommunikationsverfassung; Vernunft als intersubjektives Verfahren des
  Peta-Schwarms Leitstern.
Niklas Luhmann (1984): Soziale Systeme — Kommunikation als autopoietische Grundeinheit;
  symbolisch generalisierte Kommunikationsmedien als Evolutionserrungenschaft;
  Gesellschaft als umfassendes Kommunikationssystem; Systemdifferenzierung durch
  Kommunikationsmedien; operative Schließung als Verfassungsprinzip Leitsterns. 🌐⭐
Parent: KommunikativeHandlungsCharta (#569)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kommunikative_handlungs_charta import (
    KommunikativeHandlungsCharta,
    KommunikativeHandlungsChartaGeltung,
    build_kommunikative_handlungs_charta,
)

_WEIGHT_DELTA: dict["MedienVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["MedienVerfassungsGeltung", int] = {}
_TYP_MAP: dict["MedienVerfassungsGeltung", "MedienVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["MedienVerfassungsGeltung", "MedienVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[KommunikativeHandlungsChartaGeltung, "MedienVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MedienVerfassungsGeltung.GESPERRT: 0.0,
        MedienVerfassungsGeltung.MEDIEN_SOUVERAEN: 0.05,
        MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        MedienVerfassungsGeltung.GESPERRT: 0,
        MedienVerfassungsGeltung.MEDIEN_SOUVERAEN: 1,
        MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        MedienVerfassungsGeltung.GESPERRT: MedienVerfassungsTyp.SCHUTZ_MEDIENVERFASSUNG,
        MedienVerfassungsGeltung.MEDIEN_SOUVERAEN: MedienVerfassungsTyp.ORDNUNGS_MEDIENVERFASSUNG,
        MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN: MedienVerfassungsTyp.SOUVERAENITAETS_MEDIENVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        MedienVerfassungsGeltung.GESPERRT: MedienVerfassungsProzedur.NOTPROZEDUR,
        MedienVerfassungsGeltung.MEDIEN_SOUVERAEN: MedienVerfassungsProzedur.REGELPROTOKOLL,
        MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN: MedienVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KommunikativeHandlungsChartaGeltung.GESPERRT: MedienVerfassungsGeltung.GESPERRT,
        KommunikativeHandlungsChartaGeltung.KOMMUNIKATIV_HANDELND: MedienVerfassungsGeltung.MEDIEN_SOUVERAEN,
        KommunikativeHandlungsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV_HANDELND: MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN,
    })


class MedienVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    MEDIEN_SOUVERAEN = "medien-souveraen"
    GRUNDLEGEND_MEDIEN_SOUVERAEN = "grundlegend-medien-souveraen"


class MedienVerfassungsTyp(Enum):
    SCHUTZ_MEDIENVERFASSUNG = "schutz-medienverfassung"
    ORDNUNGS_MEDIENVERFASSUNG = "ordnungs-medienverfassung"
    SOUVERAENITAETS_MEDIENVERFASSUNG = "souveraenitaets-medienverfassung"


class MedienVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class MedienVerfassungsNorm:
    medien_verfassung_id: str
    medien_typ: MedienVerfassungsTyp
    prozedur: MedienVerfassungsProzedur
    geltung: MedienVerfassungsGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class MedienVerfassung:
    verfassung_id: str
    kommunikative_handlungs_charta: KommunikativeHandlungsCharta
    normen: tuple[MedienVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.medien_verfassung_id for n in self.normen if n.geltung is MedienVerfassungsGeltung.GESPERRT)

    @property
    def medien_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.medien_verfassung_id for n in self.normen if n.geltung is MedienVerfassungsGeltung.MEDIEN_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.medien_verfassung_id for n in self.normen if n.geltung is MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is MedienVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is MedienVerfassungsGeltung.MEDIEN_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-medien-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-medien-souveraen")


_init_map()


def build_medien_verfassung(
    kommunikative_handlungs_charta: KommunikativeHandlungsCharta | None = None,
    *,
    verfassung_id: str = "medien-verfassung",
) -> MedienVerfassung:
    if kommunikative_handlungs_charta is None:
        kommunikative_handlungs_charta = build_kommunikative_handlungs_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[MedienVerfassungsNorm] = []
    for parent_norm in kommunikative_handlungs_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kommunikative_handlungs_charta_id.removeprefix(f'{kommunikative_handlungs_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN)
        normen.append(
            MedienVerfassungsNorm(
                medien_verfassung_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"medien-verfassung:{new_geltung.value}",),
            )
        )
    return MedienVerfassung(
        verfassung_id=verfassung_id,
        kommunikative_handlungs_charta=kommunikative_handlungs_charta,
        normen=tuple(normen),
    )
