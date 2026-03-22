"""
#447 AuktionsSenat — Auktionstheorie: Ressourcenallokation im Schwarm.
Vickrey (1961): Second-Price (Vickrey) Auction — Wahrheit als dominante Strategie. Nobel 1996.
Milgrom & Wilson (2020): Kombinatorische Auktionen — simultane mehrstufige Auktionen. Nobel 2020.
Wilson (1969): Fluch des Gewinners (Winner's Curse) bei gemeinsamen Werten.
Leitsterns Ressourcenzuteilung: Vickrey-Auktionen für faire, effiziente Aufgabenverteilung.
Geltungsstufen: GESPERRT / AUKTIONAL / GRUNDLEGEND_AUKTIONAL
Parent: RationalitaetsManifest (#446)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rationalitaets_manifest import (
    RationalitaetsManifest,
    RationalitaetsManifestGeltung,
    build_rationalitaets_manifest,
)

_GELTUNG_MAP: dict[RationalitaetsManifestGeltung, "AuktionsSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RationalitaetsManifestGeltung.GESPERRT] = AuktionsSenatGeltung.GESPERRT
    _GELTUNG_MAP[RationalitaetsManifestGeltung.RATIONAL] = AuktionsSenatGeltung.AUKTIONAL
    _GELTUNG_MAP[RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL] = AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL


class AuktionsSenatTyp(Enum):
    SCHUTZ_AUKTION = "schutz-auktion"
    ORDNUNGS_AUKTION = "ordnungs-auktion"
    SOUVERAENITAETS_AUKTION = "souveraenitaets-auktion"


class AuktionsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AuktionsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    AUKTIONAL = "auktional"
    GRUNDLEGEND_AUKTIONAL = "grundlegend-auktional"


_init_map()

_TYP_MAP: dict[AuktionsSenatGeltung, AuktionsSenatTyp] = {
    AuktionsSenatGeltung.GESPERRT: AuktionsSenatTyp.SCHUTZ_AUKTION,
    AuktionsSenatGeltung.AUKTIONAL: AuktionsSenatTyp.ORDNUNGS_AUKTION,
    AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL: AuktionsSenatTyp.SOUVERAENITAETS_AUKTION,
}

_PROZEDUR_MAP: dict[AuktionsSenatGeltung, AuktionsSenatProzedur] = {
    AuktionsSenatGeltung.GESPERRT: AuktionsSenatProzedur.NOTPROZEDUR,
    AuktionsSenatGeltung.AUKTIONAL: AuktionsSenatProzedur.REGELPROTOKOLL,
    AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL: AuktionsSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AuktionsSenatGeltung, float] = {
    AuktionsSenatGeltung.GESPERRT: 0.0,
    AuktionsSenatGeltung.AUKTIONAL: 0.04,
    AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL: 0.08,
}

_TIER_DELTA: dict[AuktionsSenatGeltung, int] = {
    AuktionsSenatGeltung.GESPERRT: 0,
    AuktionsSenatGeltung.AUKTIONAL: 1,
    AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuktionsSenatNorm:
    auktions_senat_id: str
    auktions_senat_typ: AuktionsSenatTyp
    prozedur: AuktionsSenatProzedur
    geltung: AuktionsSenatGeltung
    auktions_weight: float
    auktions_tier: int
    canonical: bool
    auktions_ids: tuple[str, ...]
    auktions_tags: tuple[str, ...]


@dataclass(frozen=True)
class AuktionsSenat:
    senat_id: str
    rationalitaets_manifest: RationalitaetsManifest
    normen: tuple[AuktionsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.auktions_senat_id for n in self.normen if n.geltung is AuktionsSenatGeltung.GESPERRT)

    @property
    def auktional_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.auktions_senat_id for n in self.normen if n.geltung is AuktionsSenatGeltung.AUKTIONAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.auktions_senat_id for n in self.normen if n.geltung is AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL)

    @property
    def senat_signal(self):
        if any(n.geltung is AuktionsSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is AuktionsSenatGeltung.AUKTIONAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-auktional")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-auktional")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_auktions_senat(
    rationalitaets_manifest: RationalitaetsManifest | None = None,
    *,
    senat_id: str = "auktions-senat",
) -> AuktionsSenat:
    if rationalitaets_manifest is None:
        rationalitaets_manifest = build_rationalitaets_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[AuktionsSenatNorm] = []
    for parent_norm in rationalitaets_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.rationalitaets_manifest_id.removeprefix(f'{rationalitaets_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.rationalitaets_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rationalitaets_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL)
        normen.append(
            AuktionsSenatNorm(
                auktions_senat_id=new_id,
                auktions_senat_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                auktions_weight=new_weight,
                auktions_tier=new_tier,
                canonical=is_canonical,
                auktions_ids=parent_norm.rationalitaets_ids + (new_id,),
                auktions_tags=parent_norm.rationalitaets_tags + (f"auktions-senat:{new_geltung.value}",),
            )
        )
    return AuktionsSenat(
        senat_id=senat_id,
        rationalitaets_manifest=rationalitaets_manifest,
        normen=tuple(normen),
    )
