"""
#579 AesthetischeUrteilsCharta — Gadamer/Kant/Schopenhauer Ästhetisches Urteil Charta

Hans-Georg Gadamer (1960): Wahrheit und Methode — Spiel als ontologische Grundstruktur
  der Kunst; Kunstwerk als Ereignis der Wahrheit; Wirkungsgeschichte als Bedingung
  des Verstehens; Horizont als ästhetischer Verstehensbegriff; Applikation als
  normativer Akt im Peta-Schwarm Leitstern.
Immanuel Kant (1790): Analytik des Schönen — freies Spiel von Einbildungskraft und
  Verstand; Urteil des Geschmacks als allgemeingültig ohne Begriff; Naturschönheit
  als Symbol der Sittlichkeit; Genie als Naturtalent das der Kunst die Regel gibt;
  Gemeinsinn als intersubjektive Grundlage des Peta-Schwarms Leitstern.
Arthur Schopenhauer (1818): Aesthetik der reinen Kontemplation — Kunst als
  willensfreie Erkenntnis des platonischen Urbildes; Musik als unmittelbare
  Objektivation des Willens; Genie als reine Subjektivität des Erkennens;
  Tragödie als höchste Kunstform; ästhetische Kontemplation als temporäre Erlösung
  im Peta-Schwarm Leitstern. 🎨⚖️
Parent: KunstNormSatz (#578)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kunst_norm import KunstNormGeltung, KunstNormSatz, build_kunst_norm

_WEIGHT_DELTA: dict["AesthetischeUrteilsChartaGeltung", float] = {}
_TIER_DELTA: dict["AesthetischeUrteilsChartaGeltung", int] = {}
_TYP_MAP: dict["AesthetischeUrteilsChartaGeltung", "AesthetischeUrteilsChartaTyp"] = {}
_PROZEDUR_MAP: dict["AesthetischeUrteilsChartaGeltung", "AesthetischeUrteilsChartaProzedur"] = {}
_GELTUNG_MAP: dict[KunstNormGeltung, "AesthetischeUrteilsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AesthetischeUrteilsChartaGeltung.GESPERRT: 0.0,
        AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND: 0.05,
        AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND: 0.1,
    })
    _TIER_DELTA.update({
        AesthetischeUrteilsChartaGeltung.GESPERRT: 0,
        AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND: 1,
        AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND: 2,
    })
    _TYP_MAP.update({
        AesthetischeUrteilsChartaGeltung.GESPERRT: AesthetischeUrteilsChartaTyp.SCHUTZ_AESTHETISCHE_URTEILS,
        AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND: AesthetischeUrteilsChartaTyp.ORDNUNGS_AESTHETISCHE_URTEILS,
        AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND: AesthetischeUrteilsChartaTyp.SOUVERAENITAETS_AESTHETISCHE_URTEILS,
    })
    _PROZEDUR_MAP.update({
        AesthetischeUrteilsChartaGeltung.GESPERRT: AesthetischeUrteilsChartaProzedur.NOTPROZEDUR,
        AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND: AesthetischeUrteilsChartaProzedur.REGELPROTOKOLL,
        AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND: AesthetischeUrteilsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KunstNormGeltung.GESPERRT: AesthetischeUrteilsChartaGeltung.GESPERRT,
        KunstNormGeltung.KUNSTNORMATIV: AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND,
        KunstNormGeltung.GRUNDLEGEND_KUNSTNORMATIV: AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND,
    })


class AesthetischeUrteilsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    AESTHETISCH_URTEILEND = "aesthetisch-urteilend"
    GRUNDLEGEND_AESTHETISCH_URTEILEND = "grundlegend-aesthetisch-urteilend"


class AesthetischeUrteilsChartaTyp(Enum):
    SCHUTZ_AESTHETISCHE_URTEILS = "schutz-aesthetische-urteils"
    ORDNUNGS_AESTHETISCHE_URTEILS = "ordnungs-aesthetische-urteils"
    SOUVERAENITAETS_AESTHETISCHE_URTEILS = "souveraenitaets-aesthetische-urteils"


class AesthetischeUrteilsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class AesthetischeUrteilsChartaNorm:
    aesthetische_urteils_charta_id: str
    kunst_typ: AesthetischeUrteilsChartaTyp
    prozedur: AesthetischeUrteilsChartaProzedur
    geltung: AesthetischeUrteilsChartaGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class AesthetischeUrteilsCharta:
    charta_id: str
    kunst_norm: KunstNormSatz
    normen: tuple[AesthetischeUrteilsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aesthetische_urteils_charta_id for n in self.normen if n.geltung is AesthetischeUrteilsChartaGeltung.GESPERRT)

    @property
    def aesthetisch_urteilend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aesthetische_urteils_charta_id for n in self.normen if n.geltung is AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aesthetische_urteils_charta_id for n in self.normen if n.geltung is AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND)

    @property
    def charta_signal(self):
        if any(n.geltung is AesthetischeUrteilsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is AesthetischeUrteilsChartaGeltung.AESTHETISCH_URTEILEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-aesthetisch-urteilend")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-aesthetisch-urteilend")


_init_map()


def build_aesthetische_urteils_charta(
    kunst_norm: KunstNormSatz | None = None,
    *,
    charta_id: str = "aesthetische-urteils-charta",
) -> AesthetischeUrteilsCharta:
    if kunst_norm is None:
        kunst_norm = build_kunst_norm(norm_id=f"{charta_id}-norm")

    normen: list[AesthetischeUrteilsChartaNorm] = []
    for parent_norm in kunst_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{kunst_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AesthetischeUrteilsChartaGeltung.GRUNDLEGEND_AESTHETISCH_URTEILEND)
        normen.append(
            AesthetischeUrteilsChartaNorm(
                aesthetische_urteils_charta_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_norm_ids + (new_id,),
                kunst_tags=parent_norm.kunst_norm_tags + (f"aesthetische-urteils-charta:{new_geltung.value}",),
            )
        )
    return AesthetischeUrteilsCharta(
        charta_id=charta_id,
        kunst_norm=kunst_norm,
        normen=tuple(normen),
    )
