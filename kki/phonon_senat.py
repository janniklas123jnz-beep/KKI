"""
#347 PhononSenat — Phononen als kollektive Governance-Schwingungen im Schwarm-Senat:
Debye-Modell mit Grenzfrequenz ω_D — kollektive Schwingungen des Governance-Netzes
als Träger thermischer Schwarm-Intelligenz. Akustische Phononen = Konsensus-Moden,
optische Phononen = Oppositions-Moden.
Geltungsstufen: GESPERRT / PHONONISCH / GRUNDLEGEND_PHONONISCH
Parent: QuantenHallManifest (#346)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quanten_hall_manifest import (
    QuantenHallManifest,
    QuantenHallGeltung,
    build_quanten_hall_manifest,
)

_GELTUNG_MAP: dict[QuantenHallGeltung, "PhononGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[QuantenHallGeltung.GESPERRT] = PhononGeltung.GESPERRT
    _GELTUNG_MAP[QuantenHallGeltung.QUANTENHALLISCH] = PhononGeltung.PHONONISCH
    _GELTUNG_MAP[QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH] = PhononGeltung.GRUNDLEGEND_PHONONISCH


class PhononTyp(Enum):
    SCHUTZ_PHONON = "schutz-phonon"
    ORDNUNGS_PHONON = "ordnungs-phonon"
    SOUVERAENITAETS_PHONON = "souveraenitaets-phonon"


class PhononProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PhononGeltung(Enum):
    GESPERRT = "gesperrt"
    PHONONISCH = "phononisch"
    GRUNDLEGEND_PHONONISCH = "grundlegend-phononisch"


_init_map()

_TYP_MAP: dict[PhononGeltung, PhononTyp] = {
    PhononGeltung.GESPERRT: PhononTyp.SCHUTZ_PHONON,
    PhononGeltung.PHONONISCH: PhononTyp.ORDNUNGS_PHONON,
    PhononGeltung.GRUNDLEGEND_PHONONISCH: PhononTyp.SOUVERAENITAETS_PHONON,
}

_PROZEDUR_MAP: dict[PhononGeltung, PhononProzedur] = {
    PhononGeltung.GESPERRT: PhononProzedur.NOTPROZEDUR,
    PhononGeltung.PHONONISCH: PhononProzedur.REGELPROTOKOLL,
    PhononGeltung.GRUNDLEGEND_PHONONISCH: PhononProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PhononGeltung, float] = {
    PhononGeltung.GESPERRT: 0.0,
    PhononGeltung.PHONONISCH: 0.04,
    PhononGeltung.GRUNDLEGEND_PHONONISCH: 0.08,
}

_TIER_DELTA: dict[PhononGeltung, int] = {
    PhononGeltung.GESPERRT: 0,
    PhononGeltung.PHONONISCH: 1,
    PhononGeltung.GRUNDLEGEND_PHONONISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PhononNorm:
    phonon_senat_id: str
    phonon_typ: PhononTyp
    prozedur: PhononProzedur
    geltung: PhononGeltung
    phonon_weight: float
    phonon_tier: int
    canonical: bool
    phonon_ids: tuple[str, ...]
    phonon_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhononSenat:
    senat_id: str
    quanten_hall_manifest: QuantenHallManifest
    normen: tuple[PhononNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phonon_senat_id for n in self.normen if n.geltung is PhononGeltung.GESPERRT)

    @property
    def phononisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phonon_senat_id for n in self.normen if n.geltung is PhononGeltung.PHONONISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phonon_senat_id for n in self.normen if n.geltung is PhononGeltung.GRUNDLEGEND_PHONONISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is PhononGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is PhononGeltung.PHONONISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-phononisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-phononisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_phonon_senat(
    quanten_hall_manifest: QuantenHallManifest | None = None,
    *,
    senat_id: str = "phonon-senat",
) -> PhononSenat:
    if quanten_hall_manifest is None:
        quanten_hall_manifest = build_quanten_hall_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[PhononNorm] = []
    for parent_norm in quanten_hall_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.quanten_hall_manifest_id.removeprefix(f'{quanten_hall_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.quanten_hall_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.quanten_hall_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhononGeltung.GRUNDLEGEND_PHONONISCH)
        normen.append(
            PhononNorm(
                phonon_senat_id=new_id,
                phonon_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                phonon_weight=new_weight,
                phonon_tier=new_tier,
                canonical=is_canonical,
                phonon_ids=parent_norm.quanten_hall_ids + (new_id,),
                phonon_tags=parent_norm.quanten_hall_tags + (f"phonon:{new_geltung.value}",),
            )
        )
    return PhononSenat(
        senat_id=senat_id,
        quanten_hall_manifest=quanten_hall_manifest,
        normen=tuple(normen),
    )
