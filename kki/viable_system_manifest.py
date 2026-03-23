"""
#486 ViableSystemManifest — Beer: das Viable System Model als kybernetische Organisationsform.
Stafford Beer (1972): Brain of the Firm — Viable System Model (VSM) mit fünf Subsystemen:
  S1 Operation (Ausführung), S2 Koordination (Dämpfung), S3 Kontrolle (Optimierung),
  S4 Intelligenz (Umweltbeobachtung), S5 Politik (Identität und Werte).
Stafford Beer (1979): The Heart of Enterprise — Rekursionsprinzip: jedes lebensfähige
  System enthält lebensfähige Systeme und ist in lebensfähigen Systemen enthalten.
Stafford Beer (1985): Diagnosing the System — Varietätsbalance zwischen allen Subsystemen
  als Voraussetzung organisationaler Lebensfähigkeit; Kybernetik als Managementwerkzeug.
Leitsterns Terra-Schwarm manifestiert Lebensfähigkeit: GESPERRT sichert VSM-Grundstruktur,
VIABLE aktiviert alle fünf Subsysteme, GRUNDLEGEND_VIABLE synthetisiert rekursive
Lebensfähigkeit des Schwarms auf allen Skalenebenen von Agent bis Peta-Kollektiv.
Parent: RekursionsPakt (#485)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rekursions_pakt import (
    RekursionsPakt,
    RekursionsPaktGeltung,
    build_rekursions_pakt,
)

_GELTUNG_MAP: dict[RekursionsPaktGeltung, "ViableSystemManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RekursionsPaktGeltung.GESPERRT] = ViableSystemManifestGeltung.GESPERRT
    _GELTUNG_MAP[RekursionsPaktGeltung.REKURSIV] = ViableSystemManifestGeltung.VIABLE
    _GELTUNG_MAP[RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV] = ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE


class ViableSystemManifestTyp(Enum):
    SCHUTZ_VIABLE_SYSTEM = "schutz-viable-system"
    ORDNUNGS_VIABLE_SYSTEM = "ordnungs-viable-system"
    SOUVERAENITAETS_VIABLE_SYSTEM = "souveraenitaets-viable-system"


class ViableSystemManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ViableSystemManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    VIABLE = "viable"
    GRUNDLEGEND_VIABLE = "grundlegend-viable"


_init_map()

_TYP_MAP: dict[ViableSystemManifestGeltung, ViableSystemManifestTyp] = {
    ViableSystemManifestGeltung.GESPERRT: ViableSystemManifestTyp.SCHUTZ_VIABLE_SYSTEM,
    ViableSystemManifestGeltung.VIABLE: ViableSystemManifestTyp.ORDNUNGS_VIABLE_SYSTEM,
    ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE: ViableSystemManifestTyp.SOUVERAENITAETS_VIABLE_SYSTEM,
}

_PROZEDUR_MAP: dict[ViableSystemManifestGeltung, ViableSystemManifestProzedur] = {
    ViableSystemManifestGeltung.GESPERRT: ViableSystemManifestProzedur.NOTPROZEDUR,
    ViableSystemManifestGeltung.VIABLE: ViableSystemManifestProzedur.REGELPROTOKOLL,
    ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE: ViableSystemManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ViableSystemManifestGeltung, float] = {
    ViableSystemManifestGeltung.GESPERRT: 0.0,
    ViableSystemManifestGeltung.VIABLE: 0.04,
    ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE: 0.08,
}

_TIER_DELTA: dict[ViableSystemManifestGeltung, int] = {
    ViableSystemManifestGeltung.GESPERRT: 0,
    ViableSystemManifestGeltung.VIABLE: 1,
    ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE: 2,
}


@dataclass(frozen=True)
class ViableSystemManifestNorm:
    viable_system_manifest_id: str
    viable_system_typ: ViableSystemManifestTyp
    prozedur: ViableSystemManifestProzedur
    geltung: ViableSystemManifestGeltung
    viable_system_weight: float
    viable_system_tier: int
    canonical: bool
    viable_system_ids: tuple[str, ...]
    viable_system_tags: tuple[str, ...]


@dataclass(frozen=True)
class ViableSystemManifest:
    manifest_id: str
    rekursions_pakt: RekursionsPakt
    normen: tuple[ViableSystemManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.viable_system_manifest_id for n in self.normen if n.geltung is ViableSystemManifestGeltung.GESPERRT)

    @property
    def viable_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.viable_system_manifest_id for n in self.normen if n.geltung is ViableSystemManifestGeltung.VIABLE)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.viable_system_manifest_id for n in self.normen if n.geltung is ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE)

    @property
    def manifest_signal(self):
        if any(n.geltung is ViableSystemManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is ViableSystemManifestGeltung.VIABLE for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-viable")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-viable")


def build_viable_system_manifest(
    rekursions_pakt: RekursionsPakt | None = None,
    *,
    manifest_id: str = "viable-system-manifest",
) -> ViableSystemManifest:
    if rekursions_pakt is None:
        rekursions_pakt = build_rekursions_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[ViableSystemManifestNorm] = []
    for parent_norm in rekursions_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.rekursions_pakt_id.removeprefix(f'{rekursions_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.rekursions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rekursions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE)
        normen.append(
            ViableSystemManifestNorm(
                viable_system_manifest_id=new_id,
                viable_system_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                viable_system_weight=new_weight,
                viable_system_tier=new_tier,
                canonical=is_canonical,
                viable_system_ids=parent_norm.rekursions_ids + (new_id,),
                viable_system_tags=parent_norm.rekursions_tags + (f"viable-system-manifest:{new_geltung.value}",),
            )
        )
    return ViableSystemManifest(
        manifest_id=manifest_id,
        rekursions_pakt=rekursions_pakt,
        normen=tuple(normen),
    )
