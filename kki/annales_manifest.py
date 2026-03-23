"""
#545 AnnalesManifest — Manifest der Strukturgeschichte und Annales-Schule

Marc Bloch & Lucien Febvre (1929): Gründung der Annales d'histoire économique et sociale;
  Revolution der Geschichtswissenschaft durch Einbeziehung von Wirtschaft, Gesellschaft und Mentalität;
  Problemgeschichte statt Ereignisgeschichte als methodologisches Leitprinzip der Schule.
Fernand Braudel (1949): La Méditerranée — Longue durée als dreigliedrige Zeitstruktur;
  Unterscheidung von geographischer, sozialer und ereignishafter Zeit als analytisches Instrument;
  Mediterrane Welt als Modell der strukturgeschichtlichen Totalanalyse historischer Räume.
Emmanuel Le Roy Ladurie (1967): Les Paysans de Languedoc — Klimageschichte und Agrarstrukturen;
  Quantitative Methoden und Seriengeschichte als Erweiterung der Annales-Programmatik;
  Mikro- und Makrogeschichte als komplementäre Ebenen strukturgeschichtlicher Analyse.
Parent: EpochenKodex (#544)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .epochen_kodex import (
    EpochenKodex,
    EpochenKodexGeltung,
    build_epochen_kodex,
)

_WEIGHT_DELTA: dict["AnnalesManifestGeltung", float] = {}
_TIER_DELTA: dict["AnnalesManifestGeltung", int] = {}
_TYP_MAP: dict["AnnalesManifestGeltung", "AnnalesManifestTyp"] = {}
_PROZEDUR_MAP: dict["AnnalesManifestGeltung", "AnnalesManifestProzedur"] = {}
_GELTUNG_MAP: dict[EpochenKodexGeltung, "AnnalesManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AnnalesManifestGeltung.GESPERRT: 0.0,
        AnnalesManifestGeltung.STRUKTURGESCHICHTLICH: 0.05,
        AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        AnnalesManifestGeltung.GESPERRT: 0,
        AnnalesManifestGeltung.STRUKTURGESCHICHTLICH: 1,
        AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH: 2,
    })
    _TYP_MAP.update({
        AnnalesManifestGeltung.GESPERRT: AnnalesManifestTyp.SCHUTZ_ANNALES,
        AnnalesManifestGeltung.STRUKTURGESCHICHTLICH: AnnalesManifestTyp.ORDNUNGS_ANNALES,
        AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH: AnnalesManifestTyp.SOUVERAENITAETS_ANNALES,
    })
    _PROZEDUR_MAP.update({
        AnnalesManifestGeltung.GESPERRT: AnnalesManifestProzedur.NOTPROZEDUR,
        AnnalesManifestGeltung.STRUKTURGESCHICHTLICH: AnnalesManifestProzedur.REGELPROTOKOLL,
        AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH: AnnalesManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        EpochenKodexGeltung.GESPERRT: AnnalesManifestGeltung.GESPERRT,
        EpochenKodexGeltung.EPOCHAL: AnnalesManifestGeltung.STRUKTURGESCHICHTLICH,
        EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL: AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH,
    })


class AnnalesManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    STRUKTURGESCHICHTLICH = "strukturgeschichtlich"
    GRUNDLEGEND_STRUKTURGESCHICHTLICH = "grundlegend-strukturgeschichtlich"


class AnnalesManifestTyp(Enum):
    SCHUTZ_ANNALES = "schutz-annales"
    ORDNUNGS_ANNALES = "ordnungs-annales"
    SOUVERAENITAETS_ANNALES = "souveraenitaets-annales"


class AnnalesManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class AnnalesManifestNorm:
    annales_manifest_id: str
    geschichts_typ: AnnalesManifestTyp
    prozedur: AnnalesManifestProzedur
    geltung: AnnalesManifestGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class AnnalesManifest:
    manifest_id: str
    epochen_kodex: EpochenKodex
    normen: tuple[AnnalesManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.annales_manifest_id for n in self.normen
            if n.geltung is AnnalesManifestGeltung.GESPERRT
        )

    @property
    def strukturgeschichtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.annales_manifest_id for n in self.normen
            if n.geltung is AnnalesManifestGeltung.STRUKTURGESCHICHTLICH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.annales_manifest_id for n in self.normen
            if n.geltung is AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH
        )

    @property
    def manifest_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is AnnalesManifestGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is AnnalesManifestGeltung.STRUKTURGESCHICHTLICH for n in self.normen):
            return SimpleNamespace(status="manifest-strukturgeschichtlich")
        return SimpleNamespace(status="manifest-grundlegend-strukturgeschichtlich")


_init_map()


def build_annales_manifest(
    epochen_kodex: EpochenKodex | None = None,
    *,
    manifest_id: str = "annales-manifest",
) -> AnnalesManifest:
    if epochen_kodex is None:
        epochen_kodex = build_epochen_kodex(kodex_id=f"{manifest_id}-kodex")
    normen: list[AnnalesManifestNorm] = []
    for parent_norm in epochen_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.epochen_kodex_id.removeprefix(f'{epochen_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH)
        normen.append(AnnalesManifestNorm(
            annales_manifest_id=new_id,
            geschichts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            geschichts_weight=new_weight,
            geschichts_tier=new_tier,
            canonical=is_canonical,
            geschichts_ids=parent_norm.geschichts_ids + (new_id,),
            geschichts_tags=parent_norm.geschichts_tags + (f"annales-manifest:{new_geltung.value}",),
        ))
    return AnnalesManifest(
        manifest_id=manifest_id,
        epochen_kodex=epochen_kodex,
        normen=tuple(normen),
    )
