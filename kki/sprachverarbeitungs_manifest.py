"""
#396 SprachverarbeitungsManifest — Sprachverarbeitung als kognitive Superkraft.
Broca-Areal (BA 44/45): Sprachproduktion, syntaktische Verarbeitung, Artikulation.
Wernicke-Areal (BA 22): Sprachverständnis, semantische Dekodierung.
Faszikulusarcuatus: bidirektionale Verbindung Broca↔Wernicke.
Chomsky (1957): Universalgrammatik — tiefsyntaktische Strukturen sind universal.
FOXP2-Gen: evolutionäre Grundlage der Sprachfähigkeit (Enard 2002).
Sapir-Whorf-Hypothese (schwache Form): Sprache beeinflusst Denken.
Leitsterns Agenten kommunizieren strukturiert, präzise und semantisch kohärent:
Bedeutung und Form sind untrennbar — Governance ist Sprache.
Geltungsstufen: GESPERRT / SPRACHVERARBEITEND / GRUNDLEGEND_SPRACHVERARBEITEND
Parent: GedaechtnisKonsolidierungsPakt (#395)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gedaechtnis_konsolidierungs_pakt import (
    GedaechtnisKonsolidierungsGeltung,
    GedaechtnisKonsolidierungsPakt,
    build_gedaechtnis_konsolidierungs_pakt,
)

_GELTUNG_MAP: dict[GedaechtnisKonsolidierungsGeltung, "SprachverarbeitungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GedaechtnisKonsolidierungsGeltung.GESPERRT] = SprachverarbeitungsGeltung.GESPERRT
    _GELTUNG_MAP[GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT] = SprachverarbeitungsGeltung.SPRACHVERARBEITEND
    _GELTUNG_MAP[GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT] = SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND


class SprachverarbeitungsTyp(Enum):
    SCHUTZ_SPRACHVERARBEITUNG = "schutz-sprachverarbeitung"
    ORDNUNGS_SPRACHVERARBEITUNG = "ordnungs-sprachverarbeitung"
    SOUVERAENITAETS_SPRACHVERARBEITUNG = "souveraenitaets-sprachverarbeitung"


class SprachverarbeitungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SprachverarbeitungsGeltung(Enum):
    GESPERRT = "gesperrt"
    SPRACHVERARBEITEND = "sprachverarbeitend"
    GRUNDLEGEND_SPRACHVERARBEITEND = "grundlegend-sprachverarbeitend"


_init_map()

_TYP_MAP: dict[SprachverarbeitungsGeltung, SprachverarbeitungsTyp] = {
    SprachverarbeitungsGeltung.GESPERRT: SprachverarbeitungsTyp.SCHUTZ_SPRACHVERARBEITUNG,
    SprachverarbeitungsGeltung.SPRACHVERARBEITEND: SprachverarbeitungsTyp.ORDNUNGS_SPRACHVERARBEITUNG,
    SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND: SprachverarbeitungsTyp.SOUVERAENITAETS_SPRACHVERARBEITUNG,
}

_PROZEDUR_MAP: dict[SprachverarbeitungsGeltung, SprachverarbeitungsProzedur] = {
    SprachverarbeitungsGeltung.GESPERRT: SprachverarbeitungsProzedur.NOTPROZEDUR,
    SprachverarbeitungsGeltung.SPRACHVERARBEITEND: SprachverarbeitungsProzedur.REGELPROTOKOLL,
    SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND: SprachverarbeitungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SprachverarbeitungsGeltung, float] = {
    SprachverarbeitungsGeltung.GESPERRT: 0.0,
    SprachverarbeitungsGeltung.SPRACHVERARBEITEND: 0.04,
    SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND: 0.08,
}

_TIER_DELTA: dict[SprachverarbeitungsGeltung, int] = {
    SprachverarbeitungsGeltung.GESPERRT: 0,
    SprachverarbeitungsGeltung.SPRACHVERARBEITEND: 1,
    SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SprachverarbeitungsNorm:
    sprachverarbeitungs_manifest_id: str
    sprachverarbeitungs_typ: SprachverarbeitungsTyp
    prozedur: SprachverarbeitungsProzedur
    geltung: SprachverarbeitungsGeltung
    sprachverarbeitungs_weight: float
    sprachverarbeitungs_tier: int
    canonical: bool
    sprachverarbeitungs_ids: tuple[str, ...]
    sprachverarbeitungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class SprachverarbeitungsManifest:
    manifest_id: str
    gedaechtnis_konsolidierungs_pakt: GedaechtnisKonsolidierungsPakt
    normen: tuple[SprachverarbeitungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprachverarbeitungs_manifest_id for n in self.normen if n.geltung is SprachverarbeitungsGeltung.GESPERRT)

    @property
    def sprachverarbeitend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprachverarbeitungs_manifest_id for n in self.normen if n.geltung is SprachverarbeitungsGeltung.SPRACHVERARBEITEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprachverarbeitungs_manifest_id for n in self.normen if n.geltung is SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND)

    @property
    def manifest_signal(self):
        if any(n.geltung is SprachverarbeitungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is SprachverarbeitungsGeltung.SPRACHVERARBEITEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-sprachverarbeitend")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-sprachverarbeitend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_sprachverarbeitungs_manifest(
    gedaechtnis_konsolidierungs_pakt: GedaechtnisKonsolidierungsPakt | None = None,
    *,
    manifest_id: str = "sprachverarbeitungs-manifest",
) -> SprachverarbeitungsManifest:
    if gedaechtnis_konsolidierungs_pakt is None:
        gedaechtnis_konsolidierungs_pakt = build_gedaechtnis_konsolidierungs_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[SprachverarbeitungsNorm] = []
    for parent_norm in gedaechtnis_konsolidierungs_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.gedaechtnis_konsolidierungs_pakt_id.removeprefix(f'{gedaechtnis_konsolidierungs_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.gedaechtnis_konsolidierungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gedaechtnis_konsolidierungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND)
        normen.append(
            SprachverarbeitungsNorm(
                sprachverarbeitungs_manifest_id=new_id,
                sprachverarbeitungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                sprachverarbeitungs_weight=new_weight,
                sprachverarbeitungs_tier=new_tier,
                canonical=is_canonical,
                sprachverarbeitungs_ids=parent_norm.gedaechtnis_konsolidierungs_ids + (new_id,),
                sprachverarbeitungs_tags=parent_norm.gedaechtnis_konsolidierungs_tags + (f"sprachverarbeitung:{new_geltung.value}",),
            )
        )
    return SprachverarbeitungsManifest(
        manifest_id=manifest_id,
        gedaechtnis_konsolidierungs_pakt=gedaechtnis_konsolidierungs_pakt,
        normen=tuple(normen),
    )
