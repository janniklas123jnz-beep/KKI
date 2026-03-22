"""
#431 NeuronalesFeld — Neurowissenschaften: McCulloch-Pitts Neuron und Hebb-Lernregel.
McCulloch & Pitts (1943): erstes formales Neuronenmodell — binäre Schwellenwertfunktion.
Hebb (1949): "Neurons that fire together, wire together" — synaptisches Lernen als Basis.
Hodgkin & Huxley (1952): Ionenkanalmodell des Aktionspotenzials, Nobel 1963.
Leitsterns Agenten-Lernen ist biologisch-neuronal fundiert: Hebb + Aktivierungsschwellen.
Geltungsstufen: GESPERRT / NEURONAL / GRUNDLEGEND_NEURONAL
Parent: InformationsVerfassung (#430)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .informations_verfassung import (
    InformationsVerfassung,
    InformationsVerfassungsGeltung,
    build_informations_verfassung,
)

_GELTUNG_MAP: dict[InformationsVerfassungsGeltung, "NeuronalesFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[InformationsVerfassungsGeltung.GESPERRT] = NeuronalesFeldGeltung.GESPERRT
    _GELTUNG_MAP[InformationsVerfassungsGeltung.INFORMATIONSVERFASST] = NeuronalesFeldGeltung.NEURONAL
    _GELTUNG_MAP[InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST] = NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL


class NeuronalesFeldTyp(Enum):
    SCHUTZ_NEURON = "schutz-neuron"
    ORDNUNGS_NEURON = "ordnungs-neuron"
    SOUVERAENITAETS_NEURON = "souveraenitaets-neuron"


class NeuronalesFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NeuronalesFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    NEURONAL = "neuronal"
    GRUNDLEGEND_NEURONAL = "grundlegend-neuronal"


_init_map()

_TYP_MAP: dict[NeuronalesFeldGeltung, NeuronalesFeldTyp] = {
    NeuronalesFeldGeltung.GESPERRT: NeuronalesFeldTyp.SCHUTZ_NEURON,
    NeuronalesFeldGeltung.NEURONAL: NeuronalesFeldTyp.ORDNUNGS_NEURON,
    NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL: NeuronalesFeldTyp.SOUVERAENITAETS_NEURON,
}

_PROZEDUR_MAP: dict[NeuronalesFeldGeltung, NeuronalesFeldProzedur] = {
    NeuronalesFeldGeltung.GESPERRT: NeuronalesFeldProzedur.NOTPROZEDUR,
    NeuronalesFeldGeltung.NEURONAL: NeuronalesFeldProzedur.REGELPROTOKOLL,
    NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL: NeuronalesFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NeuronalesFeldGeltung, float] = {
    NeuronalesFeldGeltung.GESPERRT: 0.0,
    NeuronalesFeldGeltung.NEURONAL: 0.04,
    NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL: 0.08,
}

_TIER_DELTA: dict[NeuronalesFeldGeltung, int] = {
    NeuronalesFeldGeltung.GESPERRT: 0,
    NeuronalesFeldGeltung.NEURONAL: 1,
    NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NeuronalesFeldNorm:
    neuronales_feld_id: str
    neuronales_feld_typ: NeuronalesFeldTyp
    prozedur: NeuronalesFeldProzedur
    geltung: NeuronalesFeldGeltung
    neuronales_feld_weight: float
    neuronales_feld_tier: int
    canonical: bool
    neuronales_feld_ids: tuple[str, ...]
    neuronales_feld_tags: tuple[str, ...]


@dataclass(frozen=True)
class NeuronalesFeld:
    feld_id: str
    informations_verfassung: InformationsVerfassung
    normen: tuple[NeuronalesFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neuronales_feld_id for n in self.normen if n.geltung is NeuronalesFeldGeltung.GESPERRT)

    @property
    def neuronal_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neuronales_feld_id for n in self.normen if n.geltung is NeuronalesFeldGeltung.NEURONAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neuronales_feld_id for n in self.normen if n.geltung is NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL)

    @property
    def feld_signal(self):
        if any(n.geltung is NeuronalesFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is NeuronalesFeldGeltung.NEURONAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-neuronal")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-neuronal")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_neuronales_feld(
    informations_verfassung: InformationsVerfassung | None = None,
    *,
    feld_id: str = "neuronales-feld",
) -> NeuronalesFeld:
    if informations_verfassung is None:
        informations_verfassung = build_informations_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[NeuronalesFeldNorm] = []
    for parent_norm in informations_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.informations_verfassung_id.removeprefix(f'{informations_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.informations_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.informations_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL)
        normen.append(
            NeuronalesFeldNorm(
                neuronales_feld_id=new_id,
                neuronales_feld_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                neuronales_feld_weight=new_weight,
                neuronales_feld_tier=new_tier,
                canonical=is_canonical,
                neuronales_feld_ids=parent_norm.informations_verfassungs_ids + (new_id,),
                neuronales_feld_tags=parent_norm.informations_verfassungs_tags + (f"neuronales-feld:{new_geltung.value}",),
            )
        )
    return NeuronalesFeld(
        feld_id=feld_id,
        informations_verfassung=informations_verfassung,
        normen=tuple(normen),
    )
