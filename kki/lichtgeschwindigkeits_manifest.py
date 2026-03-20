"""#296 – LichtgeschwindigkeitsManifest: Lichtgeschwindigkeit als Governance-Manifest.

Parent: wellenausbreitung_pakt (#295)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wellenausbreitung_pakt import (
    WellenausbreitungsGeltung,
    WellenausbreitungsPakt,
    build_wellenausbreitung_pakt,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LichtgeschwindigkeitsTyp(Enum):
    SCHUTZ_LICHTGESCHWINDIGKEIT = "schutz-lichtgeschwindigkeit"
    ORDNUNGS_LICHTGESCHWINDIGKEIT = "ordnungs-lichtgeschwindigkeit"
    SOUVERAENITAETS_LICHTGESCHWINDIGKEIT = "souveraenitaets-lichtgeschwindigkeit"


class LichtgeschwindigkeitsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LichtgeschwindigkeitsGeltung(Enum):
    GESPERRT = "gesperrt"
    LICHTSCHNELL = "lichtschnell"
    GRUNDLEGEND_LICHTSCHNELL = "grundlegend-lichtschnell"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[WellenausbreitungsGeltung, LichtgeschwindigkeitsGeltung] = {
    WellenausbreitungsGeltung.GESPERRT: LichtgeschwindigkeitsGeltung.GESPERRT,
    WellenausbreitungsGeltung.WELLENAUSBREITEND: LichtgeschwindigkeitsGeltung.LICHTSCHNELL,
    WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND: LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL,
}

_TYP_MAP: dict[WellenausbreitungsGeltung, LichtgeschwindigkeitsTyp] = {
    WellenausbreitungsGeltung.GESPERRT: LichtgeschwindigkeitsTyp.SCHUTZ_LICHTGESCHWINDIGKEIT,
    WellenausbreitungsGeltung.WELLENAUSBREITEND: LichtgeschwindigkeitsTyp.ORDNUNGS_LICHTGESCHWINDIGKEIT,
    WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND: LichtgeschwindigkeitsTyp.SOUVERAENITAETS_LICHTGESCHWINDIGKEIT,
}

_PROZEDUR_MAP: dict[WellenausbreitungsGeltung, LichtgeschwindigkeitsProzedur] = {
    WellenausbreitungsGeltung.GESPERRT: LichtgeschwindigkeitsProzedur.NOTPROZEDUR,
    WellenausbreitungsGeltung.WELLENAUSBREITEND: LichtgeschwindigkeitsProzedur.REGELPROTOKOLL,
    WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND: LichtgeschwindigkeitsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[WellenausbreitungsGeltung, float] = {
    WellenausbreitungsGeltung.GESPERRT: 0.0,
    WellenausbreitungsGeltung.WELLENAUSBREITEND: 0.04,
    WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND: 0.08,
}

_TIER_BONUS: dict[WellenausbreitungsGeltung, int] = {
    WellenausbreitungsGeltung.GESPERRT: 0,
    WellenausbreitungsGeltung.WELLENAUSBREITEND: 1,
    WellenausbreitungsGeltung.GRUNDLEGEND_WELLENAUSBREITEND: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LichtgeschwindigkeitsNorm:
    lichtgeschwindigkeits_manifest_id: str
    lichtgeschwindigkeits_typ: LichtgeschwindigkeitsTyp
    prozedur: LichtgeschwindigkeitsProzedur
    geltung: LichtgeschwindigkeitsGeltung
    lichtgeschwindigkeits_weight: float
    lichtgeschwindigkeits_tier: int
    canonical: bool
    lichtgeschwindigkeits_ids: tuple[str, ...]
    lichtgeschwindigkeits_tags: tuple[str, ...]


@dataclass(frozen=True)
class LichtgeschwindigkeitsManifest:
    manifest_id: str
    wellenausbreitung_pakt: WellenausbreitungsPakt
    normen: tuple[LichtgeschwindigkeitsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lichtgeschwindigkeits_manifest_id for n in self.normen if n.geltung is LichtgeschwindigkeitsGeltung.GESPERRT)

    @property
    def lichtschnell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lichtgeschwindigkeits_manifest_id for n in self.normen if n.geltung is LichtgeschwindigkeitsGeltung.LICHTSCHNELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lichtgeschwindigkeits_manifest_id for n in self.normen if n.geltung is LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL)

    @property
    def manifest_signal(self):
        if any(n.geltung is LichtgeschwindigkeitsGeltung.GESPERRT for n in self.normen):
            status = "manifest-gesperrt"
            severity = "critical"
        elif any(n.geltung is LichtgeschwindigkeitsGeltung.LICHTSCHNELL for n in self.normen):
            status = "manifest-lichtschnell"
            severity = "warning"
        else:
            status = "manifest-grundlegend-lichtschnell"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_lichtgeschwindigkeits_manifest(
    wellenausbreitung_pakt: WellenausbreitungsPakt | None = None,
    *,
    manifest_id: str = "lichtgeschwindigkeits-manifest",
) -> LichtgeschwindigkeitsManifest:
    if wellenausbreitung_pakt is None:
        wellenausbreitung_pakt = build_wellenausbreitung_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[LichtgeschwindigkeitsNorm] = []
    for parent_norm in wellenausbreitung_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{manifest_id}-{parent_norm.wellenausbreitung_pakt_id.removeprefix(f'{wellenausbreitung_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.wellenausbreitung_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.wellenausbreitung_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL)
        normen.append(
            LichtgeschwindigkeitsNorm(
                lichtgeschwindigkeits_manifest_id=new_id,
                lichtgeschwindigkeits_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                lichtgeschwindigkeits_weight=raw_weight,
                lichtgeschwindigkeits_tier=new_tier,
                canonical=is_canonical,
                lichtgeschwindigkeits_ids=parent_norm.wellenausbreitung_ids + (new_id,),
                lichtgeschwindigkeits_tags=parent_norm.wellenausbreitung_tags + (f"lichtgeschwindigkeits-manifest:{new_geltung.value}",),
            )
        )

    return LichtgeschwindigkeitsManifest(
        manifest_id=manifest_id,
        wellenausbreitung_pakt=wellenausbreitung_pakt,
        normen=tuple(normen),
    )
