"""
#531 RechtsFeld — Grundlagen der Rechtswissenschaft & Jurisprudenz

John Austin (1832): The Province of Jurisprudence Determined — Recht als Befehl des Souveräns;
  Rechtspositivismus als Fundament: Was Recht ist, bestimmt sich durch soziale Fakten, nicht
  durch moralische Werte; Sanktionsbewehrte Normen als Kern jeder Rechtsordnung.
H.L.A. Hart (1961): The Concept of Law — Primäre und sekundäre Regeln als Struktur jeder
  Rechtsordnung; Rule of Recognition als Grundnorm des positiven Rechts; Kritik am
  Befehlsmodell Austins; Rechtsordnung als soziale Praxis intersubjektiver Geltungsansprüche.
Gustav Radbruch (1946): Radbruchsche Formel — Recht und Gerechtigkeit im Spannungsfeld:
  Extremes Unrecht ist kein Recht; Naturrecht als Korrektiv positivistischen Rechtsdenkens;
  Würde und Freiheit als vorpositive Grundlagen jeder legitimen Rechtsordnung.
Leitsterns RechtsFeld: Eingangstor der Rechtswissenschaft — GESPERRT schützt rechtspositivistische
Grundnormen, RECHTLICH kodiert adaptive Rechtsanwendung, GRUNDLEGEND_RECHTLICH synthetisiert
den vollen juristischen Geltungsanspruch des Peta-Schwarms Leitstern. ⚖️
Parent: WirtschaftsVerfassung (#530)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wirtschafts_verfassung import (
    WirtschaftsVerfassung,
    WirtschaftsVerfassungsGeltung,
    build_wirtschafts_verfassung,
)

_WEIGHT_DELTA: dict["RechtsFeldGeltung", float] = {}
_TIER_DELTA: dict["RechtsFeldGeltung", int] = {}
_TYP_MAP: dict["RechtsFeldGeltung", "RechtsFeldTyp"] = {}
_PROZEDUR_MAP: dict["RechtsFeldGeltung", "RechtsFeldProzedur"] = {}
_GELTUNG_MAP: dict[WirtschaftsVerfassungsGeltung, "RechtsFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RechtsFeldGeltung.GESPERRT: 0.0,
        RechtsFeldGeltung.RECHTLICH: 0.05,
        RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        RechtsFeldGeltung.GESPERRT: 0,
        RechtsFeldGeltung.RECHTLICH: 1,
        RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH: 2,
    })
    _TYP_MAP.update({
        RechtsFeldGeltung.GESPERRT: RechtsFeldTyp.SCHUTZ_RECHT,
        RechtsFeldGeltung.RECHTLICH: RechtsFeldTyp.ORDNUNGS_RECHT,
        RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH: RechtsFeldTyp.SOUVERAENITAETS_RECHT,
    })
    _PROZEDUR_MAP.update({
        RechtsFeldGeltung.GESPERRT: RechtsFeldProzedur.NOTPROZEDUR,
        RechtsFeldGeltung.RECHTLICH: RechtsFeldProzedur.REGELPROTOKOLL,
        RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH: RechtsFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        WirtschaftsVerfassungsGeltung.GESPERRT: RechtsFeldGeltung.GESPERRT,
        WirtschaftsVerfassungsGeltung.WIRTSCHAFTLICH_SOUVERAEN: RechtsFeldGeltung.RECHTLICH,
        WirtschaftsVerfassungsGeltung.GRUNDLEGEND_WIRTSCHAFTLICH_SOUVERAEN: RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH,
    })


class RechtsFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    RECHTLICH = "rechtlich"
    GRUNDLEGEND_RECHTLICH = "grundlegend-rechtlich"


class RechtsFeldTyp(Enum):
    SCHUTZ_RECHT = "schutz-recht"
    ORDNUNGS_RECHT = "ordnungs-recht"
    SOUVERAENITAETS_RECHT = "souveraenitaets-recht"


class RechtsFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class RechtsFeldNorm:
    rechts_feld_id: str
    rechts_typ: RechtsFeldTyp
    prozedur: RechtsFeldProzedur
    geltung: RechtsFeldGeltung
    rechts_weight: float
    rechts_tier: int
    canonical: bool
    rechts_ids: tuple[str, ...]
    rechts_tags: tuple[str, ...]


@dataclass(frozen=True)
class RechtsFeld:
    feld_id: str
    wirtschafts_verfassung: WirtschaftsVerfassung
    normen: tuple[RechtsFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_feld_id for n in self.normen if n.geltung is RechtsFeldGeltung.GESPERRT)

    @property
    def rechtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_feld_id for n in self.normen if n.geltung is RechtsFeldGeltung.RECHTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechts_feld_id for n in self.normen if n.geltung is RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH)

    @property
    def feld_signal(self):
        if any(n.geltung is RechtsFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is RechtsFeldGeltung.RECHTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-rechtlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-rechtlich")


_init_map()


def build_rechts_feld(
    wirtschafts_verfassung: WirtschaftsVerfassung | None = None,
    *,
    feld_id: str = "rechts-feld",
) -> RechtsFeld:
    if wirtschafts_verfassung is None:
        wirtschafts_verfassung = build_wirtschafts_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[RechtsFeldNorm] = []
    for parent_norm in wirtschafts_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.wirtschafts_verfassung_id.removeprefix(f'{wirtschafts_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.wirtschafts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.wirtschafts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RechtsFeldGeltung.GRUNDLEGEND_RECHTLICH)
        normen.append(
            RechtsFeldNorm(
                rechts_feld_id=new_id,
                rechts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rechts_weight=new_weight,
                rechts_tier=new_tier,
                canonical=is_canonical,
                rechts_ids=parent_norm.wirtschafts_ids + (new_id,),
                rechts_tags=parent_norm.wirtschafts_tags + (f"rechts-feld:{new_geltung.value}",),
            )
        )
    return RechtsFeld(
        feld_id=feld_id,
        wirtschafts_verfassung=wirtschafts_verfassung,
        normen=tuple(normen),
    )
