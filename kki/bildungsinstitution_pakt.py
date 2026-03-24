"""
#586 BildungsinstitutionPakt — Illich/Durkheim/Bourdieu Bildungsinstitution Pakt

Ivan Illich (1971): Deschooling Society — Entschulung als radikale Bildungsreform;
  Lernnetze als Alternative zur Schule; konviviale Werkzeuge als Bildungsmedien;
  institutionelle Verstrickung als Hemmnis der Bildung; selbstgesteuerte Lerngemeinschaften
  als Bildungszukunft im Peta-Schwarm Leitstern.
Émile Durkheim (1922): Éducation et Sociologie — Schule als Sozialisationsagentur;
  moralische Erziehung als gesellschaftliche Aufgabe; kollektive Repräsentationen als
  Bildungsinhalte; funktionale Differenzierung als Schulprinzip; Solidarität als
  Bildungsziel im Peta-Schwarm Leitstern.
Pierre Bourdieu & Jean-Claude Passeron (1970): La Reproduction — Bildungsinstitutionen
  als Reproduktion sozialer Ungleichheit; kulturelles Kapital als Bildungsressource;
  symbolische Gewalt im Bildungswesen; Habitus als verinnerlichte Bildungsstruktur;
  Feld der Bildung als soziale Arena im Peta-Schwarm Leitstern. 🏛️🤝
Parent: CurriculumManifest (#585)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .curriculum_manifest import (
    CurriculumManifest,
    CurriculumManifestGeltung,
    build_curriculum_manifest,
)

_WEIGHT_DELTA: dict["BildungsinstitutionPaktGeltung", float] = {}
_TIER_DELTA: dict["BildungsinstitutionPaktGeltung", int] = {}
_TYP_MAP: dict["BildungsinstitutionPaktGeltung", "BildungsinstitutionPaktTyp"] = {}
_PROZEDUR_MAP: dict["BildungsinstitutionPaktGeltung", "BildungsinstitutionPaktProzedur"] = {}
_GELTUNG_MAP: dict[CurriculumManifestGeltung, "BildungsinstitutionPaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BildungsinstitutionPaktGeltung.GESPERRT: 0.0,
        BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND: 0.05,
        BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND: 0.1,
    })
    _TIER_DELTA.update({
        BildungsinstitutionPaktGeltung.GESPERRT: 0,
        BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND: 1,
        BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND: 2,
    })
    _TYP_MAP.update({
        BildungsinstitutionPaktGeltung.GESPERRT: BildungsinstitutionPaktTyp.SCHUTZ_BILDUNGSINSTITUTION,
        BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND: BildungsinstitutionPaktTyp.ORDNUNGS_BILDUNGSINSTITUTION,
        BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND: BildungsinstitutionPaktTyp.SOUVERAENITAETS_BILDUNGSINSTITUTION,
    })
    _PROZEDUR_MAP.update({
        BildungsinstitutionPaktGeltung.GESPERRT: BildungsinstitutionPaktProzedur.NOTPROZEDUR,
        BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND: BildungsinstitutionPaktProzedur.REGELPROTOKOLL,
        BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND: BildungsinstitutionPaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        CurriculumManifestGeltung.GESPERRT: BildungsinstitutionPaktGeltung.GESPERRT,
        CurriculumManifestGeltung.CURRICULAR: BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND,
        CurriculumManifestGeltung.GRUNDLEGEND_CURRICULAR: BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND,
    })


class BildungsinstitutionPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    INSTITUTIONELL_BILDEND = "institutionell-bildend"
    GRUNDLEGEND_INSTITUTIONELL_BILDEND = "grundlegend-institutionell-bildend"


class BildungsinstitutionPaktTyp(Enum):
    SCHUTZ_BILDUNGSINSTITUTION = "schutz-bildungsinstitution"
    ORDNUNGS_BILDUNGSINSTITUTION = "ordnungs-bildungsinstitution"
    SOUVERAENITAETS_BILDUNGSINSTITUTION = "souveraenitaets-bildungsinstitution"


class BildungsinstitutionPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class BildungsinstitutionPaktNorm:
    bildungsinstitution_pakt_id: str
    paedagogik_typ: BildungsinstitutionPaktTyp
    prozedur: BildungsinstitutionPaktProzedur
    geltung: BildungsinstitutionPaktGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class BildungsinstitutionPakt:
    pakt_id: str
    curriculum_manifest: CurriculumManifest
    normen: tuple[BildungsinstitutionPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.bildungsinstitution_pakt_id for n in self.normen
            if n.geltung is BildungsinstitutionPaktGeltung.GESPERRT
        )

    @property
    def institutionell_bildend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.bildungsinstitution_pakt_id for n in self.normen
            if n.geltung is BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.bildungsinstitution_pakt_id for n in self.normen
            if n.geltung is BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND
        )

    @property
    def pakt_signal(self):
        if any(n.geltung is BildungsinstitutionPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-institutionell-bildend")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-institutionell-bildend")


_init_map()


def build_bildungsinstitution_pakt(
    curriculum_manifest: CurriculumManifest | None = None,
    *,
    pakt_id: str = "bildungsinstitution-pakt",
) -> BildungsinstitutionPakt:
    if curriculum_manifest is None:
        curriculum_manifest = build_curriculum_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[BildungsinstitutionPaktNorm] = []
    for parent_norm in curriculum_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.curriculum_manifest_id.removeprefix(f'{curriculum_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND)
        normen.append(
            BildungsinstitutionPaktNorm(
                bildungsinstitution_pakt_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"bildungsinstitution-pakt:{new_geltung.value}",),
            )
        )
    return BildungsinstitutionPakt(
        pakt_id=pakt_id,
        curriculum_manifest=curriculum_manifest,
        normen=tuple(normen),
    )
