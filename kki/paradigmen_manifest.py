"""
#476 ParadigmenManifest — Kuhn: Paradigmenwechsel, wissenschaftliche Revolutionen, normale Wissenschaft.
Thomas Kuhns Strukturwandel wissenschaftlicher Revolutionen beschreibt Wissenschaft als
Abfolge von Paradigmen: Normale Wissenschaft löst Rätsel im Rahmen eines herrschenden
Paradigmas, bis Anomalien eine Krise auslösen. Eine wissenschaftliche Revolution ersetzt
das alte Paradigma durch ein inkommensurables neues. Leitsterns Terra-Schwarm navigiert
Paradigmenwechsel dynamisch: GESPERRT sichert laufendes Paradigma, PARADIGMATISCH ermöglicht
Anomalieerkennung und Krisenbewältigung, GRUNDLEGEND_PARADIGMATISCH vollzieht die Revolution.
Parent: WissenschaftsPakt (#475)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wissenschafts_pakt import (
    WissenschaftsPakt,
    WissenschaftsPaktGeltung,
    build_wissenschafts_pakt,
)

_GELTUNG_MAP: dict[WissenschaftsPaktGeltung, "ParadigmenManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[WissenschaftsPaktGeltung.GESPERRT] = ParadigmenManifestGeltung.GESPERRT
    _GELTUNG_MAP[WissenschaftsPaktGeltung.WISSENSCHAFTLICH] = ParadigmenManifestGeltung.PARADIGMATISCH
    _GELTUNG_MAP[WissenschaftsPaktGeltung.GRUNDLEGEND_WISSENSCHAFTLICH] = ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH


class ParadigmenManifestTyp(Enum):
    SCHUTZ_PARADIGMA = "schutz-paradigma"
    ORDNUNGS_PARADIGMA = "ordnungs-paradigma"
    SOUVERAENITAETS_PARADIGMA = "souveraenitaets-paradigma"


class ParadigmenManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ParadigmenManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    PARADIGMATISCH = "paradigmatisch"
    GRUNDLEGEND_PARADIGMATISCH = "grundlegend-paradigmatisch"


_init_map()

_TYP_MAP = {
    ParadigmenManifestGeltung.GESPERRT: ParadigmenManifestTyp.SCHUTZ_PARADIGMA,
    ParadigmenManifestGeltung.PARADIGMATISCH: ParadigmenManifestTyp.ORDNUNGS_PARADIGMA,
    ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH: ParadigmenManifestTyp.SOUVERAENITAETS_PARADIGMA,
}
_PROZEDUR_MAP = {
    ParadigmenManifestGeltung.GESPERRT: ParadigmenManifestProzedur.NOTPROZEDUR,
    ParadigmenManifestGeltung.PARADIGMATISCH: ParadigmenManifestProzedur.REGELPROTOKOLL,
    ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH: ParadigmenManifestProzedur.PLENARPROTOKOLL,
}
_WEIGHT_DELTA = {
    ParadigmenManifestGeltung.GESPERRT: 0.0,
    ParadigmenManifestGeltung.PARADIGMATISCH: 0.04,
    ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH: 0.08,
}
_TIER_DELTA = {
    ParadigmenManifestGeltung.GESPERRT: 0,
    ParadigmenManifestGeltung.PARADIGMATISCH: 1,
    ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH: 2,
}


@dataclass(frozen=True)
class ParadigmenManifestNorm:
    paradigmen_manifest_id: str
    paradigmen_typ: ParadigmenManifestTyp
    prozedur: ParadigmenManifestProzedur
    geltung: ParadigmenManifestGeltung
    paradigmen_weight: float
    paradigmen_tier: int
    canonical: bool
    paradigmen_ids: tuple[str, ...]
    paradigmen_tags: tuple[str, ...]


@dataclass(frozen=True)
class ParadigmenManifest:
    manifest_id: str
    wissenschafts_pakt: WissenschaftsPakt
    normen: tuple[ParadigmenManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paradigmen_manifest_id for n in self.normen if n.geltung is ParadigmenManifestGeltung.GESPERRT)

    @property
    def paradigmatisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paradigmen_manifest_id for n in self.normen if n.geltung is ParadigmenManifestGeltung.PARADIGMATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paradigmen_manifest_id for n in self.normen if n.geltung is ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH)

    @property
    def manifest_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is ParadigmenManifestGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is ParadigmenManifestGeltung.PARADIGMATISCH for n in self.normen):
            return SimpleNamespace(status="manifest-paradigmatisch")
        return SimpleNamespace(status="manifest-grundlegend-paradigmatisch")


def build_paradigmen_manifest(
    wissenschafts_pakt: WissenschaftsPakt | None = None,
    *,
    manifest_id: str = "paradigmen-manifest",
) -> ParadigmenManifest:
    if wissenschafts_pakt is None:
        wissenschafts_pakt = build_wissenschafts_pakt(pakt_id=f"{manifest_id}-pakt")
    normen: list[ParadigmenManifestNorm] = []
    for parent_norm in wissenschafts_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.wissenschafts_pakt_id.removeprefix(f'{wissenschafts_pakt.pakt_id}-')}"
        is_canonical = parent_norm.canonical and (new_geltung is ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH)
        normen.append(ParadigmenManifestNorm(
            paradigmen_manifest_id=new_id,
            paradigmen_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            paradigmen_weight=round(min(1.0, parent_norm.wissenschafts_weight + _WEIGHT_DELTA[new_geltung]), 3),
            paradigmen_tier=parent_norm.wissenschafts_tier + _TIER_DELTA[new_geltung],
            canonical=is_canonical,
            paradigmen_ids=parent_norm.wissenschafts_ids + (new_id,),
            paradigmen_tags=parent_norm.wissenschafts_tags + (f"paradigmen-manifest:{new_geltung.value}",),
        ))
    return ParadigmenManifest(manifest_id=manifest_id, wissenschafts_pakt=wissenschafts_pakt, normen=tuple(normen))
