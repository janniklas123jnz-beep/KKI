"""
#437 AufmerksamkeitsSenat — Aufmerksamkeit: Spotlight-Modell und Feature-Integration.
Posner (1980): Spotlight-Modell der Aufmerksamkeit — Ort im Raum wird priorisiert.
Treisman (1980): Feature-Integration-Theorie — Merkmale werden durch Aufmerksamkeit gebunden.
Kahneman (1973): Kapazitätsmodell — Aufmerksamkeit als begrenzte Ressource.
Leitsterns Supervisor = Aufmerksamkeits-Spotlight: priorisiert kritische Agenten dynamisch.
Geltungsstufen: GESPERRT / AUFMERKSAM / GRUNDLEGEND_AUFMERKSAM
Parent: WahrnehmungsManifest (#436)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wahrnehmungs_manifest import (
    WahrnehmungsManifest,
    WahrnehmungsManifestGeltung,
    build_wahrnehmungs_manifest,
)

_GELTUNG_MAP: dict[WahrnehmungsManifestGeltung, "AufmerksamkeitsSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[WahrnehmungsManifestGeltung.GESPERRT] = AufmerksamkeitsSenatGeltung.GESPERRT
    _GELTUNG_MAP[WahrnehmungsManifestGeltung.WAHRNEHMEND] = AufmerksamkeitsSenatGeltung.AUFMERKSAM
    _GELTUNG_MAP[WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND] = AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM


class AufmerksamkeitsSenatTyp(Enum):
    SCHUTZ_AUFMERKSAMKEIT = "schutz-aufmerksamkeit"
    ORDNUNGS_AUFMERKSAMKEIT = "ordnungs-aufmerksamkeit"
    SOUVERAENITAETS_AUFMERKSAMKEIT = "souveraenitaets-aufmerksamkeit"


class AufmerksamkeitsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AufmerksamkeitsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    AUFMERKSAM = "aufmerksam"
    GRUNDLEGEND_AUFMERKSAM = "grundlegend-aufmerksam"


_init_map()

_TYP_MAP: dict[AufmerksamkeitsSenatGeltung, AufmerksamkeitsSenatTyp] = {
    AufmerksamkeitsSenatGeltung.GESPERRT: AufmerksamkeitsSenatTyp.SCHUTZ_AUFMERKSAMKEIT,
    AufmerksamkeitsSenatGeltung.AUFMERKSAM: AufmerksamkeitsSenatTyp.ORDNUNGS_AUFMERKSAMKEIT,
    AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM: AufmerksamkeitsSenatTyp.SOUVERAENITAETS_AUFMERKSAMKEIT,
}

_PROZEDUR_MAP: dict[AufmerksamkeitsSenatGeltung, AufmerksamkeitsSenatProzedur] = {
    AufmerksamkeitsSenatGeltung.GESPERRT: AufmerksamkeitsSenatProzedur.NOTPROZEDUR,
    AufmerksamkeitsSenatGeltung.AUFMERKSAM: AufmerksamkeitsSenatProzedur.REGELPROTOKOLL,
    AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM: AufmerksamkeitsSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AufmerksamkeitsSenatGeltung, float] = {
    AufmerksamkeitsSenatGeltung.GESPERRT: 0.0,
    AufmerksamkeitsSenatGeltung.AUFMERKSAM: 0.04,
    AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM: 0.08,
}

_TIER_DELTA: dict[AufmerksamkeitsSenatGeltung, int] = {
    AufmerksamkeitsSenatGeltung.GESPERRT: 0,
    AufmerksamkeitsSenatGeltung.AUFMERKSAM: 1,
    AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AufmerksamkeitsSenatNorm:
    aufmerksamkeits_senat_id: str
    aufmerksamkeit_typ: AufmerksamkeitsSenatTyp
    prozedur: AufmerksamkeitsSenatProzedur
    geltung: AufmerksamkeitsSenatGeltung
    aufmerksamkeit_weight: float
    aufmerksamkeit_tier: int
    canonical: bool
    aufmerksamkeit_ids: tuple[str, ...]
    aufmerksamkeit_tags: tuple[str, ...]


@dataclass(frozen=True)
class AufmerksamkeitsSenat:
    senat_id: str
    wahrnehmungs_manifest: WahrnehmungsManifest
    normen: tuple[AufmerksamkeitsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aufmerksamkeits_senat_id for n in self.normen if n.geltung is AufmerksamkeitsSenatGeltung.GESPERRT)

    @property
    def aufmerksam_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aufmerksamkeits_senat_id for n in self.normen if n.geltung is AufmerksamkeitsSenatGeltung.AUFMERKSAM)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aufmerksamkeits_senat_id for n in self.normen if n.geltung is AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM)

    @property
    def senat_signal(self):
        if any(n.geltung is AufmerksamkeitsSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is AufmerksamkeitsSenatGeltung.AUFMERKSAM for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-aufmerksam")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-aufmerksam")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_aufmerksamkeits_senat(
    wahrnehmungs_manifest: WahrnehmungsManifest | None = None,
    *,
    senat_id: str = "aufmerksamkeits-senat",
) -> AufmerksamkeitsSenat:
    if wahrnehmungs_manifest is None:
        wahrnehmungs_manifest = build_wahrnehmungs_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[AufmerksamkeitsSenatNorm] = []
    for parent_norm in wahrnehmungs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.wahrnehmungs_manifest_id.removeprefix(f'{wahrnehmungs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.wahrnehmung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.wahrnehmung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AufmerksamkeitsSenatGeltung.GRUNDLEGEND_AUFMERKSAM)
        normen.append(
            AufmerksamkeitsSenatNorm(
                aufmerksamkeits_senat_id=new_id,
                aufmerksamkeit_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                aufmerksamkeit_weight=new_weight,
                aufmerksamkeit_tier=new_tier,
                canonical=is_canonical,
                aufmerksamkeit_ids=parent_norm.wahrnehmung_ids + (new_id,),
                aufmerksamkeit_tags=parent_norm.wahrnehmung_tags + (f"aufmerksamkeits-senat:{new_geltung.value}",),
            )
        )
    return AufmerksamkeitsSenat(
        senat_id=senat_id,
        wahrnehmungs_manifest=wahrnehmungs_manifest,
        normen=tuple(normen),
    )
