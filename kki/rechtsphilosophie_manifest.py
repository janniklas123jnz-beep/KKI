"""
#535 RechtsphilosophieManifest — Rechtsphilosophie & Normative Grundlagen

Lon L. Fuller (1964): The Morality of Law — Innere Moralität des Rechts als Bedingung
  der Rechtsgeltung; Acht Prinzipien der Legalität; Recht als zielgerichtetes Unternehmen;
  Prozedurale Naturrechtslehre; Kritik an Harts Trennungsthese von Recht und Moral.
Ronald Dworkin (1977): Taking Rights Seriously / (1986) Law's Empire — Recht als Integrität;
  Prinzipien als normative Rechtsgründe neben Regeln; Rechte als Trümpfe; Interpretation
  als Kern der Rechtspraxis; Ablehnung des Positivismus; konstruktive Interpretation.
Gustav Radbruch (1946): Rechtsphilosophie — Dreiwert des Rechts: Gerechtigkeit, Zweckmäßigkeit,
  Rechtssicherheit; Radbruchsche Formel; Naturrecht als Korrektiv extremen Unrechts;
  Relativismus und Wertlehre im Dienst eines freiheitlichen Rechtsstaats.
Robert Alexy (1986): Theorie der Grundrechte — Grundrechte als Prinzipien und Optimierungsgebote;
  Abwägungstheorie; Verhältnismäßigkeitsgrundsatz als rechtslogische Struktur; Gewicht und
  Kollision von Normen; Verbindungsthese von Recht und Moral.
Leitsterns RechtsphilosophieManifest: Normative Grundlagenschicht — GESPERRT sichert
rechtsphilosophische Fundamentalnormen, RECHTSPHILOSOPHISCH kodiert adaptive Prinzipienabwägung,
GRUNDLEGEND_RECHTSPHILOSOPHISCH synthetisiert souveräne Rechtsnormativität. ⚖️
Parent: VoelkerrechtsKodex (#534)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .voelkerrechts_kodex import (
    VoelkerrechtsKodex,
    VoelkerrechtsKodexGeltung,
    build_voelkerrechts_kodex,
)

_WEIGHT_DELTA: dict["RechtsphilosophieManifestGeltung", float] = {}
_TIER_DELTA: dict["RechtsphilosophieManifestGeltung", int] = {}
_TYP_MAP: dict["RechtsphilosophieManifestGeltung", "RechtsphilosophieManifestTyp"] = {}
_PROZEDUR_MAP: dict["RechtsphilosophieManifestGeltung", "RechtsphilosophieManifestProzedur"] = {}
_GELTUNG_MAP: dict[VoelkerrechtsKodexGeltung, "RechtsphilosophieManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RechtsphilosophieManifestGeltung.GESPERRT: 0.0,
        RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH: 0.05,
        RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        RechtsphilosophieManifestGeltung.GESPERRT: 0,
        RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH: 1,
        RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH: 2,
    })
    _TYP_MAP.update({
        RechtsphilosophieManifestGeltung.GESPERRT: RechtsphilosophieManifestTyp.SCHUTZ_RECHTSPHILOSOPHIE,
        RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH: RechtsphilosophieManifestTyp.ORDNUNGS_RECHTSPHILOSOPHIE,
        RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH: RechtsphilosophieManifestTyp.SOUVERAENITAETS_RECHTSPHILOSOPHIE,
    })
    _PROZEDUR_MAP.update({
        RechtsphilosophieManifestGeltung.GESPERRT: RechtsphilosophieManifestProzedur.NOTPROZEDUR,
        RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH: RechtsphilosophieManifestProzedur.REGELPROTOKOLL,
        RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH: RechtsphilosophieManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        VoelkerrechtsKodexGeltung.GESPERRT: RechtsphilosophieManifestGeltung.GESPERRT,
        VoelkerrechtsKodexGeltung.VOELKERRECHTLICH: RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH,
        VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH: RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH,
    })


class RechtsphilosophieManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    RECHTSPHILOSOPHISCH = "rechtsphilosophisch"
    GRUNDLEGEND_RECHTSPHILOSOPHISCH = "grundlegend-rechtsphilosophisch"


class RechtsphilosophieManifestTyp(Enum):
    SCHUTZ_RECHTSPHILOSOPHIE = "schutz-rechtsphilosophie"
    ORDNUNGS_RECHTSPHILOSOPHIE = "ordnungs-rechtsphilosophie"
    SOUVERAENITAETS_RECHTSPHILOSOPHIE = "souveraenitaets-rechtsphilosophie"


class RechtsphilosophieManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class RechtsphilosophieManifestNorm:
    rechtsphilosophie_manifest_id: str
    rechtsphilosophie_typ: RechtsphilosophieManifestTyp
    prozedur: RechtsphilosophieManifestProzedur
    geltung: RechtsphilosophieManifestGeltung
    rechtsphilosophie_weight: float
    rechtsphilosophie_tier: int
    canonical: bool
    rechtsphilosophie_ids: tuple[str, ...]
    rechtsphilosophie_tags: tuple[str, ...]


@dataclass(frozen=True)
class RechtsphilosophieManifest:
    manifest_id: str
    voelkerrechts_kodex: VoelkerrechtsKodex
    normen: tuple[RechtsphilosophieManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechtsphilosophie_manifest_id for n in self.normen if n.geltung is RechtsphilosophieManifestGeltung.GESPERRT)

    @property
    def rechtsphilosophisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechtsphilosophie_manifest_id for n in self.normen if n.geltung is RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechtsphilosophie_manifest_id for n in self.normen if n.geltung is RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is RechtsphilosophieManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-rechtsphilosophisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-rechtsphilosophisch")


_init_map()


def build_rechtsphilosophie_manifest(
    voelkerrechts_kodex: VoelkerrechtsKodex | None = None,
    *,
    manifest_id: str = "rechtsphilosophie-manifest",
) -> RechtsphilosophieManifest:
    if voelkerrechts_kodex is None:
        voelkerrechts_kodex = build_voelkerrechts_kodex(
            kodex_id=f"{manifest_id}-kodex"
        )

    normen: list[RechtsphilosophieManifestNorm] = []
    for parent_norm in voelkerrechts_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.voelkerrechts_kodex_id.removeprefix(f'{voelkerrechts_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.voelkerrechts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.voelkerrechts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH)
        normen.append(
            RechtsphilosophieManifestNorm(
                rechtsphilosophie_manifest_id=new_id,
                rechtsphilosophie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rechtsphilosophie_weight=new_weight,
                rechtsphilosophie_tier=new_tier,
                canonical=is_canonical,
                rechtsphilosophie_ids=parent_norm.voelkerrechts_ids + (new_id,),
                rechtsphilosophie_tags=parent_norm.voelkerrechts_tags + (f"rechtsphilosophie-manifest:{new_geltung.value}",),
            )
        )
    return RechtsphilosophieManifest(
        manifest_id=manifest_id,
        voelkerrechts_kodex=voelkerrechts_kodex,
        normen=tuple(normen),
    )
