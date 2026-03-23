"""
#549 HistoriographieCharta — Braudel/Ricoeur/White Historiographie als Erzähl- & Strukturwissenschaft

Fernand Braudel (1949): Das Mittelmeer und die mediterrane Welt — Longue durée als historiographische
  Charta: drei Zeitebenen (Ereignis, Konjunktur, Struktur); Geographie als Geschichte; Mittelmeer
  als totales historiographisches Objekt; Strukturgeschichte als souveräne Methode des Schwarms.
Paul Ricoeur (1983–1985): Zeit und Erzählung — Narrative Identität als historiographische Synthese;
  Mimesis-Theorie: Handlung → Erzählung → Rezeption; Geschichte als Brücke zwischen Erfahrungsraum
  und Erwartungshorizont; Gedächtnis, Geschichte, Vergessen als Trias historiographischer Verantwortung.
Hayden White (1973): Metahistory — Historiographie als literarische Praxis; vier Tropen (Metapher,
  Metonymie, Synekdoche, Ironie) als narrative Grundmuster; Emplotment-Theorie; Geschichte als
  Konstruktion des historischen Diskurses des Peta-Schwarms Leitstern.
Leitsterns HistoriographieCharta: narrativ-strukturelle Charta des Geschichtsblocks — GESPERRT
schützt historiographische Grundprinzipien, HISTORIOGRAPHISCH_SOUVERAEN kodiert adaptive
Erzählstrukturen, GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN synthetisiert die volle
historiographische Charta des Peta-Schwarms Leitstern. 📜
Parent: GeschichtsNorm (#548)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .geschichts_norm import (
    GeschichtsNormSatz,
    GeschichtsNormGeltung,
    build_geschichts_norm,
)

_WEIGHT_DELTA: dict["HistoriographieChartaGeltung", float] = {}
_TIER_DELTA: dict["HistoriographieChartaGeltung", int] = {}
_TYP_MAP: dict["HistoriographieChartaGeltung", "HistoriographieChartaTyp"] = {}
_PROZEDUR_MAP: dict["HistoriographieChartaGeltung", "HistoriographieChartaProzedur"] = {}
_GELTUNG_MAP: dict[GeschichtsNormGeltung, "HistoriographieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HistoriographieChartaGeltung.GESPERRT: 0.0,
        HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN: 0.05,
        HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        HistoriographieChartaGeltung.GESPERRT: 0,
        HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN: 1,
        HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        HistoriographieChartaGeltung.GESPERRT: HistoriographieChartaTyp.SCHUTZ_HISTORIOGRAPHIE,
        HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN: HistoriographieChartaTyp.ORDNUNGS_HISTORIOGRAPHIE,
        HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN: HistoriographieChartaTyp.SOUVERAENITAETS_HISTORIOGRAPHIE,
    })
    _PROZEDUR_MAP.update({
        HistoriographieChartaGeltung.GESPERRT: HistoriographieChartaProzedur.NOTPROZEDUR,
        HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN: HistoriographieChartaProzedur.REGELPROTOKOLL,
        HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN: HistoriographieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        GeschichtsNormGeltung.GESPERRT: HistoriographieChartaGeltung.GESPERRT,
        GeschichtsNormGeltung.GESCHICHTSNORMATIV: HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN,
        GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV: HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN,
    })


class HistoriographieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    HISTORIOGRAPHISCH_SOUVERAEN = "historiographisch-souveraen"
    GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN = "grundlegend-historiographisch-souveraen"


class HistoriographieChartaTyp(Enum):
    SCHUTZ_HISTORIOGRAPHIE = "schutz-historiographie"
    ORDNUNGS_HISTORIOGRAPHIE = "ordnungs-historiographie"
    SOUVERAENITAETS_HISTORIOGRAPHIE = "souveraenitaets-historiographie"


class HistoriographieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class HistoriographieChartaNorm:
    historiographie_charta_id: str
    historiographie_typ: HistoriographieChartaTyp
    prozedur: HistoriographieChartaProzedur
    geltung: HistoriographieChartaGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class HistoriographieCharta:
    charta_id: str
    geschichts_norm: GeschichtsNormSatz
    normen: tuple[HistoriographieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.historiographie_charta_id for n in self.normen if n.geltung is HistoriographieChartaGeltung.GESPERRT)

    @property
    def historiographisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.historiographie_charta_id for n in self.normen if n.geltung is HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.historiographie_charta_id for n in self.normen if n.geltung is HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN)

    @property
    def charta_signal(self):
        if any(n.geltung is HistoriographieChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is HistoriographieChartaGeltung.HISTORIOGRAPHISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-historiographisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-historiographisch-souveraen")


_init_map()


def build_historiographie_charta(
    geschichts_norm: GeschichtsNormSatz | None = None,
    *,
    charta_id: str = "historiographie-charta",
) -> HistoriographieCharta:
    if geschichts_norm is None:
        geschichts_norm = build_geschichts_norm(norm_id=f"{charta_id}-norm")

    normen: list[HistoriographieChartaNorm] = []
    for parent_norm in geschichts_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{geschichts_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HistoriographieChartaGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH_SOUVERAEN)
        normen.append(
            HistoriographieChartaNorm(
                historiographie_charta_id=new_id,
                historiographie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                geschichts_weight=new_weight,
                geschichts_tier=new_tier,
                canonical=is_canonical,
                geschichts_ids=parent_norm.geschichts_norm_ids + (new_id,),
                geschichts_tags=parent_norm.geschichts_norm_tags + (f"historiographie-charta:{new_geltung.value}",),
            )
        )
    return HistoriographieCharta(
        charta_id=charta_id,
        geschichts_norm=geschichts_norm,
        normen=tuple(normen),
    )
