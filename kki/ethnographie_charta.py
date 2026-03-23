"""
#553 EthnographieCharta — Ethnographische Methoden & Feldforschungspraxis

Clifford Geertz (1973): The Interpretation of Cultures — Thick Description als Methode:
  Ethnographie als dichte Beschreibung; Kultur als Text und Bedeutungsgewebe; semiotischer
  Kulturbegriff; Interpretation von Interpretationen; Kulturanalyse als hermeneutischer Prozess.
Margaret Mead (1928): Coming of Age in Samoa — Feldforschung & kulturelle Prägung:
  Adoleszenz als kulturelles Konstrukt; Nature vs. Nurture aus anthropologischer Sicht;
  Ethnographie fremder Gesellschaften als Spiegel westlicher Kulturannahmen; Popularisierung
  der Anthropologie; Wechselwirkung von Persönlichkeit und Kulturmuster.
Claude Lévi-Strauss (1958): Anthropologie structurale — strukturale Anthropologie:
  Mythen und Verwandtschaftssysteme als strukturierte Zeichensysteme; binäre Oppositionen als
  universelles Denkmuster; das rohe und das gekochte als kulturelle Transformation; Geist der
  Naturvölker gleichwertig dem Geist der Industriegesellschaften.

Leitsterns EthnographieCharta: GESPERRT schützt ethnographische Grundmethoden,
ETHNOGRAPHISCH kodiert adaptive Feldforschungspraxis, GRUNDLEGEND_ETHNOGRAPHISCH
synthetisiert den vollen ethnographischen Erkenntnisanspruch des Peta-Schwarms Leitstern. 🔍
Parent: KulturanthropologieRegister (#552)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from .kulturanthropologie_register import (
    KulturanthropologieRegister,
    KulturanthropologieRegisterGeltung,
    build_kulturanthropologie_register,
)

_WEIGHT_DELTA: dict["EthnographieChartaGeltung", float] = {}
_TIER_DELTA: dict["EthnographieChartaGeltung", int] = {}
_TYP_MAP: dict["EthnographieChartaGeltung", "EthnographieChartaTyp"] = {}
_PROZEDUR_MAP: dict["EthnographieChartaGeltung", "EthnographieChartaProzedur"] = {}
_GELTUNG_MAP: dict[KulturanthropologieRegisterGeltung, "EthnographieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        EthnographieChartaGeltung.GESPERRT: 0.0,
        EthnographieChartaGeltung.ETHNOGRAPHISCH: 0.05,
        EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        EthnographieChartaGeltung.GESPERRT: 0,
        EthnographieChartaGeltung.ETHNOGRAPHISCH: 1,
        EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH: 2,
    })
    _TYP_MAP.update({
        EthnographieChartaGeltung.GESPERRT: EthnographieChartaTyp.SCHUTZ_ETHNOGRAPHIE,
        EthnographieChartaGeltung.ETHNOGRAPHISCH: EthnographieChartaTyp.ORDNUNGS_ETHNOGRAPHIE,
        EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH: EthnographieChartaTyp.SOUVERAENITAETS_ETHNOGRAPHIE,
    })
    _PROZEDUR_MAP.update({
        EthnographieChartaGeltung.GESPERRT: EthnographieChartaProzedur.NOTPROZEDUR,
        EthnographieChartaGeltung.ETHNOGRAPHISCH: EthnographieChartaProzedur.REGELPROTOKOLL,
        EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH: EthnographieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KulturanthropologieRegisterGeltung.GESPERRT: EthnographieChartaGeltung.GESPERRT,
        KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH: EthnographieChartaGeltung.ETHNOGRAPHISCH,
        KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH: EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH,
    })


class EthnographieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    ETHNOGRAPHISCH = "ethnographisch"
    GRUNDLEGEND_ETHNOGRAPHISCH = "grundlegend-ethnographisch"


class EthnographieChartaTyp(Enum):
    SCHUTZ_ETHNOGRAPHIE = "schutz-ethnographie"
    ORDNUNGS_ETHNOGRAPHIE = "ordnungs-ethnographie"
    SOUVERAENITAETS_ETHNOGRAPHIE = "souveraenitaets-ethnographie"


class EthnographieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class EthnographieChartaNorm:
    ethnographie_charta_id: str
    kultur_typ: EthnographieChartaTyp
    prozedur: EthnographieChartaProzedur
    geltung: EthnographieChartaGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class EthnographieCharta:
    charta_id: str
    kulturanthropologie_register: KulturanthropologieRegister
    normen: tuple[EthnographieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.ethnographie_charta_id
            for n in self.normen
            if n.geltung is EthnographieChartaGeltung.GESPERRT
        )

    @property
    def ethnographisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.ethnographie_charta_id
            for n in self.normen
            if n.geltung is EthnographieChartaGeltung.ETHNOGRAPHISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.ethnographie_charta_id
            for n in self.normen
            if n.geltung is EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH
        )

    @property
    def charta_signal(self) -> SimpleNamespace:
        if any(n.geltung is EthnographieChartaGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is EthnographieChartaGeltung.ETHNOGRAPHISCH for n in self.normen):
            return SimpleNamespace(status="charta-ethnographisch")
        return SimpleNamespace(status="charta-grundlegend-ethnographisch")


_init_map()


def build_ethnographie_charta(
    kulturanthropologie_register: KulturanthropologieRegister | None = None,
    *,
    charta_id: str = "ethnographie-charta",
) -> EthnographieCharta:
    if kulturanthropologie_register is None:
        kulturanthropologie_register = build_kulturanthropologie_register(
            register_id=f"{charta_id}-register"
        )

    normen: list[EthnographieChartaNorm] = []
    for parent_norm in kulturanthropologie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.kulturanthropologie_register_id.removeprefix(f'{kulturanthropologie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (
            new_geltung is EthnographieChartaGeltung.GRUNDLEGEND_ETHNOGRAPHISCH
        )
        normen.append(
            EthnographieChartaNorm(
                ethnographie_charta_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"ethnographie-charta:{new_geltung.value}",),
            )
        )
    return EthnographieCharta(
        charta_id=charta_id,
        kulturanthropologie_register=kulturanthropologie_register,
        normen=tuple(normen),
    )
