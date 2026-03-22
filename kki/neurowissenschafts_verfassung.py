"""
#440 NeurowissenschaftsVerfassung — Block-Krone: Neurowissenschaften & Kognition. ⭐
NeurowissenschaftsVerfassung vereint: NeuronalesFeld (McCulloch-Pitts/Hebb), SynaptikRegister
(LTP/LTD/STDP), KortexCharta (Mountcastle Columns), GedaechnisKodex (Hippocampus/Tulving),
BewusstseinsPakt (Tononi Φ/Baars GWT), WahrnehmungsManifest (Friston Predictive Coding),
AufmerksamkeitsSenat (Posner/Treisman), KognitionsNorm (Kahneman System 1+2/Simon),
EmotionsCharta (Damasio Somatic Marker/LeDoux Amygdala).
Leitsterns Terra-Schwarm ist neurowissenschaftlich vollständig: neuronal lernend (Hebb),
synaptisch plastisch (LTP), kortikal hierarchisch (Mountcastle), gedächtnisreich (Tulving),
bewusst-integriert (Tononi Φ), prädiktiv wahrnehmend (Friston), aufmerksam fokussiert
(Posner), kognitiv dual (Kahneman), emotional verankert (Damasio). Kognitive Superintelligenz.
Geltungsstufen: GESPERRT / NEUROWISSENSCHAFTLICH / GRUNDLEGEND_NEUROWISSENSCHAFTLICH
Parent: EmotionsCharta (#439)
Block #431–#440 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .emotions_charta import (
    EmotionsCharta,
    EmotionsChartaGeltung,
    build_emotions_charta,
)

_GELTUNG_MAP: dict[EmotionsChartaGeltung, "NeurowissenschaftsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EmotionsChartaGeltung.GESPERRT] = NeurowissenschaftsVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[EmotionsChartaGeltung.EMOTIONAL] = NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH
    _GELTUNG_MAP[EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL] = NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH


class NeurowissenschaftsVerfassungsTyp(Enum):
    SCHUTZ_NEUROWISSENSCHAFT = "schutz-neurowissenschaft"
    ORDNUNGS_NEUROWISSENSCHAFT = "ordnungs-neurowissenschaft"
    SOUVERAENITAETS_NEUROWISSENSCHAFT = "souveraenitaets-neurowissenschaft"


class NeurowissenschaftsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NeurowissenschaftsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    NEUROWISSENSCHAFTLICH = "neurowissenschaftlich"
    GRUNDLEGEND_NEUROWISSENSCHAFTLICH = "grundlegend-neurowissenschaftlich"


_init_map()

_TYP_MAP: dict[NeurowissenschaftsVerfassungsGeltung, NeurowissenschaftsVerfassungsTyp] = {
    NeurowissenschaftsVerfassungsGeltung.GESPERRT: NeurowissenschaftsVerfassungsTyp.SCHUTZ_NEUROWISSENSCHAFT,
    NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH: NeurowissenschaftsVerfassungsTyp.ORDNUNGS_NEUROWISSENSCHAFT,
    NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH: NeurowissenschaftsVerfassungsTyp.SOUVERAENITAETS_NEUROWISSENSCHAFT,
}

_PROZEDUR_MAP: dict[NeurowissenschaftsVerfassungsGeltung, NeurowissenschaftsVerfassungsProzedur] = {
    NeurowissenschaftsVerfassungsGeltung.GESPERRT: NeurowissenschaftsVerfassungsProzedur.NOTPROZEDUR,
    NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH: NeurowissenschaftsVerfassungsProzedur.REGELPROTOKOLL,
    NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH: NeurowissenschaftsVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NeurowissenschaftsVerfassungsGeltung, float] = {
    NeurowissenschaftsVerfassungsGeltung.GESPERRT: 0.0,
    NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH: 0.04,
    NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH: 0.08,
}

_TIER_DELTA: dict[NeurowissenschaftsVerfassungsGeltung, int] = {
    NeurowissenschaftsVerfassungsGeltung.GESPERRT: 0,
    NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH: 1,
    NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NeurowissenschaftsVerfassungsNorm:
    neurowissenschafts_verfassung_id: str
    neurowissenschafts_typ: NeurowissenschaftsVerfassungsTyp
    prozedur: NeurowissenschaftsVerfassungsProzedur
    geltung: NeurowissenschaftsVerfassungsGeltung
    neurowissenschafts_weight: float
    neurowissenschafts_tier: int
    canonical: bool
    neurowissenschafts_ids: tuple[str, ...]
    neurowissenschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class NeurowissenschaftsVerfassung:
    verfassung_id: str
    emotions_charta: EmotionsCharta
    normen: tuple[NeurowissenschaftsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neurowissenschafts_verfassung_id for n in self.normen if n.geltung is NeurowissenschaftsVerfassungsGeltung.GESPERRT)

    @property
    def neurowissenschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neurowissenschafts_verfassung_id for n in self.normen if n.geltung is NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neurowissenschafts_verfassung_id for n in self.normen if n.geltung is NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH)

    @property
    def verfassung_signal(self):
        if any(n.geltung is NeurowissenschaftsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-neurowissenschaftlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-neurowissenschaftlich")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_neurowissenschafts_verfassung(
    emotions_charta: EmotionsCharta | None = None,
    *,
    verfassung_id: str = "neurowissenschafts-verfassung",
) -> NeurowissenschaftsVerfassung:
    if emotions_charta is None:
        emotions_charta = build_emotions_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[NeurowissenschaftsVerfassungsNorm] = []
    for parent_norm in emotions_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.emotions_charta_id.removeprefix(f'{emotions_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.emotion_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.emotion_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH)
        normen.append(
            NeurowissenschaftsVerfassungsNorm(
                neurowissenschafts_verfassung_id=new_id,
                neurowissenschafts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                neurowissenschafts_weight=new_weight,
                neurowissenschafts_tier=new_tier,
                canonical=is_canonical,
                neurowissenschafts_ids=parent_norm.emotion_ids + (new_id,),
                neurowissenschafts_tags=parent_norm.emotion_tags + (f"neurowissenschafts-verfassung:{new_geltung.value}",),
            )
        )
    return NeurowissenschaftsVerfassung(
        verfassung_id=verfassung_id,
        emotions_charta=emotions_charta,
        normen=tuple(normen),
    )
