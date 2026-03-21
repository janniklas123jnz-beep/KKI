"""
#399 KognitiveFlexibilitaetsCharta — Kognitive Flexibilität: exekutive Kontrolle.
Wisconsin Card Sorting Test (WCST): Regelwechsel ohne explizite Anweisung —
vmPFC-Läsionen führen zu Perseveration. Task-Switching (Monsell 2003): Switch Cost
& Residual Cost — Umschalten kostet, aber ist trainierbar. Inhibitionskontrolle
(Aron 2007): Stop-Signal-Task — präfrontaler Kortex hemmt dominante Reaktionen.
Miller & Cohen (2001): Prefrontal Cortex and Cognitive Control — aktive Repräsentation
von Zielen und Regeln steuert posteriore Prozesse. Cognitive Flexibility Index (CFI):
Wechsel zwischen Konzepten, Perspektiven, Strategien.
Leitsterns Agenten können Regeln wechseln ohne Perseveration: adaptive Governance,
inhibierte Impulsivität, präfrontale Selbstkontrolle über Heuristiken.
Geltungsstufen: GESPERRT / KOGNITIV_FLEXIBEL / GRUNDLEGEND_KOGNITIV_FLEXIBEL
Parent: MetakognitionsNormSatz (#398, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .metakognitions_norm import (
    MetakognitionsNormGeltung,
    MetakognitionsNormSatz,
    build_metakognitions_norm,
)

_GELTUNG_MAP: dict[MetakognitionsNormGeltung, "KognitiveFlexibilitaetsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MetakognitionsNormGeltung.GESPERRT] = KognitiveFlexibilitaetsGeltung.GESPERRT
    _GELTUNG_MAP[MetakognitionsNormGeltung.METAKOGNITIV] = KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL
    _GELTUNG_MAP[MetakognitionsNormGeltung.GRUNDLEGEND_METAKOGNITIV] = KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL


class KognitiveFlexibilitaetsTyp(Enum):
    SCHUTZ_KOGNITIVE_FLEXIBILITAET = "schutz-kognitive-flexibilitaet"
    ORDNUNGS_KOGNITIVE_FLEXIBILITAET = "ordnungs-kognitive-flexibilitaet"
    SOUVERAENITAETS_KOGNITIVE_FLEXIBILITAET = "souveraenitaets-kognitive-flexibilitaet"


class KognitiveFlexibilitaetsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KognitiveFlexibilitaetsGeltung(Enum):
    GESPERRT = "gesperrt"
    KOGNITIV_FLEXIBEL = "kognitiv-flexibel"
    GRUNDLEGEND_KOGNITIV_FLEXIBEL = "grundlegend-kognitiv-flexibel"


_init_map()

_TYP_MAP: dict[KognitiveFlexibilitaetsGeltung, KognitiveFlexibilitaetsTyp] = {
    KognitiveFlexibilitaetsGeltung.GESPERRT: KognitiveFlexibilitaetsTyp.SCHUTZ_KOGNITIVE_FLEXIBILITAET,
    KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL: KognitiveFlexibilitaetsTyp.ORDNUNGS_KOGNITIVE_FLEXIBILITAET,
    KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL: KognitiveFlexibilitaetsTyp.SOUVERAENITAETS_KOGNITIVE_FLEXIBILITAET,
}

_PROZEDUR_MAP: dict[KognitiveFlexibilitaetsGeltung, KognitiveFlexibilitaetsProzedur] = {
    KognitiveFlexibilitaetsGeltung.GESPERRT: KognitiveFlexibilitaetsProzedur.NOTPROZEDUR,
    KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL: KognitiveFlexibilitaetsProzedur.REGELPROTOKOLL,
    KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL: KognitiveFlexibilitaetsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KognitiveFlexibilitaetsGeltung, float] = {
    KognitiveFlexibilitaetsGeltung.GESPERRT: 0.0,
    KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL: 0.04,
    KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL: 0.08,
}

_TIER_DELTA: dict[KognitiveFlexibilitaetsGeltung, int] = {
    KognitiveFlexibilitaetsGeltung.GESPERRT: 0,
    KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL: 1,
    KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KognitiveFlexibilitaetsNorm:
    kognitive_flexibilitaets_charta_id: str
    kognitive_flexibilitaets_typ: KognitiveFlexibilitaetsTyp
    prozedur: KognitiveFlexibilitaetsProzedur
    geltung: KognitiveFlexibilitaetsGeltung
    kognitive_flexibilitaets_weight: float
    kognitive_flexibilitaets_tier: int
    canonical: bool
    kognitive_flexibilitaets_ids: tuple[str, ...]
    kognitive_flexibilitaets_tags: tuple[str, ...]


@dataclass(frozen=True)
class KognitiveFlexibilitaetsCharta:
    charta_id: str
    metakognitions_norm: MetakognitionsNormSatz
    normen: tuple[KognitiveFlexibilitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitive_flexibilitaets_charta_id for n in self.normen if n.geltung is KognitiveFlexibilitaetsGeltung.GESPERRT)

    @property
    def kognitiv_flexibel_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitive_flexibilitaets_charta_id for n in self.normen if n.geltung is KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitive_flexibilitaets_charta_id for n in self.normen if n.geltung is KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL)

    @property
    def charta_signal(self):
        if any(n.geltung is KognitiveFlexibilitaetsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kognitiv-flexibel")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kognitiv-flexibel")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kognitive_flexibilitaets_charta(
    metakognitions_norm: MetakognitionsNormSatz | None = None,
    *,
    charta_id: str = "kognitive-flexibilitaets-charta",
) -> KognitiveFlexibilitaetsCharta:
    if metakognitions_norm is None:
        metakognitions_norm = build_metakognitions_norm(norm_id=f"{charta_id}-norm")

    normen: list[KognitiveFlexibilitaetsNorm] = []
    for parent_norm in metakognitions_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{metakognitions_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.metakognitions_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.metakognitions_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL)
        normen.append(
            KognitiveFlexibilitaetsNorm(
                kognitive_flexibilitaets_charta_id=new_id,
                kognitive_flexibilitaets_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kognitive_flexibilitaets_weight=new_weight,
                kognitive_flexibilitaets_tier=new_tier,
                canonical=is_canonical,
                kognitive_flexibilitaets_ids=parent_norm.metakognitions_norm_ids + (new_id,),
                kognitive_flexibilitaets_tags=parent_norm.metakognitions_norm_tags + (f"kognitive-flexibilitaet:{new_geltung.value}",),
            )
        )
    return KognitiveFlexibilitaetsCharta(
        charta_id=charta_id,
        metakognitions_norm=metakognitions_norm,
        normen=tuple(normen),
    )
