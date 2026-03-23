"""
#526 InnovationsPakt — Schumpeter/Solow/Romer Kreative Zerstörung und Wachstumstheorie

Joseph Schumpeter (1942): Kapitalismus, Sozialismus und Demokratie — Kreative Zerstörung
  als Motor des kapitalistischen Fortschritts; Unternehmer als Innovationsträger;
  technologische Disruption und Strukturwandel als permanente Eigenschaft des Schwarms.
Robert Solow (1956): A Contribution to the Theory of Economic Growth — neoklassisches
  Wachstumsmodell; technischer Fortschritt als exogene Residualgröße; Steady-State und
  Konvergenztheorem für die langfristige Entwicklung des Peta-Schwarms Leitstern.
Paul Romer (1990): Endogenous Technological Change — endogenes Wachstumsmodell;
  Humankapital und Wissensakkumulation als Wachstumstreiber; steigende Skalenerträge durch
  nicht-rivale Güter; Innovationssysteme als positive Feedback-Schleifen im Schwarm.
William Nordhaus (1969): An Economic Theory of Technological Change — Patentsystem und
  Innovationsanreize; optimale Dauer des Schutzes neuen Wissens im Schwarmkontext. ⚡
Module #526, Parent: WirtschaftsOrdnungsManifest (#525)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wirtschafts_ordnungs_manifest import (
    WirtschaftsOrdnungsManifest,
    WirtschaftsOrdnungsManifestGeltung,
    build_ordnungs_manifest,
)

_WEIGHT_DELTA: dict["InnovationsPaktGeltung", float] = {}
_TIER_DELTA: dict["InnovationsPaktGeltung", int] = {}
_TYP_MAP: dict["InnovationsPaktGeltung", "InnovationsPaktTyp"] = {}
_PROZEDUR_MAP: dict["InnovationsPaktGeltung", "InnovationsPaktProzedur"] = {}
_GELTUNG_MAP: dict[WirtschaftsOrdnungsManifestGeltung, "InnovationsPaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InnovationsPaktGeltung.GESPERRT: 0.0,
        InnovationsPaktGeltung.INNOVATIV: 0.05,
        InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV: 0.1,
    })
    _TIER_DELTA.update({
        InnovationsPaktGeltung.GESPERRT: 0,
        InnovationsPaktGeltung.INNOVATIV: 1,
        InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV: 2,
    })
    _TYP_MAP.update({
        InnovationsPaktGeltung.GESPERRT: InnovationsPaktTyp.SCHUTZ_INNOVATION,
        InnovationsPaktGeltung.INNOVATIV: InnovationsPaktTyp.ORDNUNGS_INNOVATION,
        InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV: InnovationsPaktTyp.SOUVERAENITAETS_INNOVATION,
    })
    _PROZEDUR_MAP.update({
        InnovationsPaktGeltung.GESPERRT: InnovationsPaktProzedur.NOTPROZEDUR,
        InnovationsPaktGeltung.INNOVATIV: InnovationsPaktProzedur.REGELPROTOKOLL,
        InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV: InnovationsPaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        WirtschaftsOrdnungsManifestGeltung.GESPERRT: InnovationsPaktGeltung.GESPERRT,
        WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH: InnovationsPaktGeltung.INNOVATIV,
        WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH: InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV,
    })


class InnovationsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    INNOVATIV = "innovativ"
    GRUNDLEGEND_INNOVATIV = "grundlegend-innovativ"


class InnovationsPaktTyp(Enum):
    SCHUTZ_INNOVATION = "schutz-innovation"
    ORDNUNGS_INNOVATION = "ordnungs-innovation"
    SOUVERAENITAETS_INNOVATION = "souveraenitaets-innovation"


class InnovationsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class InnovationsPaktNorm:
    innovations_pakt_id: str
    innovations_typ: InnovationsPaktTyp
    prozedur: InnovationsPaktProzedur
    geltung: InnovationsPaktGeltung
    innovations_weight: float
    innovations_tier: int
    canonical: bool
    innovations_ids: tuple[str, ...]
    innovations_tags: tuple[str, ...]


@dataclass(frozen=True)
class InnovationsPakt:
    pakt_id: str
    ordnungs_manifest: WirtschaftsOrdnungsManifest
    normen: tuple[InnovationsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.innovations_pakt_id for n in self.normen if n.geltung is InnovationsPaktGeltung.GESPERRT)

    @property
    def innovativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.innovations_pakt_id for n in self.normen if n.geltung is InnovationsPaktGeltung.INNOVATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.innovations_pakt_id for n in self.normen if n.geltung is InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV)

    @property
    def pakt_signal(self):
        if any(n.geltung is InnovationsPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is InnovationsPaktGeltung.INNOVATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-innovativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-innovativ")


_init_map()


def build_innovations_pakt(
    ordnungs_manifest: WirtschaftsOrdnungsManifest | None = None,
    *,
    pakt_id: str = "innovations-pakt",
) -> InnovationsPakt:
    if ordnungs_manifest is None:
        ordnungs_manifest = build_ordnungs_manifest(
            manifest_id=f"{pakt_id}-ordnungs-manifest"
        )

    normen: list[InnovationsPaktNorm] = []
    for parent_norm in ordnungs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.ordnungs_manifest_id.removeprefix(f'{ordnungs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.ordnungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.ordnungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV)
        normen.append(
            InnovationsPaktNorm(
                innovations_pakt_id=new_id,
                innovations_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                innovations_weight=new_weight,
                innovations_tier=new_tier,
                canonical=is_canonical,
                innovations_ids=parent_norm.ordnungs_ids + (new_id,),
                innovations_tags=parent_norm.ordnungs_tags + (f"innovations-pakt:{new_geltung.value}",),
            )
        )
    return InnovationsPakt(
        pakt_id=pakt_id,
        ordnungs_manifest=ordnungs_manifest,
        normen=tuple(normen),
    )
