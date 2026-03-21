"""
#346 QuantenHallManifest — Quanten-Hall-Effekt als topologisch geschütztes
Governance-Manifest: σ_xy = n·e²/h (TKNN-Invariante / Chern-Zahl) — Governance-
Kanäle am Rand des Systems laufen ohne Streuung; topologische Quantisierung
macht Governance-Rechte invariant unter kontinuierlicher Deformation.
Geltungsstufen: GESPERRT / QUANTENHALLISCH / GRUNDLEGEND_QUANTENHALLISCH
Parent: SupraleitungPakt (#345)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .supraleitung_pakt import (
    SupraleitungPakt,
    SupraleitungGeltung,
    build_supraleitung_pakt,
)

_GELTUNG_MAP: dict[SupraleitungGeltung, "QuantenHallGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SupraleitungGeltung.GESPERRT] = QuantenHallGeltung.GESPERRT
    _GELTUNG_MAP[SupraleitungGeltung.SUPRALEITEND] = QuantenHallGeltung.QUANTENHALLISCH
    _GELTUNG_MAP[SupraleitungGeltung.GRUNDLEGEND_SUPRALEITEND] = QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH


class QuantenHallTyp(Enum):
    SCHUTZ_QUANTEN_HALL = "schutz-quanten-hall"
    ORDNUNGS_QUANTEN_HALL = "ordnungs-quanten-hall"
    SOUVERAENITAETS_QUANTEN_HALL = "souveraenitaets-quanten-hall"


class QuantenHallProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenHallGeltung(Enum):
    GESPERRT = "gesperrt"
    QUANTENHALLISCH = "quantenhallisch"
    GRUNDLEGEND_QUANTENHALLISCH = "grundlegend-quantenhallisch"


_init_map()

_TYP_MAP: dict[QuantenHallGeltung, QuantenHallTyp] = {
    QuantenHallGeltung.GESPERRT: QuantenHallTyp.SCHUTZ_QUANTEN_HALL,
    QuantenHallGeltung.QUANTENHALLISCH: QuantenHallTyp.ORDNUNGS_QUANTEN_HALL,
    QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH: QuantenHallTyp.SOUVERAENITAETS_QUANTEN_HALL,
}

_PROZEDUR_MAP: dict[QuantenHallGeltung, QuantenHallProzedur] = {
    QuantenHallGeltung.GESPERRT: QuantenHallProzedur.NOTPROZEDUR,
    QuantenHallGeltung.QUANTENHALLISCH: QuantenHallProzedur.REGELPROTOKOLL,
    QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH: QuantenHallProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[QuantenHallGeltung, float] = {
    QuantenHallGeltung.GESPERRT: 0.0,
    QuantenHallGeltung.QUANTENHALLISCH: 0.04,
    QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH: 0.08,
}

_TIER_DELTA: dict[QuantenHallGeltung, int] = {
    QuantenHallGeltung.GESPERRT: 0,
    QuantenHallGeltung.QUANTENHALLISCH: 1,
    QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuantenHallNorm:
    quanten_hall_manifest_id: str
    quanten_hall_typ: QuantenHallTyp
    prozedur: QuantenHallProzedur
    geltung: QuantenHallGeltung
    quanten_hall_weight: float
    quanten_hall_tier: int
    canonical: bool
    quanten_hall_ids: tuple[str, ...]
    quanten_hall_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenHallManifest:
    manifest_id: str
    supraleitung_pakt: SupraleitungPakt
    normen: tuple[QuantenHallNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_hall_manifest_id for n in self.normen if n.geltung is QuantenHallGeltung.GESPERRT)

    @property
    def quantenhallisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_hall_manifest_id for n in self.normen if n.geltung is QuantenHallGeltung.QUANTENHALLISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_hall_manifest_id for n in self.normen if n.geltung is QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is QuantenHallGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is QuantenHallGeltung.QUANTENHALLISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-quantenhallisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-quantenhallisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_quanten_hall_manifest(
    supraleitung_pakt: SupraleitungPakt | None = None,
    *,
    manifest_id: str = "quanten-hall-manifest",
) -> QuantenHallManifest:
    if supraleitung_pakt is None:
        supraleitung_pakt = build_supraleitung_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[QuantenHallNorm] = []
    for parent_norm in supraleitung_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.supraleitung_pakt_id.removeprefix(f'{supraleitung_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.supraleitung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.supraleitung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenHallGeltung.GRUNDLEGEND_QUANTENHALLISCH)
        normen.append(
            QuantenHallNorm(
                quanten_hall_manifest_id=new_id,
                quanten_hall_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                quanten_hall_weight=new_weight,
                quanten_hall_tier=new_tier,
                canonical=is_canonical,
                quanten_hall_ids=parent_norm.supraleitung_ids + (new_id,),
                quanten_hall_tags=parent_norm.supraleitung_tags + (f"quanten-hall:{new_geltung.value}",),
            )
        )
    return QuantenHallManifest(
        manifest_id=manifest_id,
        supraleitung_pakt=supraleitung_pakt,
        normen=tuple(normen),
    )
