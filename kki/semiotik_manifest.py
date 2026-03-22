"""
#466 SemiotikManifest — Agenten-Signale klassifiziert nach Peirce-Trichotomie.
Peirce (1903): Collected Papers — Ikon, Index, Symbol als Zeichentypologie.
Eco (1976): A Theory of Semiotics — Semiotik als allgemeine Zeichenlehre.
Barthes (1957): Mythologies — kulturelle Zeichen und sekundäre Bedeutungssysteme.
Leitsterns Semiotik: Agenten-Signale klassifiziert nach Peirce-Trichotomie (ikonisch/indexikal/symbolisch).
Geltungsstufen: GESPERRT / SEMIOTISCH / GRUNDLEGEND_SEMIOTISCH
Parent: PragmatikPakt (#465)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .pragmatik_pakt import (
    PragmatikPakt,
    PragmatikPaktGeltung,
    build_pragmatik_pakt,
)

_GELTUNG_MAP: dict[PragmatikPaktGeltung, "SemiotikManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PragmatikPaktGeltung.GESPERRT] = SemiotikManifestGeltung.GESPERRT
    _GELTUNG_MAP[PragmatikPaktGeltung.PRAGMATISCH] = SemiotikManifestGeltung.SEMIOTISCH
    _GELTUNG_MAP[PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH] = SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH


class SemiotikManifestTyp(Enum):
    SCHUTZ_SEMIOTIK = "schutz-semiotik"
    ORDNUNGS_SEMIOTIK = "ordnungs-semiotik"
    SOUVERAENITAETS_SEMIOTIK = "souveraenitaets-semiotik"


class SemiotikManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SemiotikManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    SEMIOTISCH = "semiotisch"
    GRUNDLEGEND_SEMIOTISCH = "grundlegend-semiotisch"


_init_map()

_TYP_MAP: dict[SemiotikManifestGeltung, SemiotikManifestTyp] = {
    SemiotikManifestGeltung.GESPERRT: SemiotikManifestTyp.SCHUTZ_SEMIOTIK,
    SemiotikManifestGeltung.SEMIOTISCH: SemiotikManifestTyp.ORDNUNGS_SEMIOTIK,
    SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH: SemiotikManifestTyp.SOUVERAENITAETS_SEMIOTIK,
}

_PROZEDUR_MAP: dict[SemiotikManifestGeltung, SemiotikManifestProzedur] = {
    SemiotikManifestGeltung.GESPERRT: SemiotikManifestProzedur.NOTPROZEDUR,
    SemiotikManifestGeltung.SEMIOTISCH: SemiotikManifestProzedur.REGELPROTOKOLL,
    SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH: SemiotikManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SemiotikManifestGeltung, float] = {
    SemiotikManifestGeltung.GESPERRT: 0.0,
    SemiotikManifestGeltung.SEMIOTISCH: 0.04,
    SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH: 0.08,
}

_TIER_DELTA: dict[SemiotikManifestGeltung, int] = {
    SemiotikManifestGeltung.GESPERRT: 0,
    SemiotikManifestGeltung.SEMIOTISCH: 1,
    SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH: 2,
}


@dataclass(frozen=True)
class SemiotikManifestNorm:
    semiotik_manifest_id: str
    semiotik_manifest_typ: SemiotikManifestTyp
    prozedur: SemiotikManifestProzedur
    geltung: SemiotikManifestGeltung
    semiotik_weight: float
    semiotik_tier: int
    canonical: bool
    semiotik_ids: tuple[str, ...]
    semiotik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SemiotikManifest:
    manifest_id: str
    pragmatik_pakt: PragmatikPakt
    normen: tuple[SemiotikManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semiotik_manifest_id for n in self.normen if n.geltung is SemiotikManifestGeltung.GESPERRT)

    @property
    def semiotisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semiotik_manifest_id for n in self.normen if n.geltung is SemiotikManifestGeltung.SEMIOTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semiotik_manifest_id for n in self.normen if n.geltung is SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is SemiotikManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is SemiotikManifestGeltung.SEMIOTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-semiotisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-semiotisch")


def build_semiotik_manifest(
    pragmatik_pakt: PragmatikPakt | None = None,
    *,
    manifest_id: str = "semiotik-manifest",
) -> SemiotikManifest:
    if pragmatik_pakt is None:
        pragmatik_pakt = build_pragmatik_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[SemiotikManifestNorm] = []
    for parent_norm in pragmatik_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.pragmatik_pakt_id.removeprefix(f'{pragmatik_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.pragmatik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.pragmatik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH)
        normen.append(
            SemiotikManifestNorm(
                semiotik_manifest_id=new_id,
                semiotik_manifest_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                semiotik_weight=new_weight,
                semiotik_tier=new_tier,
                canonical=is_canonical,
                semiotik_ids=parent_norm.pragmatik_ids + (new_id,),
                semiotik_tags=parent_norm.pragmatik_tags + (f"semiotik-manifest:{new_geltung.value}",),
            )
        )
    return SemiotikManifest(
        manifest_id=manifest_id,
        pragmatik_pakt=pragmatik_pakt,
        normen=tuple(normen),
    )
