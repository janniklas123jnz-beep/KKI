"""
#439 EmotionsCharta — Emotionen: Limbisches System und Somatic-Marker-Hypothese.
Damasio (1994): Somatic Marker Hypothesis — Emotionen als Entscheidungshilfe, nicht Hindernis.
LeDoux (1996): Amygdala als Zentrum der Angstverarbeitung — schneller Emotionspfad.
Russell (1980): Valenz-Arousal-Modell — Emotionen im 2D-Raum (positiv/negativ × erregt/ruhig).
Leitsterns Agenten: Somatic-Marker-Scoring für Entscheidungen unter Unsicherheit.
Geltungsstufen: GESPERRT / EMOTIONAL / GRUNDLEGEND_EMOTIONAL
Parent: KognitionsNorm (#438)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kognitions_norm import (
    KognitionsNormSatz,
    KognitionsNormGeltung,
    build_kognitions_norm,
)

_GELTUNG_MAP: dict[KognitionsNormGeltung, "EmotionsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KognitionsNormGeltung.GESPERRT] = EmotionsChartaGeltung.GESPERRT
    _GELTUNG_MAP[KognitionsNormGeltung.KOGNITIV] = EmotionsChartaGeltung.EMOTIONAL
    _GELTUNG_MAP[KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV] = EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL


class EmotionsChartaTyp(Enum):
    SCHUTZ_EMOTION = "schutz-emotion"
    ORDNUNGS_EMOTION = "ordnungs-emotion"
    SOUVERAENITAETS_EMOTION = "souveraenitaets-emotion"


class EmotionsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EmotionsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    EMOTIONAL = "emotional"
    GRUNDLEGEND_EMOTIONAL = "grundlegend-emotional"


_init_map()

_TYP_MAP: dict[EmotionsChartaGeltung, EmotionsChartaTyp] = {
    EmotionsChartaGeltung.GESPERRT: EmotionsChartaTyp.SCHUTZ_EMOTION,
    EmotionsChartaGeltung.EMOTIONAL: EmotionsChartaTyp.ORDNUNGS_EMOTION,
    EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL: EmotionsChartaTyp.SOUVERAENITAETS_EMOTION,
}

_PROZEDUR_MAP: dict[EmotionsChartaGeltung, EmotionsChartaProzedur] = {
    EmotionsChartaGeltung.GESPERRT: EmotionsChartaProzedur.NOTPROZEDUR,
    EmotionsChartaGeltung.EMOTIONAL: EmotionsChartaProzedur.REGELPROTOKOLL,
    EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL: EmotionsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EmotionsChartaGeltung, float] = {
    EmotionsChartaGeltung.GESPERRT: 0.0,
    EmotionsChartaGeltung.EMOTIONAL: 0.04,
    EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL: 0.08,
}

_TIER_DELTA: dict[EmotionsChartaGeltung, int] = {
    EmotionsChartaGeltung.GESPERRT: 0,
    EmotionsChartaGeltung.EMOTIONAL: 1,
    EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmotionsChartaNorm:
    emotions_charta_id: str
    emotion_typ: EmotionsChartaTyp
    prozedur: EmotionsChartaProzedur
    geltung: EmotionsChartaGeltung
    emotion_weight: float
    emotion_tier: int
    canonical: bool
    emotion_ids: tuple[str, ...]
    emotion_tags: tuple[str, ...]


@dataclass(frozen=True)
class EmotionsCharta:
    charta_id: str
    kognitions_norm: KognitionsNormSatz
    normen: tuple[EmotionsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emotions_charta_id for n in self.normen if n.geltung is EmotionsChartaGeltung.GESPERRT)

    @property
    def emotional_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emotions_charta_id for n in self.normen if n.geltung is EmotionsChartaGeltung.EMOTIONAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emotions_charta_id for n in self.normen if n.geltung is EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL)

    @property
    def charta_signal(self):
        if any(n.geltung is EmotionsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is EmotionsChartaGeltung.EMOTIONAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-emotional")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-emotional")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_emotions_charta(
    kognitions_norm: KognitionsNormSatz | None = None,
    *,
    charta_id: str = "emotions-charta",
) -> EmotionsCharta:
    if kognitions_norm is None:
        kognitions_norm = build_kognitions_norm(norm_id=f"{charta_id}-norm")

    normen: list[EmotionsChartaNorm] = []
    for parent_norm in kognitions_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{kognitions_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.kognitions_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kognitions_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EmotionsChartaGeltung.GRUNDLEGEND_EMOTIONAL)
        normen.append(
            EmotionsChartaNorm(
                emotions_charta_id=new_id,
                emotion_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                emotion_weight=new_weight,
                emotion_tier=new_tier,
                canonical=is_canonical,
                emotion_ids=parent_norm.kognitions_norm_ids + (new_id,),
                emotion_tags=parent_norm.kognitions_norm_tags + (f"emotions-charta:{new_geltung.value}",),
            )
        )
    return EmotionsCharta(
        charta_id=charta_id,
        kognitions_norm=kognitions_norm,
        normen=tuple(normen),
    )
