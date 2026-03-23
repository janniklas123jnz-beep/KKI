"""
#562 KommunikationsRegister — Habermas/Luhmann/Shannon Kommunikationstheorie Register

Jürgen Habermas (1981): Theorie des kommunikativen Handelns — kommunikatives Handeln
  als verständigungsorientiertes Sprechen; Geltungsansprüche in der Diskurspragmatik;
  Lebenswelt vs. System als kommunikationstheoretische Grundspannung; ideale
  Sprechsituation als Regulativ im Peta-Schwarm Leitstern.
Niklas Luhmann (1984): Soziale Systeme — Kommunikation als dreistellige Selektion
  aus Information, Mitteilung, Verstehen; autopoietische Reproduktion sozialer Systeme;
  doppelte Kontingenz als Strukturbedingung; symbolisch generalisierte Kommunikationsmedien
  im Peta-Schwarm Leitstern.
Claude Shannon (1948): A Mathematical Theory of Communication — Informationsentropie
  als Maß der Unsicherheit; Kanalkapazität und Rauschen; Redundanz als Fehlerkorrektur;
  binäre Kodierung als universelles Medium im Peta-Schwarm Leitstern. 📡🗣️
Parent: MedienFeld (#561)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .medien_feld import (
    MedienFeld,
    MedienFeldGeltung,
    build_medien_feld,
)

_WEIGHT_DELTA: dict["KommunikationsRegisterGeltung", float] = {}
_TIER_DELTA: dict["KommunikationsRegisterGeltung", int] = {}
_TYP_MAP: dict["KommunikationsRegisterGeltung", "KommunikationsRegisterTyp"] = {}
_PROZEDUR_MAP: dict["KommunikationsRegisterGeltung", "KommunikationsRegisterProzedur"] = {}
_GELTUNG_MAP: dict[MedienFeldGeltung, "KommunikationsRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KommunikationsRegisterGeltung.GESPERRT: 0.0,
        KommunikationsRegisterGeltung.KOMMUNIKATIV: 0.05,
        KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV: 0.1,
    })
    _TIER_DELTA.update({
        KommunikationsRegisterGeltung.GESPERRT: 0,
        KommunikationsRegisterGeltung.KOMMUNIKATIV: 1,
        KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV: 2,
    })
    _TYP_MAP.update({
        KommunikationsRegisterGeltung.GESPERRT: KommunikationsRegisterTyp.SCHUTZ_KOMMUNIKATION,
        KommunikationsRegisterGeltung.KOMMUNIKATIV: KommunikationsRegisterTyp.ORDNUNGS_KOMMUNIKATION,
        KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV: KommunikationsRegisterTyp.SOUVERAENITAETS_KOMMUNIKATION,
    })
    _PROZEDUR_MAP.update({
        KommunikationsRegisterGeltung.GESPERRT: KommunikationsRegisterProzedur.NOTPROZEDUR,
        KommunikationsRegisterGeltung.KOMMUNIKATIV: KommunikationsRegisterProzedur.REGELPROTOKOLL,
        KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV: KommunikationsRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        MedienFeldGeltung.GESPERRT: KommunikationsRegisterGeltung.GESPERRT,
        MedienFeldGeltung.MEDIENKULTURELL: KommunikationsRegisterGeltung.KOMMUNIKATIV,
        MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL: KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV,
    })


class KommunikationsRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMMUNIKATIV = "kommunikativ"
    GRUNDLEGEND_KOMMUNIKATIV = "grundlegend-kommunikativ"


class KommunikationsRegisterTyp(Enum):
    SCHUTZ_KOMMUNIKATION = "schutz-kommunikation"
    ORDNUNGS_KOMMUNIKATION = "ordnungs-kommunikation"
    SOUVERAENITAETS_KOMMUNIKATION = "souveraenitaets-kommunikation"


class KommunikationsRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KommunikationsRegisterNorm:
    kommunikations_register_id: str
    medien_typ: KommunikationsRegisterTyp
    prozedur: KommunikationsRegisterProzedur
    geltung: KommunikationsRegisterGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class KommunikationsRegister:
    register_id: str
    medien_feld: MedienFeld
    normen: tuple[KommunikationsRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kommunikations_register_id for n in self.normen
            if n.geltung is KommunikationsRegisterGeltung.GESPERRT
        )

    @property
    def kommunikativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kommunikations_register_id for n in self.normen
            if n.geltung is KommunikationsRegisterGeltung.KOMMUNIKATIV
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kommunikations_register_id for n in self.normen
            if n.geltung is KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV
        )

    @property
    def register_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is KommunikationsRegisterGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is KommunikationsRegisterGeltung.KOMMUNIKATIV for n in self.normen):
            return SimpleNamespace(status="register-kommunikativ")
        return SimpleNamespace(status="register-grundlegend-kommunikativ")


_init_map()


def build_kommunikations_register(
    medien_feld: MedienFeld | None = None,
    *,
    register_id: str = "kommunikations-register",
) -> KommunikationsRegister:
    if medien_feld is None:
        medien_feld = build_medien_feld(feld_id=f"{register_id}-feld")

    normen: list[KommunikationsRegisterNorm] = []
    for parent_norm in medien_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.medien_feld_id.removeprefix(f'{medien_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV)
        normen.append(
            KommunikationsRegisterNorm(
                kommunikations_register_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"kommunikations-register:{new_geltung.value}",),
            )
        )
    return KommunikationsRegister(
        register_id=register_id,
        medien_feld=medien_feld,
        normen=tuple(normen),
    )
