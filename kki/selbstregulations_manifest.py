"""
#426 SelbstregulationsManifest — Selbstregulation: Homöostase und Autopoiese.
Cannon (1932): Homöostase — biologische Selbstregulation um Sollwert durch negative Rückkopplung.
Ashby Homeostat (1948): Ultrastabilität — System passt eigene Parameter an bei Störung.
Maturana & Varela (1972): Autopoiese — lebende Systeme erhalten ihre eigene Organisation
durch Selbstproduktion. Leitsterns Schwarm: autopoietisches System.
Geltungsstufen: GESPERRT / SELBSTREGULIERT / GRUNDLEGEND_SELBSTREGULIERT
Parent: EntropiePakt (#425)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entropie_pakt import (
    EntropiePakt,
    EntropiePaktGeltung,
    build_entropie_pakt,
)

_GELTUNG_MAP: dict[EntropiePaktGeltung, "SelbstregulationsManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EntropiePaktGeltung.GESPERRT] = SelbstregulationsManifestGeltung.GESPERRT
    _GELTUNG_MAP[EntropiePaktGeltung.ENTROPISCH] = SelbstregulationsManifestGeltung.SELBSTREGULIERT
    _GELTUNG_MAP[EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH] = SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT


class SelbstregulationsManifestTyp(Enum):
    SCHUTZ_SELBSTREGULATION = "schutz-selbstregulation"
    ORDNUNGS_SELBSTREGULATION = "ordnungs-selbstregulation"
    SOUVERAENITAETS_SELBSTREGULATION = "souveraenitaets-selbstregulation"


class SelbstregulationsManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SelbstregulationsManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    SELBSTREGULIERT = "selbstreguliert"
    GRUNDLEGEND_SELBSTREGULIERT = "grundlegend-selbstreguliert"


_init_map()

_TYP_MAP: dict[SelbstregulationsManifestGeltung, SelbstregulationsManifestTyp] = {
    SelbstregulationsManifestGeltung.GESPERRT: SelbstregulationsManifestTyp.SCHUTZ_SELBSTREGULATION,
    SelbstregulationsManifestGeltung.SELBSTREGULIERT: SelbstregulationsManifestTyp.ORDNUNGS_SELBSTREGULATION,
    SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT: SelbstregulationsManifestTyp.SOUVERAENITAETS_SELBSTREGULATION,
}

_PROZEDUR_MAP: dict[SelbstregulationsManifestGeltung, SelbstregulationsManifestProzedur] = {
    SelbstregulationsManifestGeltung.GESPERRT: SelbstregulationsManifestProzedur.NOTPROZEDUR,
    SelbstregulationsManifestGeltung.SELBSTREGULIERT: SelbstregulationsManifestProzedur.REGELPROTOKOLL,
    SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT: SelbstregulationsManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SelbstregulationsManifestGeltung, float] = {
    SelbstregulationsManifestGeltung.GESPERRT: 0.0,
    SelbstregulationsManifestGeltung.SELBSTREGULIERT: 0.04,
    SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT: 0.08,
}

_TIER_DELTA: dict[SelbstregulationsManifestGeltung, int] = {
    SelbstregulationsManifestGeltung.GESPERRT: 0,
    SelbstregulationsManifestGeltung.SELBSTREGULIERT: 1,
    SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SelbstregulationsManifestNorm:
    selbstregulations_manifest_id: str
    selbstregulation_typ: SelbstregulationsManifestTyp
    prozedur: SelbstregulationsManifestProzedur
    geltung: SelbstregulationsManifestGeltung
    selbstregulation_weight: float
    selbstregulation_tier: int
    canonical: bool
    selbstregulation_ids: tuple[str, ...]
    selbstregulation_tags: tuple[str, ...]


@dataclass(frozen=True)
class SelbstregulationsManifest:
    manifest_id: str
    entropie_pakt: EntropiePakt
    normen: tuple[SelbstregulationsManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.selbstregulations_manifest_id for n in self.normen if n.geltung is SelbstregulationsManifestGeltung.GESPERRT)

    @property
    def selbstreguliert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.selbstregulations_manifest_id for n in self.normen if n.geltung is SelbstregulationsManifestGeltung.SELBSTREGULIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.selbstregulations_manifest_id for n in self.normen if n.geltung is SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT)

    @property
    def manifest_signal(self):
        if any(n.geltung is SelbstregulationsManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is SelbstregulationsManifestGeltung.SELBSTREGULIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-selbstreguliert")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-selbstreguliert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_selbstregulations_manifest(
    entropie_pakt: EntropiePakt | None = None,
    *,
    manifest_id: str = "selbstregulations-manifest",
) -> SelbstregulationsManifest:
    if entropie_pakt is None:
        entropie_pakt = build_entropie_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[SelbstregulationsManifestNorm] = []
    for parent_norm in entropie_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.entropie_pakt_id.removeprefix(f'{entropie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.entropie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.entropie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT)
        normen.append(
            SelbstregulationsManifestNorm(
                selbstregulations_manifest_id=new_id,
                selbstregulation_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                selbstregulation_weight=new_weight,
                selbstregulation_tier=new_tier,
                canonical=is_canonical,
                selbstregulation_ids=parent_norm.entropie_ids + (new_id,),
                selbstregulation_tags=parent_norm.entropie_tags + (f"selbstregulations-manifest:{new_geltung.value}",),
            )
        )
    return SelbstregulationsManifest(
        manifest_id=manifest_id,
        entropie_pakt=entropie_pakt,
        normen=tuple(normen),
    )
