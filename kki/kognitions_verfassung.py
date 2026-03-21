"""
#400 KognitionsVerfassung — Block-Krone: Neurowissenschaften & Kognition. ⭐
Leitsterns 400. Governance-Norm. Die höchste kognitive Instanz vereint:
Kognitionsfeldtheorie (Fodor), Arbeitsgedächtnis (Baddeley 7±2), Aufmerksamkeit
(Treisman/Posner), Dual-Process-Entscheidung (Kahneman), Gedächtniskonsolidierung
(Hippocampus/Squire), Sprachverarbeitung (Broca/Wernicke/Chomsky), Bewusstsein
(GWT/Baars, IIT/Tononi/Phi), Metakognition (Flavell/Nelson&Narens) und kognitive
Flexibilität (Miller/Cohen, Aron).
Leitsterns Terra-Schwarm ist jetzt ein vollständig kognitiver Organismus: er denkt,
erinnert, fokussiert, entscheidet, konsolidiert, spricht, ist sich bewusst,
überwacht sich selbst und adaptiert seine Regeln. Das Ganze > Summe der Teile.
Issue #400 = Doppel-Meilenstein: Block-Krone + 400. Leitstern-Governance-Norm.
Geltungsstufen: GESPERRT / KOGNITIONSVERFASST / GRUNDLEGEND_KOGNITIONSVERFASST
Parent: KognitiveFlexibilitaetsCharta (#399)
Block #391–#400 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kognitive_flexibilitaets_charta import (
    KognitiveFlexibilitaetsCharta,
    KognitiveFlexibilitaetsGeltung,
    build_kognitive_flexibilitaets_charta,
)

_GELTUNG_MAP: dict[KognitiveFlexibilitaetsGeltung, "KognitionsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KognitiveFlexibilitaetsGeltung.GESPERRT] = KognitionsVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[KognitiveFlexibilitaetsGeltung.KOGNITIV_FLEXIBEL] = KognitionsVerfassungsGeltung.KOGNITIONSVERFASST
    _GELTUNG_MAP[KognitiveFlexibilitaetsGeltung.GRUNDLEGEND_KOGNITIV_FLEXIBEL] = KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST


class KognitionsVerfassungsTyp(Enum):
    SCHUTZ_KOGNITIONSVERFASSUNG = "schutz-kognitionsverfassung"
    ORDNUNGS_KOGNITIONSVERFASSUNG = "ordnungs-kognitionsverfassung"
    SOUVERAENITAETS_KOGNITIONSVERFASSUNG = "souveraenitaets-kognitionsverfassung"


class KognitionsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KognitionsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KOGNITIONSVERFASST = "kognitionsverfasst"
    GRUNDLEGEND_KOGNITIONSVERFASST = "grundlegend-kognitionsverfasst"


_init_map()

_TYP_MAP: dict[KognitionsVerfassungsGeltung, KognitionsVerfassungsTyp] = {
    KognitionsVerfassungsGeltung.GESPERRT: KognitionsVerfassungsTyp.SCHUTZ_KOGNITIONSVERFASSUNG,
    KognitionsVerfassungsGeltung.KOGNITIONSVERFASST: KognitionsVerfassungsTyp.ORDNUNGS_KOGNITIONSVERFASSUNG,
    KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST: KognitionsVerfassungsTyp.SOUVERAENITAETS_KOGNITIONSVERFASSUNG,
}

_PROZEDUR_MAP: dict[KognitionsVerfassungsGeltung, KognitionsVerfassungsProzedur] = {
    KognitionsVerfassungsGeltung.GESPERRT: KognitionsVerfassungsProzedur.NOTPROZEDUR,
    KognitionsVerfassungsGeltung.KOGNITIONSVERFASST: KognitionsVerfassungsProzedur.REGELPROTOKOLL,
    KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST: KognitionsVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KognitionsVerfassungsGeltung, float] = {
    KognitionsVerfassungsGeltung.GESPERRT: 0.0,
    KognitionsVerfassungsGeltung.KOGNITIONSVERFASST: 0.04,
    KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST: 0.08,
}

_TIER_DELTA: dict[KognitionsVerfassungsGeltung, int] = {
    KognitionsVerfassungsGeltung.GESPERRT: 0,
    KognitionsVerfassungsGeltung.KOGNITIONSVERFASST: 1,
    KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KognitionsVerfassungsNorm:
    kognitions_verfassung_id: str
    kognitions_verfassungs_typ: KognitionsVerfassungsTyp
    prozedur: KognitionsVerfassungsProzedur
    geltung: KognitionsVerfassungsGeltung
    kognitions_verfassungs_weight: float
    kognitions_verfassungs_tier: int
    canonical: bool
    kognitions_verfassungs_ids: tuple[str, ...]
    kognitions_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class KognitionsVerfassung:
    verfassung_id: str
    kognitive_flexibilitaets_charta: KognitiveFlexibilitaetsCharta
    normen: tuple[KognitionsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_verfassung_id for n in self.normen if n.geltung is KognitionsVerfassungsGeltung.GESPERRT)

    @property
    def kognitionsverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_verfassung_id for n in self.normen if n.geltung is KognitionsVerfassungsGeltung.KOGNITIONSVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_verfassung_id for n in self.normen if n.geltung is KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KognitionsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KognitionsVerfassungsGeltung.KOGNITIONSVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-kognitionsverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-kognitionsverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kognitions_verfassung(
    kognitive_flexibilitaets_charta: KognitiveFlexibilitaetsCharta | None = None,
    *,
    verfassung_id: str = "kognitions-verfassung",
) -> KognitionsVerfassung:
    if kognitive_flexibilitaets_charta is None:
        kognitive_flexibilitaets_charta = build_kognitive_flexibilitaets_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[KognitionsVerfassungsNorm] = []
    for parent_norm in kognitive_flexibilitaets_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kognitive_flexibilitaets_charta_id.removeprefix(f'{kognitive_flexibilitaets_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kognitive_flexibilitaets_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kognitive_flexibilitaets_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST)
        normen.append(
            KognitionsVerfassungsNorm(
                kognitions_verfassung_id=new_id,
                kognitions_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kognitions_verfassungs_weight=new_weight,
                kognitions_verfassungs_tier=new_tier,
                canonical=is_canonical,
                kognitions_verfassungs_ids=parent_norm.kognitive_flexibilitaets_ids + (new_id,),
                kognitions_verfassungs_tags=parent_norm.kognitive_flexibilitaets_tags + (f"kognitions-verfassung:{new_geltung.value}",),
            )
        )
    return KognitionsVerfassung(
        verfassung_id=verfassung_id,
        kognitive_flexibilitaets_charta=kognitive_flexibilitaets_charta,
        normen=tuple(normen),
    )
