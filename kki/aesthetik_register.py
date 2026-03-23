"""
#572 AesthetikRegister — Baumgarten/Burke/Schiller Kunstwissenschaft Ästhetik

Alexander Baumgarten (1750): Aesthetica — Begründung der Ästhetik als eigenständige
  philosophische Disziplin; sinnliche Erkenntnis als niedere Erkenntnisform mit
  eigenem epistemischen Wert; Schönheit als Vollkommenheit der sinnlichen Erkenntnis;
  Geschmack als Vermögen des ästhetischen Urteils im Peta-Schwarm Leitstern.
Edmund Burke (1757): A Philosophical Enquiry into the Sublime and Beautiful —
  Unterscheidung von Erhabenem und Schönem als psychophysiologische Kategorien;
  das Erhabene als Lustgefühl bei drohender Gefahr aus sicherer Distanz; Schönheit
  als soziale Qualität; Empirie des ästhetischen Erlebens im Peta-Schwarm Leitstern.
Friedrich Schiller (1795): Über die ästhetische Erziehung des Menschen — Spieltrieb
  als Brücke zwischen Natur und Vernunft; ästhetische Freiheit als Voraussetzung
  politischer Freiheit; der ästhetische Staat als Ideal; Schönheit als lebende Gestalt
  im Peta-Schwarm Leitstern. 🎭🌺
Parent: KunstFeld (#571)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kunst_feld import (
    KunstFeld,
    KunstFeldGeltung,
    build_kunst_feld,
)

_WEIGHT_DELTA: dict["AesthetikRegisterGeltung", float] = {}
_TIER_DELTA: dict["AesthetikRegisterGeltung", int] = {}
_TYP_MAP: dict["AesthetikRegisterGeltung", "AesthetikRegisterTyp"] = {}
_PROZEDUR_MAP: dict["AesthetikRegisterGeltung", "AesthetikRegisterProzedur"] = {}
_GELTUNG_MAP: dict[KunstFeldGeltung, "AesthetikRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AesthetikRegisterGeltung.GESPERRT: 0.0,
        AesthetikRegisterGeltung.AESTHETISCH_AKTIV: 0.05,
        AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        AesthetikRegisterGeltung.GESPERRT: 0,
        AesthetikRegisterGeltung.AESTHETISCH_AKTIV: 1,
        AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        AesthetikRegisterGeltung.GESPERRT: AesthetikRegisterTyp.SCHUTZ_AESTHETIKREGISTER,
        AesthetikRegisterGeltung.AESTHETISCH_AKTIV: AesthetikRegisterTyp.ORDNUNGS_AESTHETIKREGISTER,
        AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV: AesthetikRegisterTyp.SOUVERAENITAETS_AESTHETIKREGISTER,
    })
    _PROZEDUR_MAP.update({
        AesthetikRegisterGeltung.GESPERRT: AesthetikRegisterProzedur.NOTPROZEDUR,
        AesthetikRegisterGeltung.AESTHETISCH_AKTIV: AesthetikRegisterProzedur.REGELPROTOKOLL,
        AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV: AesthetikRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KunstFeldGeltung.GESPERRT: AesthetikRegisterGeltung.GESPERRT,
        KunstFeldGeltung.AESTHETISCH_SOUVERAEN: AesthetikRegisterGeltung.AESTHETISCH_AKTIV,
        KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN: AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV,
    })


class AesthetikRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    AESTHETISCH_AKTIV = "aesthetisch-aktiv"
    GRUNDLEGEND_AESTHETISCH_AKTIV = "grundlegend-aesthetisch-aktiv"


class AesthetikRegisterTyp(Enum):
    SCHUTZ_AESTHETIKREGISTER = "schutz-aesthetikregister"
    ORDNUNGS_AESTHETIKREGISTER = "ordnungs-aesthetikregister"
    SOUVERAENITAETS_AESTHETIKREGISTER = "souveraenitaets-aesthetikregister"


class AesthetikRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class AesthetikRegisterNorm:
    aesthetik_register_id: str
    kunst_typ: AesthetikRegisterTyp
    prozedur: AesthetikRegisterProzedur
    geltung: AesthetikRegisterGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class AesthetikRegister:
    register_id: str
    kunst_feld: KunstFeld
    normen: tuple[AesthetikRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aesthetik_register_id for n in self.normen if n.geltung is AesthetikRegisterGeltung.GESPERRT)

    @property
    def aesthetisch_aktiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aesthetik_register_id for n in self.normen if n.geltung is AesthetikRegisterGeltung.AESTHETISCH_AKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aesthetik_register_id for n in self.normen if n.geltung is AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV)

    @property
    def register_signal(self):
        if any(n.geltung is AesthetikRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is AesthetikRegisterGeltung.AESTHETISCH_AKTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-aesthetisch-aktiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-aesthetisch-aktiv")


_init_map()


def build_aesthetik_register(
    kunst_feld: KunstFeld | None = None,
    *,
    register_id: str = "aesthetik-register",
) -> AesthetikRegister:
    if kunst_feld is None:
        kunst_feld = build_kunst_feld(feld_id=f"{register_id}-feld")

    normen: list[AesthetikRegisterNorm] = []
    for parent_norm in kunst_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.kunst_feld_id.removeprefix(f'{kunst_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AesthetikRegisterGeltung.GRUNDLEGEND_AESTHETISCH_AKTIV)
        normen.append(
            AesthetikRegisterNorm(
                aesthetik_register_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"aesthetik-register:{new_geltung.value}",),
            )
        )
    return AesthetikRegister(
        register_id=register_id,
        kunst_feld=kunst_feld,
        normen=tuple(normen),
    )
