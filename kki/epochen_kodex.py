"""
#544 EpochenKodex — Kodex der historischen Epochengliederung

Jacob Burckhardt (1860): Die Kultur der Renaissance in Italien — Epochenbegriff als Kulturgestalt;
  Renaissance als erste Epoche bewusster Individualität und modernen Staatsdenkens;
  Kulturgeschichte als Synthese von Kunst, Religion, Staat und sozialen Kräften einer Zeit.
Oswald Spengler (1918): Der Untergang des Abendlandes — Kulturmorphologie als Epochentheorie;
  Kulturen als organische Lebenszyklen mit Geburt, Blüte und Untergang;
  Ablehnung linearer Fortschrittsgeschichte zugunsten zyklischer Kulturmodelle.
Arnold Toynbee (1934–1961): A Study of History — Zivilisationstheorie als komparative Epochenkunde;
  Challenge-and-Response als Motor zivilisatorischen Auf- und Abstiegs;
  Vergleichende Zivilisationsgeschichte als Erweiterung eurozentristischer Epochenschemata.
Parent: QuellenCharta (#543)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quellen_charta import (
    QuellenCharta,
    QuellenChartaGeltung,
    build_quellen_charta,
)

_WEIGHT_DELTA: dict["EpochenKodexGeltung", float] = {}
_TIER_DELTA: dict["EpochenKodexGeltung", int] = {}
_TYP_MAP: dict["EpochenKodexGeltung", "EpochenKodexTyp"] = {}
_PROZEDUR_MAP: dict["EpochenKodexGeltung", "EpochenKodexProzedur"] = {}
_GELTUNG_MAP: dict[QuellenChartaGeltung, "EpochenKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        EpochenKodexGeltung.GESPERRT: 0.0,
        EpochenKodexGeltung.EPOCHAL: 0.05,
        EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL: 0.1,
    })
    _TIER_DELTA.update({
        EpochenKodexGeltung.GESPERRT: 0,
        EpochenKodexGeltung.EPOCHAL: 1,
        EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL: 2,
    })
    _TYP_MAP.update({
        EpochenKodexGeltung.GESPERRT: EpochenKodexTyp.SCHUTZ_EPOCHE,
        EpochenKodexGeltung.EPOCHAL: EpochenKodexTyp.ORDNUNGS_EPOCHE,
        EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL: EpochenKodexTyp.SOUVERAENITAETS_EPOCHE,
    })
    _PROZEDUR_MAP.update({
        EpochenKodexGeltung.GESPERRT: EpochenKodexProzedur.NOTPROZEDUR,
        EpochenKodexGeltung.EPOCHAL: EpochenKodexProzedur.REGELPROTOKOLL,
        EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL: EpochenKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        QuellenChartaGeltung.GESPERRT: EpochenKodexGeltung.GESPERRT,
        QuellenChartaGeltung.QUELLENKRITISCH: EpochenKodexGeltung.EPOCHAL,
        QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH: EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL,
    })


class EpochenKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    EPOCHAL = "epochal"
    GRUNDLEGEND_EPOCHAL = "grundlegend-epochal"


class EpochenKodexTyp(Enum):
    SCHUTZ_EPOCHE = "schutz-epoche"
    ORDNUNGS_EPOCHE = "ordnungs-epoche"
    SOUVERAENITAETS_EPOCHE = "souveraenitaets-epoche"


class EpochenKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class EpochenKodexNorm:
    epochen_kodex_id: str
    geschichts_typ: EpochenKodexTyp
    prozedur: EpochenKodexProzedur
    geltung: EpochenKodexGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class EpochenKodex:
    kodex_id: str
    quellen_charta: QuellenCharta
    normen: tuple[EpochenKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.epochen_kodex_id for n in self.normen
            if n.geltung is EpochenKodexGeltung.GESPERRT
        )

    @property
    def epochal_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.epochen_kodex_id for n in self.normen
            if n.geltung is EpochenKodexGeltung.EPOCHAL
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.epochen_kodex_id for n in self.normen
            if n.geltung is EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL
        )

    @property
    def kodex_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is EpochenKodexGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is EpochenKodexGeltung.EPOCHAL for n in self.normen):
            return SimpleNamespace(status="kodex-epochal")
        return SimpleNamespace(status="kodex-grundlegend-epochal")


_init_map()


def build_epochen_kodex(
    quellen_charta: QuellenCharta | None = None,
    *,
    kodex_id: str = "epochen-kodex",
) -> EpochenKodex:
    if quellen_charta is None:
        quellen_charta = build_quellen_charta(charta_id=f"{kodex_id}-charta")
    normen: list[EpochenKodexNorm] = []
    for parent_norm in quellen_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.quellen_charta_id.removeprefix(f'{quellen_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EpochenKodexGeltung.GRUNDLEGEND_EPOCHAL)
        normen.append(EpochenKodexNorm(
            epochen_kodex_id=new_id,
            geschichts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            geschichts_weight=new_weight,
            geschichts_tier=new_tier,
            canonical=is_canonical,
            geschichts_ids=parent_norm.geschichts_ids + (new_id,),
            geschichts_tags=parent_norm.geschichts_tags + (f"epochen-kodex:{new_geltung.value}",),
        ))
    return EpochenKodex(
        kodex_id=kodex_id,
        quellen_charta=quellen_charta,
        normen=tuple(normen),
    )
