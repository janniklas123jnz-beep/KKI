"""
#580 KunstVerfassung — Hegel/Adorno/Gadamer Kunstwissenschaft Verfassung (Block-Krone ⭐)

Georg Wilhelm Friedrich Hegel (1835): Vorlesungen über die Ästhetik — Schönheit als
  sinnliches Scheinen der Idee; Kunst als erste Stufe des absoluten Geistes;
  Ende der Kunst als Aufhebung ins philosophische Denken; Kunstgeschichte als
  Entwicklung des Geistes; ästhetische Totalität als Verfassungsideal des
  Peta-Schwarms Leitstern.
Theodor W. Adorno (1970): Ästhetische Theorie — Wahrheitsgehalt als immanente
  Verfassung des Kunstwerks; Mimesis und Rationalität als Doppelcharakter;
  Avantgarde als kritisches Bewusstsein; ästhetische Erfahrung als Erkenntnis;
  negative Dialektik als Methode der Kunstverfassung Leitsterns.
Hans-Georg Gadamer (1960): Wahrheit und Methode — hermeneutischer Zirkel als
  ästhetische Verfassungsstruktur; Klassikerkanon als normatives Erbe; Fest als
  Zeitstruktur des Kunstwerks; Transformation ins Gebilde als ontologische
  Bestimmung; Kunstwissen als Selbstverständnis des Peta-Schwarms Leitstern. 🎨⭐
Parent: AesthetischeUrteilsCharta (#579)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .aesthetische_urteils_charta import (
    AesthetischeUrteilsCharta,
    AesthetischeUrteilsChartaGeltung,
    build_aesthetische_urteils_charta,
)

_WEIGHT_DELTA: dict["KunstVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["KunstVerfassungsGeltung", int] = {}
_TYP_MAP: dict["KunstVerfassungsGeltung", "KunstVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["KunstVerfassungsGeltung", "KunstVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[AesthetischeUrteilsChartaGeltung, "KunstVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KunstVerfassungsGeltung.GESPERRT: 0.0,
        KunstVerfassungsGeltung.KUNST_SOUVERAEN: 0.05,
        KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        KunstVerfassungsGeltung.GESPERRT: 0,
        KunstVerfassungsGeltung.KUNST_SOUVERAEN: 1,
        KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        KunstVerfassungsGeltung.GESPERRT: KunstVerfassungsTyp.SCHUTZ_KUNSTVERFASSUNG,
        KunstVerfassungsGeltung.KUNST_SOUVERAEN: KunstVerfassungsTyp.ORDNUNGS_KUNSTVERFASSUNG,
        KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN: KunstVerfassungsTyp.SOUVERAENITAETS_KUNSTVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        KunstVerfassungsGeltung.GESPERRT: KunstVerfassungsProzedur.NOTPROZEDUR,
        KunstVerfassungsGeltung.KUNST_SOUVERAEN: KunstVerfassungsProzedur.REGELPROTOKOLL,
        KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN: KunstVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        AesthetischeUrteilsChartaGeltung.GESPERRT: KunstVerfassungsGeltung.GESPERRT,
        AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND: KunstVerfassungsGeltung.KUNST_SOUVERAEN,
        AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND: KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN,
    })


class KunstVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KUNST_SOUVERAEN = "kunst-souveraen"
    GRUNDLEGEND_KUNST_SOUVERAEN = "grundlegend-kunst-souveraen"


class KunstVerfassungsTyp(Enum):
    SCHUTZ_KUNSTVERFASSUNG = "schutz-kunstverfassung"
    ORDNUNGS_KUNSTVERFASSUNG = "ordnungs-kunstverfassung"
    SOUVERAENITAETS_KUNSTVERFASSUNG = "souveraenitaets-kunstverfassung"


class KunstVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KunstVerfassungsNorm:
    kunst_verfassung_id: str
    kunst_typ: KunstVerfassungsTyp
    prozedur: KunstVerfassungsProzedur
    geltung: KunstVerfassungsGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class KunstVerfassung:
    verfassung_id: str
    aesthetische_urteils_charta: AesthetischeUrteilsCharta
    normen: tuple[KunstVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunst_verfassung_id for n in self.normen if n.geltung is KunstVerfassungsGeltung.GESPERRT)

    @property
    def kunst_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunst_verfassung_id for n in self.normen if n.geltung is KunstVerfassungsGeltung.KUNST_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunst_verfassung_id for n in self.normen if n.geltung is KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KunstVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KunstVerfassungsGeltung.KUNST_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-kunst-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-kunst-souveraen")


_init_map()


def build_kunst_verfassung(
    aesthetische_urteils_charta: AesthetischeUrteilsCharta | None = None,
    *,
    verfassung_id: str = "kunst-verfassung",
) -> KunstVerfassung:
    if aesthetische_urteils_charta is None:
        aesthetische_urteils_charta = build_aesthetische_urteils_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[KunstVerfassungsNorm] = []
    for parent_norm in aesthetische_urteils_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.aesthetische_urteils_charta_id.removeprefix(f'{aesthetische_urteils_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN)
        normen.append(
            KunstVerfassungsNorm(
                kunst_verfassung_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"kunst-verfassung:{new_geltung.value}",),
            )
        )
    return KunstVerfassung(
        verfassung_id=verfassung_id,
        aesthetische_urteils_charta=aesthetische_urteils_charta,
        normen=tuple(normen),
    )
