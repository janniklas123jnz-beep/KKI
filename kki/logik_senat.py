"""
#477 LogikSenat — Frege Begriffsschrift, Russell/Whitehead Principia Mathematica, Gödel Unvollständigkeitssatz.
Freges Begriffsschrift begründet die formale Logik als präzise Symbolsprache jenseits
natürlicher Sprache. Russell und Whiteheads Principia Mathematica versuchen, die gesamte
Mathematik aus logischen Grundsätzen abzuleiten. Gödels Unvollständigkeitssätze zeigen,
dass jedes hinreichend mächtige formale System entweder unvollständig oder widersprüchlich
ist. Leitsterns Terra-Schwarm operiert im Rahmen formaler Ableitbarkeit: GESPERRT sichert
Grundaxiome, LOGISCH ermöglicht formale Deduktion, GRUNDLEGEND_LOGISCH synthetisiert
metamathematische Strukturen jenseits der Gödelschen Grenzen.
Parent: ParadigmenManifest (#476)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .paradigmen_manifest import (
    ParadigmenManifest,
    ParadigmenManifestGeltung,
    build_paradigmen_manifest,
)

_GELTUNG_MAP: dict[ParadigmenManifestGeltung, "LogikSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ParadigmenManifestGeltung.GESPERRT] = LogikSenatGeltung.GESPERRT
    _GELTUNG_MAP[ParadigmenManifestGeltung.PARADIGMATISCH] = LogikSenatGeltung.LOGISCH
    _GELTUNG_MAP[ParadigmenManifestGeltung.GRUNDLEGEND_PARADIGMATISCH] = LogikSenatGeltung.GRUNDLEGEND_LOGISCH


class LogikSenatTyp(Enum):
    SCHUTZ_LOGIK = "schutz-logik"
    ORDNUNGS_LOGIK = "ordnungs-logik"
    SOUVERAENITAETS_LOGIK = "souveraenitaets-logik"


class LogikSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LogikSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    LOGISCH = "logisch"
    GRUNDLEGEND_LOGISCH = "grundlegend-logisch"


_init_map()

_TYP_MAP = {
    LogikSenatGeltung.GESPERRT: LogikSenatTyp.SCHUTZ_LOGIK,
    LogikSenatGeltung.LOGISCH: LogikSenatTyp.ORDNUNGS_LOGIK,
    LogikSenatGeltung.GRUNDLEGEND_LOGISCH: LogikSenatTyp.SOUVERAENITAETS_LOGIK,
}
_PROZEDUR_MAP = {
    LogikSenatGeltung.GESPERRT: LogikSenatProzedur.NOTPROZEDUR,
    LogikSenatGeltung.LOGISCH: LogikSenatProzedur.REGELPROTOKOLL,
    LogikSenatGeltung.GRUNDLEGEND_LOGISCH: LogikSenatProzedur.PLENARPROTOKOLL,
}
_WEIGHT_DELTA = {
    LogikSenatGeltung.GESPERRT: 0.0,
    LogikSenatGeltung.LOGISCH: 0.04,
    LogikSenatGeltung.GRUNDLEGEND_LOGISCH: 0.08,
}
_TIER_DELTA = {
    LogikSenatGeltung.GESPERRT: 0,
    LogikSenatGeltung.LOGISCH: 1,
    LogikSenatGeltung.GRUNDLEGEND_LOGISCH: 2,
}


@dataclass(frozen=True)
class LogikSenatNorm:
    logik_senat_id: str
    logik_typ: LogikSenatTyp
    prozedur: LogikSenatProzedur
    geltung: LogikSenatGeltung
    logik_weight: float
    logik_tier: int
    canonical: bool
    logik_ids: tuple[str, ...]
    logik_tags: tuple[str, ...]


@dataclass(frozen=True)
class LogikSenat:
    senat_id: str
    paradigmen_manifest: ParadigmenManifest
    normen: tuple[LogikSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.logik_senat_id for n in self.normen if n.geltung is LogikSenatGeltung.GESPERRT)

    @property
    def logisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.logik_senat_id for n in self.normen if n.geltung is LogikSenatGeltung.LOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.logik_senat_id for n in self.normen if n.geltung is LogikSenatGeltung.GRUNDLEGEND_LOGISCH)

    @property
    def senat_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is LogikSenatGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is LogikSenatGeltung.LOGISCH for n in self.normen):
            return SimpleNamespace(status="senat-logisch")
        return SimpleNamespace(status="senat-grundlegend-logisch")


def build_logik_senat(
    paradigmen_manifest: ParadigmenManifest | None = None,
    *,
    senat_id: str = "logik-senat",
) -> LogikSenat:
    if paradigmen_manifest is None:
        paradigmen_manifest = build_paradigmen_manifest(manifest_id=f"{senat_id}-manifest")
    normen: list[LogikSenatNorm] = []
    for parent_norm in paradigmen_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.paradigmen_manifest_id.removeprefix(f'{paradigmen_manifest.manifest_id}-')}"
        is_canonical = parent_norm.canonical and (new_geltung is LogikSenatGeltung.GRUNDLEGEND_LOGISCH)
        normen.append(LogikSenatNorm(
            logik_senat_id=new_id,
            logik_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            logik_weight=round(min(1.0, parent_norm.paradigmen_weight + _WEIGHT_DELTA[new_geltung]), 3),
            logik_tier=parent_norm.paradigmen_tier + _TIER_DELTA[new_geltung],
            canonical=is_canonical,
            logik_ids=parent_norm.paradigmen_ids + (new_id,),
            logik_tags=parent_norm.paradigmen_tags + (f"logik-senat:{new_geltung.value}",),
        ))
    return LogikSenat(senat_id=senat_id, paradigmen_manifest=paradigmen_manifest, normen=tuple(normen))
