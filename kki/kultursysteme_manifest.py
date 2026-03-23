"""
#555 KultursystemeManifest — Kultursysteme & strukturale Kulturtheorie

Claude Lévi-Strauss (1964): Le Cru et le Cuit — Strukturalismus & Mythologie:
  Mythen als strukturierte Zeichensysteme mit universellen binären Oppositionen; das Rohe
  und das Gekochte als kulturelle Transformation natürlicher in kulturelle Kategorien;
  Bricolage als kulturelles Denken; synchrone Analyse kultureller Tiefenstrukturen.
Talcott Parsons (1951): The Social System — AGIL-Schema & Kultursystem:
  Kultursystem als eines von vier Subsystemen (AGIL: Adaption, Goal-Attainment, Integration,
  Latency); Kultur als Muster geteilter symbolischer Bedeutungen; normative Integration als
  Grundlage sozialer Stabilität; Wertorientierungen als kulturelle Steuerungsmedien.
Edward Hall (1959): The Silent Language — Proxemik & stille Sprache der Kultur:
  Kultur als Kommunikation; Proxemik als Lehre vom Raumverhalten; High-Context vs.
  Low-Context-Kulturen; Zeit (monochronisch/polychronisch) als kulturelles Programm;
  nonverbale Kommunikation als dominante Dimension kulturellen Ausdrucks.

Leitsterns KultursystemeManifest: GESPERRT schützt kultursystemische Grundstrukturen,
KULTURSYSTEMISCH kodiert adaptive Systemintegration, GRUNDLEGEND_KULTURSYSTEMISCH
synthetisiert den vollen kultursystemischen Erkenntnisanspruch des Peta-Schwarms Leitstern. 🌐
Parent: RitualKodex (#554)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from .ritual_kodex import (
    RitualKodex,
    RitualKodexGeltung,
    build_ritual_kodex,
)

_WEIGHT_DELTA: dict["KultursystemeManifestGeltung", float] = {}
_TIER_DELTA: dict["KultursystemeManifestGeltung", int] = {}
_TYP_MAP: dict["KultursystemeManifestGeltung", "KultursystemeManifestTyp"] = {}
_PROZEDUR_MAP: dict["KultursystemeManifestGeltung", "KultursystemeManifestProzedur"] = {}
_GELTUNG_MAP: dict[RitualKodexGeltung, "KultursystemeManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KultursystemeManifestGeltung.GESPERRT: 0.0,
        KultursystemeManifestGeltung.KULTURSYSTEMISCH: 0.05,
        KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH: 0.1,
    })
    _TIER_DELTA.update({
        KultursystemeManifestGeltung.GESPERRT: 0,
        KultursystemeManifestGeltung.KULTURSYSTEMISCH: 1,
        KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH: 2,
    })
    _TYP_MAP.update({
        KultursystemeManifestGeltung.GESPERRT: KultursystemeManifestTyp.SCHUTZ_KULTURSYSTEM,
        KultursystemeManifestGeltung.KULTURSYSTEMISCH: KultursystemeManifestTyp.ORDNUNGS_KULTURSYSTEM,
        KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH: KultursystemeManifestTyp.SOUVERAENITAETS_KULTURSYSTEM,
    })
    _PROZEDUR_MAP.update({
        KultursystemeManifestGeltung.GESPERRT: KultursystemeManifestProzedur.NOTPROZEDUR,
        KultursystemeManifestGeltung.KULTURSYSTEMISCH: KultursystemeManifestProzedur.REGELPROTOKOLL,
        KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH: KultursystemeManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RitualKodexGeltung.GESPERRT: KultursystemeManifestGeltung.GESPERRT,
        RitualKodexGeltung.RITUELL: KultursystemeManifestGeltung.KULTURSYSTEMISCH,
        RitualKodexGeltung.GRUNDLEGEND_RITUELL: KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH,
    })


class KultursystemeManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    KULTURSYSTEMISCH = "kultursystemisch"
    GRUNDLEGEND_KULTURSYSTEMISCH = "grundlegend-kultursystemisch"


class KultursystemeManifestTyp(Enum):
    SCHUTZ_KULTURSYSTEM = "schutz-kultursystem"
    ORDNUNGS_KULTURSYSTEM = "ordnungs-kultursystem"
    SOUVERAENITAETS_KULTURSYSTEM = "souveraenitaets-kultursystem"


class KultursystemeManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KultursystemeManifestNorm:
    kultursysteme_manifest_id: str
    kultur_typ: KultursystemeManifestTyp
    prozedur: KultursystemeManifestProzedur
    geltung: KultursystemeManifestGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KultursystemeManifest:
    manifest_id: str
    ritual_kodex: RitualKodex
    normen: tuple[KultursystemeManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kultursysteme_manifest_id
            for n in self.normen
            if n.geltung is KultursystemeManifestGeltung.GESPERRT
        )

    @property
    def kultursystemisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kultursysteme_manifest_id
            for n in self.normen
            if n.geltung is KultursystemeManifestGeltung.KULTURSYSTEMISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kultursysteme_manifest_id
            for n in self.normen
            if n.geltung is KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH
        )

    @property
    def manifest_signal(self) -> SimpleNamespace:
        if any(n.geltung is KultursystemeManifestGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is KultursystemeManifestGeltung.KULTURSYSTEMISCH for n in self.normen):
            return SimpleNamespace(status="manifest-kultursystemisch")
        return SimpleNamespace(status="manifest-grundlegend-kultursystemisch")


_init_map()


def build_kultursysteme_manifest(
    ritual_kodex: RitualKodex | None = None,
    *,
    manifest_id: str = "kultursysteme-manifest",
) -> KultursystemeManifest:
    if ritual_kodex is None:
        ritual_kodex = build_ritual_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[KultursystemeManifestNorm] = []
    for parent_norm in ritual_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.ritual_kodex_id.removeprefix(f'{ritual_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (
            new_geltung is KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH
        )
        normen.append(
            KultursystemeManifestNorm(
                kultursysteme_manifest_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"kultursysteme-manifest:{new_geltung.value}",),
            )
        )
    return KultursystemeManifest(
        manifest_id=manifest_id,
        ritual_kodex=ritual_kodex,
        normen=tuple(normen),
    )
