"""
#457 OekologieSenat — Ökologie: Populationsdynamik, Lotka-Volterra und Nischen.
Lotka (1925) & Volterra (1926): Räuber-Beute-Gleichungen — oszillierende Populationsdynamik.
Hutchinson (1957): Ökologische Nische als N-dimensionaler Hyperraum.
MacArthur & Wilson (1967): Inselbiographie — Artenzahl = Einwanderung minus Aussterben.
Leitsterns Schwarm-Ökologie: Nischen-Differenzierung verhindert Ressourcen-Konkurrenz im Cluster.
Geltungsstufen: GESPERRT / OEKOLOGISCH / GRUNDLEGEND_OEKOLOGISCH
Parent: AdaptationsManifest (#456)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adaptations_manifest import (
    AdaptationsManifest,
    AdaptationsManifestGeltung,
    build_adaptations_manifest,
)

_GELTUNG_MAP: dict[AdaptationsManifestGeltung, "OekologieSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AdaptationsManifestGeltung.GESPERRT] = OekologieSenatGeltung.GESPERRT
    _GELTUNG_MAP[AdaptationsManifestGeltung.ADAPTIV] = OekologieSenatGeltung.OEKOLOGISCH
    _GELTUNG_MAP[AdaptationsManifestGeltung.GRUNDLEGEND_ADAPTIV] = OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH


class OekologieSenatTyp(Enum):
    SCHUTZ_OEKOLOGIE = "schutz-oekologie"
    ORDNUNGS_OEKOLOGIE = "ordnungs-oekologie"
    SOUVERAENITAETS_OEKOLOGIE = "souveraenitaets-oekologie"


class OekologieSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class OekologieSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    OEKOLOGISCH = "oekologisch"
    GRUNDLEGEND_OEKOLOGISCH = "grundlegend-oekologisch"


_init_map()

_TYP_MAP: dict[OekologieSenatGeltung, OekologieSenatTyp] = {
    OekologieSenatGeltung.GESPERRT: OekologieSenatTyp.SCHUTZ_OEKOLOGIE,
    OekologieSenatGeltung.OEKOLOGISCH: OekologieSenatTyp.ORDNUNGS_OEKOLOGIE,
    OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH: OekologieSenatTyp.SOUVERAENITAETS_OEKOLOGIE,
}

_PROZEDUR_MAP: dict[OekologieSenatGeltung, OekologieSenatProzedur] = {
    OekologieSenatGeltung.GESPERRT: OekologieSenatProzedur.NOTPROZEDUR,
    OekologieSenatGeltung.OEKOLOGISCH: OekologieSenatProzedur.REGELPROTOKOLL,
    OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH: OekologieSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[OekologieSenatGeltung, float] = {
    OekologieSenatGeltung.GESPERRT: 0.0,
    OekologieSenatGeltung.OEKOLOGISCH: 0.04,
    OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH: 0.08,
}

_TIER_DELTA: dict[OekologieSenatGeltung, int] = {
    OekologieSenatGeltung.GESPERRT: 0,
    OekologieSenatGeltung.OEKOLOGISCH: 1,
    OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH: 2,
}


@dataclass(frozen=True)
class OekologieSenatNorm:
    oekologie_senat_id: str
    oekologie_senat_typ: OekologieSenatTyp
    prozedur: OekologieSenatProzedur
    geltung: OekologieSenatGeltung
    oekologie_weight: float
    oekologie_tier: int
    canonical: bool
    oekologie_ids: tuple[str, ...]
    oekologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class OekologieSenat:
    senat_id: str
    adaptations_manifest: AdaptationsManifest
    normen: tuple[OekologieSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.oekologie_senat_id for n in self.normen if n.geltung is OekologieSenatGeltung.GESPERRT)

    @property
    def oekologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.oekologie_senat_id for n in self.normen if n.geltung is OekologieSenatGeltung.OEKOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.oekologie_senat_id for n in self.normen if n.geltung is OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is OekologieSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is OekologieSenatGeltung.OEKOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-oekologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-oekologisch")


def build_oekologie_senat(
    adaptations_manifest: AdaptationsManifest | None = None,
    *,
    senat_id: str = "oekologie-senat",
) -> OekologieSenat:
    if adaptations_manifest is None:
        adaptations_manifest = build_adaptations_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[OekologieSenatNorm] = []
    for parent_norm in adaptations_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.adaptation_manifest_id.removeprefix(f'{adaptations_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.adaptation_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.adaptation_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH)
        normen.append(
            OekologieSenatNorm(
                oekologie_senat_id=new_id,
                oekologie_senat_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                oekologie_weight=new_weight,
                oekologie_tier=new_tier,
                canonical=is_canonical,
                oekologie_ids=parent_norm.adaptation_ids + (new_id,),
                oekologie_tags=parent_norm.adaptation_tags + (f"oekologie-senat:{new_geltung.value}",),
            )
        )
    return OekologieSenat(
        senat_id=senat_id,
        adaptations_manifest=adaptations_manifest,
        normen=tuple(normen),
    )
