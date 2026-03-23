"""
#551 KulturFeld — Grundlagen der Kulturwissenschaft & Kulturanthropologie

Edward Burnett Tylor (1871): Primitive Culture — erste wissenschaftliche Definition von Kultur:
  "jenes komplexe Ganze, das Wissen, Glauben, Kunst, Moral, Recht, Brauch und alle anderen
  Fähigkeiten und Gewohnheiten umfasst, die der Mensch als Mitglied der Gesellschaft erworben hat";
  Evolutionismus als Grundrahmen; vergleichende Methode in der Ethnologie.
Franz Boas (1911): The Mind of Primitive Man — Kulturrelativismus als methodisches Fundament:
  jede Kultur hat ihre eigene Logik und Würde; Kritik am Evolutionismus; historischer
  Partikularismus; Feldforschung als Basisinstrument kulturanthropologischer Erkenntnis.
Clifford Geertz (1973): The Interpretation of Cultures — Thick Description als Methode:
  Kultur als Text; Weber'sches Bedeutungsgewebe; semiotischer Kulturbegriff; Ethnographie
  als Interpretation von Interpretationen; Kultur als Kontext, nicht als Ursache.
Leitsterns KulturFeld: Eingangstor der Kulturwissenschaft — GESPERRT schützt kulturelle
Grundmethoden, KULTURELL kodiert adaptive Kulturinterpretation, GRUNDLEGEND_KULTURELL
synthetisiert den vollen kulturwissenschaftlichen Erkenntnisanspruch des Peta-Schwarms Leitstern. 🎭
Parent: GeschichtsVerfassung (#550)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .geschichts_verfassung import (
    GeschichtsVerfassung,
    GeschichtsVerfassungsGeltung,
    build_geschichts_verfassung,
)

_WEIGHT_DELTA: dict["KulturFeldGeltung", float] = {}
_TIER_DELTA: dict["KulturFeldGeltung", int] = {}
_TYP_MAP: dict["KulturFeldGeltung", "KulturFeldTyp"] = {}
_PROZEDUR_MAP: dict["KulturFeldGeltung", "KulturFeldProzedur"] = {}
_GELTUNG_MAP: dict[GeschichtsVerfassungsGeltung, "KulturFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KulturFeldGeltung.GESPERRT: 0.0,
        KulturFeldGeltung.KULTURELL: 0.05,
        KulturFeldGeltung.GRUNDLEGEND_KULTURELL: 0.1,
    })
    _TIER_DELTA.update({
        KulturFeldGeltung.GESPERRT: 0,
        KulturFeldGeltung.KULTURELL: 1,
        KulturFeldGeltung.GRUNDLEGEND_KULTURELL: 2,
    })
    _TYP_MAP.update({
        KulturFeldGeltung.GESPERRT: KulturFeldTyp.SCHUTZ_KULTUR,
        KulturFeldGeltung.KULTURELL: KulturFeldTyp.ORDNUNGS_KULTUR,
        KulturFeldGeltung.GRUNDLEGEND_KULTURELL: KulturFeldTyp.SOUVERAENITAETS_KULTUR,
    })
    _PROZEDUR_MAP.update({
        KulturFeldGeltung.GESPERRT: KulturFeldProzedur.NOTPROZEDUR,
        KulturFeldGeltung.KULTURELL: KulturFeldProzedur.REGELPROTOKOLL,
        KulturFeldGeltung.GRUNDLEGEND_KULTURELL: KulturFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        GeschichtsVerfassungsGeltung.GESPERRT: KulturFeldGeltung.GESPERRT,
        GeschichtsVerfassungsGeltung.HISTORISCH_SOUVERAEN: KulturFeldGeltung.KULTURELL,
        GeschichtsVerfassungsGeltung.GRUNDLEGEND_HISTORISCH_SOUVERAEN: KulturFeldGeltung.GRUNDLEGEND_KULTURELL,
    })


class KulturFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    KULTURELL = "kulturell"
    GRUNDLEGEND_KULTURELL = "grundlegend-kulturell"


class KulturFeldTyp(Enum):
    SCHUTZ_KULTUR = "schutz-kultur"
    ORDNUNGS_KULTUR = "ordnungs-kultur"
    SOUVERAENITAETS_KULTUR = "souveraenitaets-kultur"


class KulturFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KulturFeldNorm:
    kultur_feld_id: str
    kultur_typ: KulturFeldTyp
    prozedur: KulturFeldProzedur
    geltung: KulturFeldGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturFeld:
    feld_id: str
    geschichts_verfassung: GeschichtsVerfassung
    normen: tuple[KulturFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kultur_feld_id for n in self.normen if n.geltung is KulturFeldGeltung.GESPERRT)

    @property
    def kulturell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kultur_feld_id for n in self.normen if n.geltung is KulturFeldGeltung.KULTURELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kultur_feld_id for n in self.normen if n.geltung is KulturFeldGeltung.GRUNDLEGEND_KULTURELL)

    @property
    def feld_signal(self):
        if any(n.geltung is KulturFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is KulturFeldGeltung.KULTURELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-kulturell")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-kulturell")


_init_map()


def build_kultur_feld(
    geschichts_verfassung: GeschichtsVerfassung | None = None,
    *,
    feld_id: str = "kultur-feld",
) -> KulturFeld:
    if geschichts_verfassung is None:
        geschichts_verfassung = build_geschichts_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[KulturFeldNorm] = []
    for parent_norm in geschichts_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.geschichts_verfassung_id.removeprefix(f'{geschichts_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KulturFeldGeltung.GRUNDLEGEND_KULTURELL)
        normen.append(
            KulturFeldNorm(
                kultur_feld_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.geschichts_ids + (new_id,),
                kultur_tags=parent_norm.geschichts_tags + (f"kultur-feld:{new_geltung.value}",),
            )
        )
    return KulturFeld(
        feld_id=feld_id,
        geschichts_verfassung=geschichts_verfassung,
        normen=tuple(normen),
    )
