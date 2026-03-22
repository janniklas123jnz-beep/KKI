"""
#438 KognitionsNorm — Kognition: Dual-Process-Theorie und Bounded Rationality.
Kahneman (2011): System 1 (schnell, intuitiv) vs. System 2 (langsam, analytisch).
Simon (1956): Bounded Rationality — Satisficing statt Optimizing unter realen Constraints.
Tversky & Kahneman (1974): Heuristiken und Biases — Verfügbarkeit, Repräsentativität, Anker.
Leitsterns Agenten: System-1-Schnellreaktionen + System-2-Planungseinheiten im Schwarm.
Geltungsstufen: GESPERRT / KOGNITIV / GRUNDLEGEND_KOGNITIV
Parent: AufmerksamkeitsSenat (#437) — *_norm-Muster
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .aufmerksamkeits_senat import (
    AufmerksamkeitsSenat,
    AufmerksamkeitsSenatGeltung,
    build_aufmerksamkeits_senat,
)

_GELTUNG_MAP: dict[AufmerksamkeitsSenatGeltung, "KognitionsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AufmerksamkeitsSenatGeltung.GESPERRT] = KognitionsNormGeltung.GESPERRT
    _GELTUNG_MAP[AufmerksamkeitsSenatGeltung.AUFMERKSAM] = KognitionsNormGeltung.KOGNITIV
    _GELTUNG_MAP[AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM] = KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV


class KognitionsNormTyp(Enum):
    SCHUTZ_KOGNITION = "schutz-kognition"
    ORDNUNGS_KOGNITION = "ordnungs-kognition"
    SOUVERAENITAETS_KOGNITION = "souveraenitaets-kognition"


class KognitionsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KognitionsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    KOGNITIV = "kognitiv"
    GRUNDLEGEND_KOGNITIV = "grundlegend-kognitiv"


_init_map()

_TYP_MAP: dict[KognitionsNormGeltung, KognitionsNormTyp] = {
    KognitionsNormGeltung.GESPERRT: KognitionsNormTyp.SCHUTZ_KOGNITION,
    KognitionsNormGeltung.KOGNITIV: KognitionsNormTyp.ORDNUNGS_KOGNITION,
    KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV: KognitionsNormTyp.SOUVERAENITAETS_KOGNITION,
}

_PROZEDUR_MAP: dict[KognitionsNormGeltung, KognitionsNormProzedur] = {
    KognitionsNormGeltung.GESPERRT: KognitionsNormProzedur.NOTPROZEDUR,
    KognitionsNormGeltung.KOGNITIV: KognitionsNormProzedur.REGELPROTOKOLL,
    KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV: KognitionsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KognitionsNormGeltung, float] = {
    KognitionsNormGeltung.GESPERRT: 0.0,
    KognitionsNormGeltung.KOGNITIV: 0.04,
    KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV: 0.08,
}

_TIER_DELTA: dict[KognitionsNormGeltung, int] = {
    KognitionsNormGeltung.GESPERRT: 0,
    KognitionsNormGeltung.KOGNITIV: 1,
    KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KognitionsNormEintrag:
    norm_id: str
    kognitions_norm_typ: KognitionsNormTyp
    prozedur: KognitionsNormProzedur
    geltung: KognitionsNormGeltung
    kognitions_norm_weight: float
    kognitions_norm_tier: int
    canonical: bool
    kognitions_norm_ids: tuple[str, ...]
    kognitions_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class KognitionsNormSatz:
    norm_id: str
    aufmerksamkeits_senat: AufmerksamkeitsSenat
    normen: tuple[KognitionsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KognitionsNormGeltung.GESPERRT)

    @property
    def kognitiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KognitionsNormGeltung.KOGNITIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV)

    @property
    def norm_signal(self):
        if any(n.geltung is KognitionsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is KognitionsNormGeltung.KOGNITIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-kognitiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-kognitiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kognitions_norm(
    aufmerksamkeits_senat: AufmerksamkeitsSenat | None = None,
    *,
    norm_id: str = "kognitions-norm",
) -> KognitionsNormSatz:
    if aufmerksamkeits_senat is None:
        aufmerksamkeits_senat = build_aufmerksamkeits_senat(senat_id=f"{norm_id}-senat")

    normen: list[KognitionsNormEintrag] = []
    for parent_norm in aufmerksamkeits_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.aufmerksamkeits_senat_id.removeprefix(f'{aufmerksamkeits_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.aufmerksamkeit_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.aufmerksamkeit_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KognitionsNormGeltung.GRUNDLEGEND_KOGNITIV)
        normen.append(
            KognitionsNormEintrag(
                norm_id=new_id,
                kognitions_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kognitions_norm_weight=new_weight,
                kognitions_norm_tier=new_tier,
                canonical=is_canonical,
                kognitions_norm_ids=parent_norm.aufmerksamkeit_ids + (new_id,),
                kognitions_norm_tags=parent_norm.aufmerksamkeit_tags + (f"kognitions-norm:{new_geltung.value}",),
            )
        )
    return KognitionsNormSatz(
        norm_id=norm_id,
        aufmerksamkeits_senat=aufmerksamkeits_senat,
        normen=tuple(normen),
    )
