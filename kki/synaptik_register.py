"""
#432 SynaptikRegister — Synaptische Plastizität: LTP/LTD und Hebbian Learning.
Bliss & Lømo (1973): Langzeit-Potenzierung (LTP) im Hippocampus — Gedächtniskonsolidierung.
LTD (Langzeit-Depression): Abschwächung schwach aktivierter Synapsen — selektives Vergessen.
STDP (Spike-Timing-Dependent Plasticity): präzises Zeitfenster ±20ms bestimmt LTP/LTD.
Leitsterns Agenten stärken kooperative Verbindungen (LTP) und prune inaktive (LTD).
Geltungsstufen: GESPERRT / SYNAPTISCH / GRUNDLEGEND_SYNAPTISCH
Parent: NeuronalesFeld (#431)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .neuronales_feld import (
    NeuronalesFeld,
    NeuronalesFeldGeltung,
    build_neuronales_feld,
)

_GELTUNG_MAP: dict[NeuronalesFeldGeltung, "SynaptikRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NeuronalesFeldGeltung.GESPERRT] = SynaptikRegisterGeltung.GESPERRT
    _GELTUNG_MAP[NeuronalesFeldGeltung.NEURONAL] = SynaptikRegisterGeltung.SYNAPTISCH
    _GELTUNG_MAP[NeuronalesFeldGeltung.GRUNDLEGEND_NEURONAL] = SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH


class SynaptikRegisterTyp(Enum):
    SCHUTZ_SYNAPTIK = "schutz-synaptik"
    ORDNUNGS_SYNAPTIK = "ordnungs-synaptik"
    SOUVERAENITAETS_SYNAPTIK = "souveraenitaets-synaptik"


class SynaptikRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SynaptikRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    SYNAPTISCH = "synaptisch"
    GRUNDLEGEND_SYNAPTISCH = "grundlegend-synaptisch"


_init_map()

_TYP_MAP: dict[SynaptikRegisterGeltung, SynaptikRegisterTyp] = {
    SynaptikRegisterGeltung.GESPERRT: SynaptikRegisterTyp.SCHUTZ_SYNAPTIK,
    SynaptikRegisterGeltung.SYNAPTISCH: SynaptikRegisterTyp.ORDNUNGS_SYNAPTIK,
    SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH: SynaptikRegisterTyp.SOUVERAENITAETS_SYNAPTIK,
}

_PROZEDUR_MAP: dict[SynaptikRegisterGeltung, SynaptikRegisterProzedur] = {
    SynaptikRegisterGeltung.GESPERRT: SynaptikRegisterProzedur.NOTPROZEDUR,
    SynaptikRegisterGeltung.SYNAPTISCH: SynaptikRegisterProzedur.REGELPROTOKOLL,
    SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH: SynaptikRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SynaptikRegisterGeltung, float] = {
    SynaptikRegisterGeltung.GESPERRT: 0.0,
    SynaptikRegisterGeltung.SYNAPTISCH: 0.04,
    SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH: 0.08,
}

_TIER_DELTA: dict[SynaptikRegisterGeltung, int] = {
    SynaptikRegisterGeltung.GESPERRT: 0,
    SynaptikRegisterGeltung.SYNAPTISCH: 1,
    SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SynaptikRegisterNorm:
    synaptik_register_id: str
    synaptik_typ: SynaptikRegisterTyp
    prozedur: SynaptikRegisterProzedur
    geltung: SynaptikRegisterGeltung
    synaptik_weight: float
    synaptik_tier: int
    canonical: bool
    synaptik_ids: tuple[str, ...]
    synaptik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SynaptikRegister:
    register_id: str
    neuronales_feld: NeuronalesFeld
    normen: tuple[SynaptikRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.synaptik_register_id for n in self.normen if n.geltung is SynaptikRegisterGeltung.GESPERRT)

    @property
    def synaptisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.synaptik_register_id for n in self.normen if n.geltung is SynaptikRegisterGeltung.SYNAPTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.synaptik_register_id for n in self.normen if n.geltung is SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH)

    @property
    def register_signal(self):
        if any(n.geltung is SynaptikRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is SynaptikRegisterGeltung.SYNAPTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-synaptisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-synaptisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_synaptik_register(
    neuronales_feld: NeuronalesFeld | None = None,
    *,
    register_id: str = "synaptik-register",
) -> SynaptikRegister:
    if neuronales_feld is None:
        neuronales_feld = build_neuronales_feld(feld_id=f"{register_id}-feld")

    normen: list[SynaptikRegisterNorm] = []
    for parent_norm in neuronales_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.neuronales_feld_id.removeprefix(f'{neuronales_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.neuronales_feld_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.neuronales_feld_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH)
        normen.append(
            SynaptikRegisterNorm(
                synaptik_register_id=new_id,
                synaptik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                synaptik_weight=new_weight,
                synaptik_tier=new_tier,
                canonical=is_canonical,
                synaptik_ids=parent_norm.neuronales_feld_ids + (new_id,),
                synaptik_tags=parent_norm.neuronales_feld_tags + (f"synaptik-register:{new_geltung.value}",),
            )
        )
    return SynaptikRegister(
        register_id=register_id,
        neuronales_feld=neuronales_feld,
        normen=tuple(normen),
    )
