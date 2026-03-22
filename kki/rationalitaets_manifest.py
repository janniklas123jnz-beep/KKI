"""
#446 RationalitaetsManifest — Begrenzte Rationalität: Simon und Heuristiken.
Simon (1955): Bounded Rationality — Satisficing statt Maximieren. Nobel 1978.
Gigerenzer (1999): Ökologische Rationalität — Heuristiken sind oft optimal, nicht irrational.
Kahneman (2011): System 1 (schnell/intuitiv) vs. System 2 (langsam/analytisch). Denken.
Leitsterns Agenten nutzen adaptive Heuristiken: schnell, kontextsensitiv, ressourcenschonend.
Geltungsstufen: GESPERRT / RATIONAL / GRUNDLEGEND_RATIONAL
Parent: EntscheidungsPakt (#445)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entscheidungs_pakt import (
    EntscheidungsPakt,
    EntscheidungsPaktGeltung,
    build_entscheidungs_pakt,
)

_GELTUNG_MAP: dict[EntscheidungsPaktGeltung, "RationalitaetsManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EntscheidungsPaktGeltung.GESPERRT] = RationalitaetsManifestGeltung.GESPERRT
    _GELTUNG_MAP[EntscheidungsPaktGeltung.ENTSCHEIDEND] = RationalitaetsManifestGeltung.RATIONAL
    _GELTUNG_MAP[EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND] = RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL


class RationalitaetsManifestTyp(Enum):
    SCHUTZ_RATIONALITAET = "schutz-rationalitaet"
    ORDNUNGS_RATIONALITAET = "ordnungs-rationalitaet"
    SOUVERAENITAETS_RATIONALITAET = "souveraenitaets-rationalitaet"


class RationalitaetsManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RationalitaetsManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    RATIONAL = "rational"
    GRUNDLEGEND_RATIONAL = "grundlegend-rational"


_init_map()

_TYP_MAP: dict[RationalitaetsManifestGeltung, RationalitaetsManifestTyp] = {
    RationalitaetsManifestGeltung.GESPERRT: RationalitaetsManifestTyp.SCHUTZ_RATIONALITAET,
    RationalitaetsManifestGeltung.RATIONAL: RationalitaetsManifestTyp.ORDNUNGS_RATIONALITAET,
    RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL: RationalitaetsManifestTyp.SOUVERAENITAETS_RATIONALITAET,
}

_PROZEDUR_MAP: dict[RationalitaetsManifestGeltung, RationalitaetsManifestProzedur] = {
    RationalitaetsManifestGeltung.GESPERRT: RationalitaetsManifestProzedur.NOTPROZEDUR,
    RationalitaetsManifestGeltung.RATIONAL: RationalitaetsManifestProzedur.REGELPROTOKOLL,
    RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL: RationalitaetsManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RationalitaetsManifestGeltung, float] = {
    RationalitaetsManifestGeltung.GESPERRT: 0.0,
    RationalitaetsManifestGeltung.RATIONAL: 0.04,
    RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL: 0.08,
}

_TIER_DELTA: dict[RationalitaetsManifestGeltung, int] = {
    RationalitaetsManifestGeltung.GESPERRT: 0,
    RationalitaetsManifestGeltung.RATIONAL: 1,
    RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RationalitaetsManifestNorm:
    rationalitaets_manifest_id: str
    rationalitaets_manifest_typ: RationalitaetsManifestTyp
    prozedur: RationalitaetsManifestProzedur
    geltung: RationalitaetsManifestGeltung
    rationalitaets_weight: float
    rationalitaets_tier: int
    canonical: bool
    rationalitaets_ids: tuple[str, ...]
    rationalitaets_tags: tuple[str, ...]


@dataclass(frozen=True)
class RationalitaetsManifest:
    manifest_id: str
    entscheidungs_pakt: EntscheidungsPakt
    normen: tuple[RationalitaetsManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rationalitaets_manifest_id for n in self.normen if n.geltung is RationalitaetsManifestGeltung.GESPERRT)

    @property
    def rational_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rationalitaets_manifest_id for n in self.normen if n.geltung is RationalitaetsManifestGeltung.RATIONAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rationalitaets_manifest_id for n in self.normen if n.geltung is RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL)

    @property
    def manifest_signal(self):
        if any(n.geltung is RationalitaetsManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is RationalitaetsManifestGeltung.RATIONAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-rational")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-rational")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_rationalitaets_manifest(
    entscheidungs_pakt: EntscheidungsPakt | None = None,
    *,
    manifest_id: str = "rationalitaets-manifest",
) -> RationalitaetsManifest:
    if entscheidungs_pakt is None:
        entscheidungs_pakt = build_entscheidungs_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[RationalitaetsManifestNorm] = []
    for parent_norm in entscheidungs_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.entscheidungs_pakt_id.removeprefix(f'{entscheidungs_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.entscheidungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.entscheidungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RationalitaetsManifestGeltung.GRUNDLEGEND_RATIONAL)
        normen.append(
            RationalitaetsManifestNorm(
                rationalitaets_manifest_id=new_id,
                rationalitaets_manifest_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rationalitaets_weight=new_weight,
                rationalitaets_tier=new_tier,
                canonical=is_canonical,
                rationalitaets_ids=parent_norm.entscheidungs_ids + (new_id,),
                rationalitaets_tags=parent_norm.entscheidungs_tags + (f"rationalitaets-manifest:{new_geltung.value}",),
            )
        )
    return RationalitaetsManifest(
        manifest_id=manifest_id,
        entscheidungs_pakt=entscheidungs_pakt,
        normen=tuple(normen),
    )
