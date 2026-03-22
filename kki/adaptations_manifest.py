"""
#456 AdaptationsManifest — Adaptation und Koevolution: Arme Wettläufe und Symbiose.
Red-Queen-Hypothese (Van Valen 1973): Koevolution erzwingt ständige Anpassung — Rüstungswettlauf.
Margulis (1967): Endosymbiosetheorie — Mitochondrien aus Bakterien. Kooperation als Evolution.
Dobzhansky (1937): Moderne Synthese — Darwin + Mendel + Population Genetics vereint.
Leitsterns Agenten koevolvieren mit ihrer Umgebung: Red-Queen-Dynamik im Schwarm-Ökosystem.
Geltungsstufen: GESPERRT / ADAPTIV / GRUNDLEGEND_ADAPTIV
Parent: FitnessPakt (#455)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fitness_pakt import (
    FitnessPakt,
    FitnessPaktGeltung,
    build_fitness_pakt,
)

_GELTUNG_MAP: dict[FitnessPaktGeltung, "AdaptationsManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FitnessPaktGeltung.GESPERRT] = AdaptationsManifestGeltung.GESPERRT
    _GELTUNG_MAP[FitnessPaktGeltung.FITNESSORIENTIERT] = AdaptationsManifestGeltung.ADAPTIV
    _GELTUNG_MAP[FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT] = AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV


class AdaptationsManifestTyp(Enum):
    SCHUTZ_ADAPTATION = "schutz-adaptation"
    ORDNUNGS_ADAPTATION = "ordnungs-adaptation"
    SOUVERAENITAETS_ADAPTATION = "souveraenitaets-adaptation"


class AdaptationsManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AdaptationsManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    ADAPTIV = "adaptiv"
    GRUNDLEGEND_ADAPTIV = "grundlegend-adaptiv"


_init_map()

_TYP_MAP: dict[AdaptationsManifestGeltung, AdaptationsManifestTyp] = {
    AdaptationsManifestGeltung.GESPERRT: AdaptationsManifestTyp.SCHUTZ_ADAPTATION,
    AdaptationsManifestGeltung.ADAPTIV: AdaptationsManifestTyp.ORDNUNGS_ADAPTATION,
    AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV: AdaptationsManifestTyp.SOUVERAENITAETS_ADAPTATION,
}

_PROZEDUR_MAP: dict[AdaptationsManifestGeltung, AdaptationsManifestProzedur] = {
    AdaptationsManifestGeltung.GESPERRT: AdaptationsManifestProzedur.NOTPROZEDUR,
    AdaptationsManifestGeltung.ADAPTIV: AdaptationsManifestProzedur.REGELPROTOKOLL,
    AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV: AdaptationsManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AdaptationsManifestGeltung, float] = {
    AdaptationsManifestGeltung.GESPERRT: 0.0,
    AdaptationsManifestGeltung.ADAPTIV: 0.04,
    AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV: 0.08,
}

_TIER_DELTA: dict[AdaptationsManifestGeltung, int] = {
    AdaptationsManifestGeltung.GESPERRT: 0,
    AdaptationsManifestGeltung.ADAPTIV: 1,
    AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV: 2,
}


@dataclass(frozen=True)
class AdaptationsManifestNorm:
    adaptation_manifest_id: str
    adaptation_manifest_typ: AdaptationsManifestTyp
    prozedur: AdaptationsManifestProzedur
    geltung: AdaptationsManifestGeltung
    adaptation_weight: float
    adaptation_tier: int
    canonical: bool
    adaptation_ids: tuple[str, ...]
    adaptation_tags: tuple[str, ...]


@dataclass(frozen=True)
class AdaptationsManifest:
    manifest_id: str
    fitness_pakt: FitnessPakt
    normen: tuple[AdaptationsManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptation_manifest_id for n in self.normen if n.geltung is AdaptationsManifestGeltung.GESPERRT)

    @property
    def adaptiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptation_manifest_id for n in self.normen if n.geltung is AdaptationsManifestGeltung.ADAPTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptation_manifest_id for n in self.normen if n.geltung is AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV)

    @property
    def manifest_signal(self):
        if any(n.geltung is AdaptationsManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is AdaptationsManifestGeltung.ADAPTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-adaptiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-adaptiv")


def build_adaptations_manifest(
    fitness_pakt: FitnessPakt | None = None,
    *,
    manifest_id: str = "adaptations-manifest",
) -> AdaptationsManifest:
    if fitness_pakt is None:
        fitness_pakt = build_fitness_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[AdaptationsManifestNorm] = []
    for parent_norm in fitness_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.fitness_pakt_id.removeprefix(f'{fitness_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.fitness_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fitness_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV)
        normen.append(
            AdaptationsManifestNorm(
                adaptation_manifest_id=new_id,
                adaptation_manifest_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                adaptation_weight=new_weight,
                adaptation_tier=new_tier,
                canonical=is_canonical,
                adaptation_ids=parent_norm.fitness_ids + (new_id,),
                adaptation_tags=parent_norm.fitness_tags + (f"adaptations-manifest:{new_geltung.value}",),
            )
        )
    return AdaptationsManifest(
        manifest_id=manifest_id,
        fitness_pakt=fitness_pakt,
        normen=tuple(normen),
    )
