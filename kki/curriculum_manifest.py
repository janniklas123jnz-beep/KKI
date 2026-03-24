"""
#585 CurriculumManifest — Tyler/Dewey/Eisner Curriculum Manifest

Ralph Tyler (1949): Basic Principles of Curriculum and Instruction — Vier Grundfragen
  des Curriculums: Ziele, Erfahrungen, Organisation, Evaluation; rationale Curriculumplanung
  als Bildungswissenschaft; Lernziele als Ausgangspunkt der Unterrichtsplanung; Tyler-Rationale
  als Standardmodell der Curriculumtheorie im Peta-Schwarm Leitstern.
John Dewey (1902): The Child and the Curriculum — Kind vs. Lehrplan als pädagogische Spannung;
  Erfahrungscurriculum als Verbindung von Kind und Lehrinhalt; demokratische Bildung als
  curriculare Grundhaltung; Problemorientierung als curriculares Prinzip; Schule als
  Mikrokosmos der Gesellschaft im Peta-Schwarm Leitstern.
Elliot Eisner (1979): The Educational Imagination — Curriculum als künstlerische Gestaltung;
  explizites, implizites und null Curriculum als analytische Trias; ästhetische Qualität
  von Unterricht; kunstbasierte Evaluation als Bildungsforschung; Curriculumkritik als
  kreative Praxis im Peta-Schwarm Leitstern. 📜🗂️
Parent: DidaktikKodex (#584)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .didaktik_kodex import (
    DidaktikKodex,
    DidaktikKodexGeltung,
    build_didaktik_kodex,
)

_WEIGHT_DELTA: dict["CurriculumManifestGeltung", float] = {}
_TIER_DELTA: dict["CurriculumManifestGeltung", int] = {}
_TYP_MAP: dict["CurriculumManifestGeltung", "CurriculumManifestTyp"] = {}
_PROZEDUR_MAP: dict["CurriculumManifestGeltung", "CurriculumManifestProzedur"] = {}
_GELTUNG_MAP: dict[DidaktikKodexGeltung, "CurriculumManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        CurriculumManifestGeltung.GESPERRT: 0.0,
        CurriculumManifestGeltung.CURRICULAR: 0.05,
        CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR: 0.1,
    })
    _TIER_DELTA.update({
        CurriculumManifestGeltung.GESPERRT: 0,
        CurriculumManifestGeltung.CURRICULAR: 1,
        CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR: 2,
    })
    _TYP_MAP.update({
        CurriculumManifestGeltung.GESPERRT: CurriculumManifestTyp.SCHUTZ_CURRICULUM,
        CurriculumManifestGeltung.CURRICULAR: CurriculumManifestTyp.ORDNUNGS_CURRICULUM,
        CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR: CurriculumManifestTyp.SOUVERAENITAETS_CURRICULUM,
    })
    _PROZEDUR_MAP.update({
        CurriculumManifestGeltung.GESPERRT: CurriculumManifestProzedur.NOTPROZEDUR,
        CurriculumManifestGeltung.CURRICULAR: CurriculumManifestProzedur.REGELPROTOKOLL,
        CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR: CurriculumManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        DidaktikKodexGeltung.GESPERRT: CurriculumManifestGeltung.GESPERRT,
        DidaktikKodexGeltung.DIDAKTISCH: CurriculumManifestGeltung.CURRICULAR,
        DidaktikKodexGeltung.GRUNDLEGEND_DIDAKTISCH: CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR,
    })


class CurriculumManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    CURRICULAR = "curricular"
    GRUNDLEGEND_CURRICULAR = "grundlegend-curricular"


class CurriculumManifestTyp(Enum):
    SCHUTZ_CURRICULUM = "schutz-curriculum"
    ORDNUNGS_CURRICULUM = "ordnungs-curriculum"
    SOUVERAENITAETS_CURRICULUM = "souveraenitaets-curriculum"


class CurriculumManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class CurriculumManifestNorm:
    curriculum_manifest_id: str
    paedagogik_typ: CurriculumManifestTyp
    prozedur: CurriculumManifestProzedur
    geltung: CurriculumManifestGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class CurriculumManifest:
    manifest_id: str
    didaktik_kodex: DidaktikKodex
    normen: tuple[CurriculumManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.curriculum_manifest_id for n in self.normen
            if n.geltung is CurriculumManifestGeltung.GESPERRT
        )

    @property
    def curricular_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.curriculum_manifest_id for n in self.normen
            if n.geltung is CurriculumManifestGeltung.CURRICULAR
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.curriculum_manifest_id for n in self.normen
            if n.geltung is CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR
        )

    @property
    def manifest_signal(self):
        if any(n.geltung is CurriculumManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is CurriculumManifestGeltung.CURRICULAR for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-curricular")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-curricular")


_init_map()


def build_curriculum_manifest(
    didaktik_kodex: DidaktikKodex | None = None,
    *,
    manifest_id: str = "curriculum-manifest",
) -> CurriculumManifest:
    if didaktik_kodex is None:
        didaktik_kodex = build_didaktik_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[CurriculumManifestNorm] = []
    for parent_norm in didaktik_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.didaktik_kodex_id.removeprefix(f'{didaktik_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR)
        normen.append(
            CurriculumManifestNorm(
                curriculum_manifest_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"curriculum-manifest:{new_geltung.value}",),
            )
        )
    return CurriculumManifest(
        manifest_id=manifest_id,
        didaktik_kodex=didaktik_kodex,
        normen=tuple(normen),
    )
