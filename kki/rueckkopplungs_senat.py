"""
#427 RueckkopplungsSenat — Rückkopplung: negative und positive Feedback-Schleifen.
Negative Rückkopplung: Abweichung vom Sollwert → Gegensteuerung → Stabilisierung.
Positive Rückkopplung: Verstärkung von Abweichungen → Wachstum oder Kipppunkt.
Lorenz (1963): Schmetterlingseffekt. Autopoietische Netzwerke: Rückkopplung erzeugt
Selbsterhaltung. Leitsterns adaptive Rückkopplung.
Geltungsstufen: GESPERRT / RUECKGEKOPPELT / GRUNDLEGEND_RUECKGEKOPPELT
Parent: SelbstregulationsManifest (#426)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .selbstregulations_manifest import (
    SelbstregulationsManifest,
    SelbstregulationsManifestGeltung,
    build_selbstregulations_manifest,
)

_GELTUNG_MAP: dict[SelbstregulationsManifestGeltung, "RueckkopplungsSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SelbstregulationsManifestGeltung.GESPERRT] = RueckkopplungsSenatGeltung.GESPERRT
    _GELTUNG_MAP[SelbstregulationsManifestGeltung.SELBSTREGULIERT] = RueckkopplungsSenatGeltung.RUECKGEKOPPELT
    _GELTUNG_MAP[SelbstregulationsManifestGeltung.GRUNDLEGEND_SELBSTREGULIERT] = RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT


class RueckkopplungsSenatTyp(Enum):
    SCHUTZ_RUECKKOPPLUNG = "schutz-rueckkopplung"
    ORDNUNGS_RUECKKOPPLUNG = "ordnungs-rueckkopplung"
    SOUVERAENITAETS_RUECKKOPPLUNG = "souveraenitaets-rueckkopplung"


class RueckkopplungsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RueckkopplungsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    RUECKGEKOPPELT = "rueckgekoppelt"
    GRUNDLEGEND_RUECKGEKOPPELT = "grundlegend-rueckgekoppelt"


_init_map()

_TYP_MAP: dict[RueckkopplungsSenatGeltung, RueckkopplungsSenatTyp] = {
    RueckkopplungsSenatGeltung.GESPERRT: RueckkopplungsSenatTyp.SCHUTZ_RUECKKOPPLUNG,
    RueckkopplungsSenatGeltung.RUECKGEKOPPELT: RueckkopplungsSenatTyp.ORDNUNGS_RUECKKOPPLUNG,
    RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT: RueckkopplungsSenatTyp.SOUVERAENITAETS_RUECKKOPPLUNG,
}

_PROZEDUR_MAP: dict[RueckkopplungsSenatGeltung, RueckkopplungsSenatProzedur] = {
    RueckkopplungsSenatGeltung.GESPERRT: RueckkopplungsSenatProzedur.NOTPROZEDUR,
    RueckkopplungsSenatGeltung.RUECKGEKOPPELT: RueckkopplungsSenatProzedur.REGELPROTOKOLL,
    RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT: RueckkopplungsSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RueckkopplungsSenatGeltung, float] = {
    RueckkopplungsSenatGeltung.GESPERRT: 0.0,
    RueckkopplungsSenatGeltung.RUECKGEKOPPELT: 0.04,
    RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT: 0.08,
}

_TIER_DELTA: dict[RueckkopplungsSenatGeltung, int] = {
    RueckkopplungsSenatGeltung.GESPERRT: 0,
    RueckkopplungsSenatGeltung.RUECKGEKOPPELT: 1,
    RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RueckkopplungsSenatNorm:
    rueckkopplungs_senat_id: str
    rueckkopplung_typ: RueckkopplungsSenatTyp
    prozedur: RueckkopplungsSenatProzedur
    geltung: RueckkopplungsSenatGeltung
    rueckkopplung_weight: float
    rueckkopplung_tier: int
    canonical: bool
    rueckkopplung_ids: tuple[str, ...]
    rueckkopplung_tags: tuple[str, ...]


@dataclass(frozen=True)
class RueckkopplungsSenat:
    senat_id: str
    selbstregulations_manifest: SelbstregulationsManifest
    normen: tuple[RueckkopplungsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rueckkopplungs_senat_id for n in self.normen if n.geltung is RueckkopplungsSenatGeltung.GESPERRT)

    @property
    def rueckgekoppelt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rueckkopplungs_senat_id for n in self.normen if n.geltung is RueckkopplungsSenatGeltung.RUECKGEKOPPELT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rueckkopplungs_senat_id for n in self.normen if n.geltung is RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT)

    @property
    def senat_signal(self):
        if any(n.geltung is RueckkopplungsSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is RueckkopplungsSenatGeltung.RUECKGEKOPPELT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-rueckgekoppelt")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-rueckgekoppelt")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_rueckkopplungs_senat(
    selbstregulations_manifest: SelbstregulationsManifest | None = None,
    *,
    senat_id: str = "rueckkopplungs-senat",
) -> RueckkopplungsSenat:
    if selbstregulations_manifest is None:
        selbstregulations_manifest = build_selbstregulations_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[RueckkopplungsSenatNorm] = []
    for parent_norm in selbstregulations_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.selbstregulations_manifest_id.removeprefix(f'{selbstregulations_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.selbstregulation_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.selbstregulation_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT)
        normen.append(
            RueckkopplungsSenatNorm(
                rueckkopplungs_senat_id=new_id,
                rueckkopplung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rueckkopplung_weight=new_weight,
                rueckkopplung_tier=new_tier,
                canonical=is_canonical,
                rueckkopplung_ids=parent_norm.selbstregulation_ids + (new_id,),
                rueckkopplung_tags=parent_norm.selbstregulation_tags + (f"rueckkopplungs-senat:{new_geltung.value}",),
            )
        )
    return RueckkopplungsSenat(
        senat_id=senat_id,
        selbstregulations_manifest=selbstregulations_manifest,
        normen=tuple(normen),
    )
