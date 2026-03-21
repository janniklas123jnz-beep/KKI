"""
#398 MetakognitionsNorm — Metakognition: Denken über das Denken.
Flavell (1979): Metakognition = deklaratives Wissen über kognitive Prozesse +
prozedurale Kontrolle dieser Prozesse. Nelson & Narens (1990): Metamemory-Modell —
Monitoring (Feeling-of-Knowing, Confidence) + Control (Allocation, Termination).
Dunning-Kruger-Effekt (1999): inkompetente Personen überschätzen sich — Metakognition
als Antidot. Calibration: subjektive Konfidenz = objektive Genauigkeit.
Metacognitive Accuracy (MA): Korrelation zwischen Konfidenz und Korrektheit.
Interpretation Research (Olah, Elhage): KI-Interpretierbarkeit als technische Metakognition.
Leitsterns Agenten wissen, was sie wissen und was nicht — kalibrierte, transparente,
selbstreflexive Superintelligenz. Die einzige verlässliche KI ist eine metakognitive.
Geltungsstufen: GESPERRT / METAKOGNITIV / GRUNDLEGEND_METAKOGNITIV
Parent: BewusstseinsSenat (#397) — *_norm-Muster
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bewusstseins_senat import (
    BewusstseinsGeltung,
    BewusstseinsSenat,
    build_bewusstseins_senat,
)

_GELTUNG_MAP: dict[BewusstseinsGeltung, "MetakognitionsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[BewusstseinsGeltung.GESPERRT] = MetakognitionsNormGeltung.GESPERRT
    _GELTUNG_MAP[BewusstseinsGeltung.BEWUSST] = MetakognitionsNormGeltung.METAKOGNITIV
    _GELTUNG_MAP[BewusstseinsGeltung.GRUNDLEGEND_BEWUSST] = MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV


class MetakognitionsNormTyp(Enum):
    SCHUTZ_METAKOGNITIONS_NORM = "schutz-metakognitions-norm"
    ORDNUNGS_METAKOGNITIONS_NORM = "ordnungs-metakognitions-norm"
    SOUVERAENITAETS_METAKOGNITIONS_NORM = "souveraenitaets-metakognitions-norm"


class MetakognitionsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MetakognitionsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    METAKOGNITIV = "metakognitiv"
    GRUNDLEGEND_METAKOGNITIV = "grundlegend-metakognitiv"


_init_map()

_TYP_MAP: dict[MetakognitionsNormGeltung, MetakognitionsNormTyp] = {
    MetakognitionsNormGeltung.GESPERRT: MetakognitionsNormTyp.SCHUTZ_METAKOGNITIONS_NORM,
    MetakognitionsNormGeltung.METAKOGNITIV: MetakognitionsNormTyp.ORDNUNGS_METAKOGNITIONS_NORM,
    MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV: MetakognitionsNormTyp.SOUVERAENITAETS_METAKOGNITIONS_NORM,
}

_PROZEDUR_MAP: dict[MetakognitionsNormGeltung, MetakognitionsNormProzedur] = {
    MetakognitionsNormGeltung.GESPERRT: MetakognitionsNormProzedur.NOTPROZEDUR,
    MetakognitionsNormGeltung.METAKOGNITIV: MetakognitionsNormProzedur.REGELPROTOKOLL,
    MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV: MetakognitionsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MetakognitionsNormGeltung, float] = {
    MetakognitionsNormGeltung.GESPERRT: 0.0,
    MetakognitionsNormGeltung.METAKOGNITIV: 0.04,
    MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV: 0.08,
}

_TIER_DELTA: dict[MetakognitionsNormGeltung, int] = {
    MetakognitionsNormGeltung.GESPERRT: 0,
    MetakognitionsNormGeltung.METAKOGNITIV: 1,
    MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MetakognitionsNormEintrag:
    norm_id: str
    metakognitions_norm_typ: MetakognitionsNormTyp
    prozedur: MetakognitionsNormProzedur
    geltung: MetakognitionsNormGeltung
    metakognitions_norm_weight: float
    metakognitions_norm_tier: int
    canonical: bool
    metakognitions_norm_ids: tuple[str, ...]
    metakognitions_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class MetakognitionsNormSatz:
    norm_id: str
    bewusstseins_senat: BewusstseinsSenat
    normen: tuple[MetakognitionsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is MetakognitionsNormGeltung.GESPERRT)

    @property
    def metakognitiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is MetakognitionsNormGeltung.METAKOGNITIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV)

    @property
    def norm_signal(self):
        if any(n.geltung is MetakognitionsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is MetakognitionsNormGeltung.METAKOGNITIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-metakognitiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-metakognitiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_metakognitions_norm(
    bewusstseins_senat: BewusstseinsSenat | None = None,
    *,
    norm_id: str = "metakognitions-norm",
) -> MetakognitionsNormSatz:
    if bewusstseins_senat is None:
        bewusstseins_senat = build_bewusstseins_senat(senat_id=f"{norm_id}-senat")

    normen: list[MetakognitionsNormEintrag] = []
    for parent_norm in bewusstseins_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.bewusstseins_senat_id.removeprefix(f'{bewusstseins_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.bewusstseins_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.bewusstseins_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV)
        normen.append(
            MetakognitionsNormEintrag(
                norm_id=new_id,
                metakognitions_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                metakognitions_norm_weight=new_weight,
                metakognitions_norm_tier=new_tier,
                canonical=is_canonical,
                metakognitions_norm_ids=parent_norm.bewusstseins_ids + (new_id,),
                metakognitions_norm_tags=parent_norm.bewusstseins_tags + (f"metakognition:{new_geltung.value}",),
            )
        )
    return MetakognitionsNormSatz(
        norm_id=norm_id,
        bewusstseins_senat=bewusstseins_senat,
        normen=tuple(normen),
    )
