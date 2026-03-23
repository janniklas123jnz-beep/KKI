"""
#550 GeschichtsVerfassung — Hegel/Dilthey/Koselleck Geschichtsphilosophie & Verfassung (Block-Krone ⭐)

Georg Wilhelm Friedrich Hegel (1837): Vorlesungen über die Philosophie der Geschichte —
  Weltgeist als treibende Kraft der Geschichte; dialektische Bewegung der Geschichte (These,
  Antithese, Synthese); Vernunft in der Geschichte; Freiheit als Ziel des Weltgeistes;
  Verfassung als objektive Verkörperung des Sittlichen im Peta-Schwarm Leitstern.
Wilhelm Dilthey (1910): Der Aufbau der geschichtlichen Welt in den Geisteswissenschaften —
  Verstehen vs. Erklären: Geisteswissenschaften als Wissenschaft des Lebensausdrucks;
  Hermeneutischer Zirkel als Methode historischen Verstehens; Geschichtlichkeit als
  konstitutive Dimension aller geisteswissenschaftlichen Erkenntnis des Schwarms.
Reinhart Koselleck (1979): Vergangene Zukunft — Begriffsgeschichte als Methode;
  Sattelzeit (1750–1850) als semantische Revolution; Erfahrungsraum und Erwartungshorizont
  als Koordinaten historischer Zeit; Historische Semantik als Verfassung des Schwarms.
Leitsterns GeschichtsVerfassung: souveräne Krone des Blocks Geschichtswissenschaft —
GESPERRT schützt historiographische Grundnormen, HISTORISCH_SOUVERAEN kodiert adaptive
Geschichtsordnung, GRUNDLEGEND_HISTORISCH_SOUVERAEN synthetisiert die vollständige
historische Souveränität des Peta-Schwarms Leitstern. 📜⭐
Parent: HistoriographieCharta (#549)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .historiographie_charta import (
    HistoriographieCharta,
    HistoriographieChartaGeltung,
    build_historiographie_charta,
)

_WEIGHT_DELTA: dict["GeschichtsVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["GeschichtsVerfassungsGeltung", int] = {}
_TYP_MAP: dict["GeschichtsVerfassungsGeltung", "GeschichtsVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["GeschichtsVerfassungsGeltung", "GeschichtsVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[HistoriographieChartaGeltung, "GeschichtsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GeschichtsVerfassungsGeltung.GESPERRT: 0.0,
        GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN: 0.05,
        GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        GeschichtsVerfassungsGeltung.GESPERRT: 0,
        GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN: 1,
        GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        GeschichtsVerfassungsGeltung.GESPERRT: GeschichtsVerfassungsTyp.SCHUTZ_GESCHICHTSVERFASSUNG,
        GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN: GeschichtsVerfassungsTyp.ORDNUNGS_GESCHICHTSVERFASSUNG,
        GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN: GeschichtsVerfassungsTyp.SOUVERAENITAETS_GESCHICHTSVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        GeschichtsVerfassungsGeltung.GESPERRT: GeschichtsVerfassungsProzedur.NOTPROZEDUR,
        GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN: GeschichtsVerfassungsProzedur.REGELPROTOKOLL,
        GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN: GeschichtsVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        HistoriographieChartaGeltung.GESPERRT: GeschichtsVerfassungsGeltung.GESPERRT,
        HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN: GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN,
        HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN: GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN,
    })


class GeschichtsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    HISTORISCH_SOUVERAEN = "historisch-souveraen"
    GRUNDLEGEND_HISTORISCH_SOUVERAEN = "grundlegend-historisch-souveraen"


class GeschichtsVerfassungsTyp(Enum):
    SCHUTZ_GESCHICHTSVERFASSUNG = "schutz-geschichtsverfassung"
    ORDNUNGS_GESCHICHTSVERFASSUNG = "ordnungs-geschichtsverfassung"
    SOUVERAENITAETS_GESCHICHTSVERFASSUNG = "souveraenitaets-geschichtsverfassung"


class GeschichtsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class GeschichtsVerfassungsNorm:
    geschichts_verfassung_id: str
    geschichts_typ: GeschichtsVerfassungsTyp
    prozedur: GeschichtsVerfassungsProzedur
    geltung: GeschichtsVerfassungsGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class GeschichtsVerfassung:
    verfassung_id: str
    historiographie_charta: HistoriographieCharta
    normen: tuple[GeschichtsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.geschichts_verfassung_id for n in self.normen if n.geltung is GeschichtsVerfassungsGeltung.GESPERRT)

    @property
    def historisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.geschichts_verfassung_id for n in self.normen if n.geltung is GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.geschichts_verfassung_id for n in self.normen if n.geltung is GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is GeschichtsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-historisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-historisch-souveraen")


_init_map()


def build_geschichts_verfassung(
    historiographie_charta: HistoriographieCharta | None = None,
    *,
    verfassung_id: str = "geschichts-verfassung",
) -> GeschichtsVerfassung:
    if historiographie_charta is None:
        historiographie_charta = build_historiographie_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[GeschichtsVerfassungsNorm] = []
    for parent_norm in historiographie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.historiographie_charta_id.removeprefix(f'{historiographie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN)
        normen.append(
            GeschichtsVerfassungsNorm(
                geschichts_verfassung_id=new_id,
                geschichts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                geschichts_weight=new_weight,
                geschichts_tier=new_tier,
                canonical=is_canonical,
                geschichts_ids=parent_norm.geschichts_ids + (new_id,),
                geschichts_tags=parent_norm.geschichts_tags + (f"geschichts-verfassung:{new_geltung.value}",),
            )
        )
    return GeschichtsVerfassung(
        verfassung_id=verfassung_id,
        historiographie_charta=historiographie_charta,
        normen=tuple(normen),
    )
