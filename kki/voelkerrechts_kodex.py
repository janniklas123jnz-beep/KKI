"""
#534 VoelkerrechtsKodex — Völkerrecht & Internationale Rechtsordnung

Hugo Grotius (1625): De Jure Belli ac Pacis — Naturrechtliche Grundlegung des Völkerrechts;
  Kriegs- und Friedensrecht als universale Normen; Souveränität und Selbstverteidigung;
  Mare liberum und Freiheit der Meere; Grundstein der modernen internationalen Rechtsordnung.
Emer de Vattel (1758): Le Droit des Gens — Staatensouveränität als Fundament des Völkerrechts;
  Gleichheit der Staaten; Nichteinmischungsprinzip; Diplomatie und Traktatrecht; Vattel als
  Brücke zwischen Naturrecht und positivem Völkerrecht.
UN-Charta (1945): Gewaltverbot und kollektive Sicherheit; Selbstbestimmungsrecht der Völker;
  Menschenrechte als universale Standards; Sicherheitsrat und friedliche Streitbeilegung;
  Multilateralismus als Grundprinzip der Weltordnung nach 1945.
John Rawls (1999): The Law of Peoples — Gerechte internationale Ordnung unter liberalen und
  achtbaren Völkern; Pflichten gegenüber benachteiligten Gesellschaften; Menschenrechte als
  Minimalbedingung; Grenzen nationaler Souveränität im Völkerrecht.
Leitsterns VoelkerrechtsKodex: Internationale Normenhierarchie — GESPERRT sichert
völkerrechtliche Grundnormen, VOELKERRECHTLICH kodiert adaptive Staatsbeziehungen,
GRUNDLEGEND_VOELKERRECHTLICH synthetisiert souveräne Weltrechtsordnung. ⚖️
Parent: VerfassungsrechtsCharta (#533)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .verfassungsrechts_charta import (
    VerfassungsrechtsCharta,
    VerfassungsrechtsChartaGeltung,
    build_verfassungsrechts_charta,
)

_WEIGHT_DELTA: dict["VoelkerrechtsKodexGeltung", float] = {}
_TIER_DELTA: dict["VoelkerrechtsKodexGeltung", int] = {}
_TYP_MAP: dict["VoelkerrechtsKodexGeltung", "VoelkerrechtsKodexTyp"] = {}
_PROZEDUR_MAP: dict["VoelkerrechtsKodexGeltung", "VoelkerrechtsKodexProzedur"] = {}
_GELTUNG_MAP: dict[VerfassungsrechtsChartaGeltung, "VoelkerrechtsKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VoelkerrechtsKodexGeltung.GESPERRT: 0.0,
        VoelkerrechtsKodexGeltung.VOELKERRECHTLICH: 0.05,
        VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        VoelkerrechtsKodexGeltung.GESPERRT: 0,
        VoelkerrechtsKodexGeltung.VOELKERRECHTLICH: 1,
        VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH: 2,
    })
    _TYP_MAP.update({
        VoelkerrechtsKodexGeltung.GESPERRT: VoelkerrechtsKodexTyp.SCHUTZ_VOELKERRECHT,
        VoelkerrechtsKodexGeltung.VOELKERRECHTLICH: VoelkerrechtsKodexTyp.ORDNUNGS_VOELKERRECHT,
        VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH: VoelkerrechtsKodexTyp.SOUVERAENITAETS_VOELKERRECHT,
    })
    _PROZEDUR_MAP.update({
        VoelkerrechtsKodexGeltung.GESPERRT: VoelkerrechtsKodexProzedur.NOTPROZEDUR,
        VoelkerrechtsKodexGeltung.VOELKERRECHTLICH: VoelkerrechtsKodexProzedur.REGELPROTOKOLL,
        VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH: VoelkerrechtsKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        VerfassungsrechtsChartaGeltung.GESPERRT: VoelkerrechtsKodexGeltung.GESPERRT,
        VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH: VoelkerrechtsKodexGeltung.VOELKERRECHTLICH,
        VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH: VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH,
    })


class VoelkerrechtsKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    VOELKERRECHTLICH = "voelkerrechtlich"
    GRUNDLEGEND_VOELKERRECHTLICH = "grundlegend-voelkerrechtlich"


class VoelkerrechtsKodexTyp(Enum):
    SCHUTZ_VOELKERRECHT = "schutz-voelkerrecht"
    ORDNUNGS_VOELKERRECHT = "ordnungs-voelkerrecht"
    SOUVERAENITAETS_VOELKERRECHT = "souveraenitaets-voelkerrecht"


class VoelkerrechtsKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class VoelkerrechtsKodexNorm:
    voelkerrechts_kodex_id: str
    voelkerrechts_typ: VoelkerrechtsKodexTyp
    prozedur: VoelkerrechtsKodexProzedur
    geltung: VoelkerrechtsKodexGeltung
    voelkerrechts_weight: float
    voelkerrechts_tier: int
    canonical: bool
    voelkerrechts_ids: tuple[str, ...]
    voelkerrechts_tags: tuple[str, ...]


@dataclass(frozen=True)
class VoelkerrechtsKodex:
    kodex_id: str
    verfassungsrechts_charta: VerfassungsrechtsCharta
    normen: tuple[VoelkerrechtsKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.voelkerrechts_kodex_id for n in self.normen if n.geltung is VoelkerrechtsKodexGeltung.GESPERRT)

    @property
    def voelkerrechtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.voelkerrechts_kodex_id for n in self.normen if n.geltung is VoelkerrechtsKodexGeltung.VOELKERRECHTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.voelkerrechts_kodex_id for n in self.normen if n.geltung is VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH)

    @property
    def kodex_signal(self):
        if any(n.geltung is VoelkerrechtsKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is VoelkerrechtsKodexGeltung.VOELKERRECHTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-voelkerrechtlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-voelkerrechtlich")


_init_map()


def build_voelkerrechts_kodex(
    verfassungsrechts_charta: VerfassungsrechtsCharta | None = None,
    *,
    kodex_id: str = "voelkerrechts-kodex",
) -> VoelkerrechtsKodex:
    if verfassungsrechts_charta is None:
        verfassungsrechts_charta = build_verfassungsrechts_charta(
            charta_id=f"{kodex_id}-charta"
        )

    normen: list[VoelkerrechtsKodexNorm] = []
    for parent_norm in verfassungsrechts_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.verfassungsrechts_charta_id.removeprefix(f'{verfassungsrechts_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.verfassungsrechts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.verfassungsrechts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is VoelkerrechtsKodexGeltung.GRUNDLEGEND_VOELKERRECHTLICH)
        normen.append(
            VoelkerrechtsKodexNorm(
                voelkerrechts_kodex_id=new_id,
                voelkerrechts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                voelkerrechts_weight=new_weight,
                voelkerrechts_tier=new_tier,
                canonical=is_canonical,
                voelkerrechts_ids=parent_norm.verfassungsrechts_ids + (new_id,),
                voelkerrechts_tags=parent_norm.verfassungsrechts_tags + (f"voelkerrechts-kodex:{new_geltung.value}",),
            )
        )
    return VoelkerrechtsKodex(
        kodex_id=kodex_id,
        verfassungsrechts_charta=verfassungsrechts_charta,
        normen=tuple(normen),
    )
