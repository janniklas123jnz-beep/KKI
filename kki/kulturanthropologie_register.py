"""
#552 KulturanthropologieRegister — Grundlagen der Kulturanthropologie

Franz Boas (1911): The Mind of Primitive Man — kultureller Relativismus als methodisches Fundament:
  jede Kultur hat ihre eigene Logik und Würde; Kritik am Evolutionismus; historischer
  Partikularismus; Feldforschung als Basisinstrument kulturanthropologischer Erkenntnis.
Bronisław Malinowski (1922): Argonauts of the Western Pacific — Feldforschung & Funktionalismus:
  teilnehmende Beobachtung als Kernmethode; Kultur als integriertes Funktionssystem;
  jedes kulturelle Element erfüllt eine Funktion im Gesamtsystem der menschlichen Bedürfnisse.
Ruth Benedict (1934): Patterns of Culture — Kulturmuster als integrative Gestalt:
  jede Kultur hat ein dominantes Ethos/Muster (Apollinisch/Dionysisch); Konfigurationalismus;
  Persönlichkeit und Kultur als wechselseitig konstituierend; kulturelle Variabilität als Norm.

Leitsterns KulturanthropologieRegister: GESPERRT schützt anthropologische Grundmethoden,
ANTHROPOLOGISCH kodiert adaptive Feldforschungspraxis, GRUNDLEGEND_ANTHROPOLOGISCH
synthetisiert den vollen kulturanthropologischen Erkenntnisanspruch des Peta-Schwarms Leitstern. 🏺
Parent: KulturFeld (#551)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from .kultur_feld import (
    KulturFeld,
    KulturFeldGeltung,
    build_kultur_feld,
)

_WEIGHT_DELTA: dict["KulturanthropologieRegisterGeltung", float] = {}
_TIER_DELTA: dict["KulturanthropologieRegisterGeltung", int] = {}
_TYP_MAP: dict["KulturanthropologieRegisterGeltung", "KulturanthropologieRegisterTyp"] = {}
_PROZEDUR_MAP: dict["KulturanthropologieRegisterGeltung", "KulturanthropologieRegisterProzedur"] = {}
_GELTUNG_MAP: dict[KulturFeldGeltung, "KulturanthropologieRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KulturanthropologieRegisterGeltung.GESPERRT: 0.0,
        KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH: 0.05,
        KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        KulturanthropologieRegisterGeltung.GESPERRT: 0,
        KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH: 1,
        KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH: 2,
    })
    _TYP_MAP.update({
        KulturanthropologieRegisterGeltung.GESPERRT: KulturanthropologieRegisterTyp.SCHUTZ_ANTHROPOLOGIE,
        KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH: KulturanthropologieRegisterTyp.ORDNUNGS_ANTHROPOLOGIE,
        KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH: KulturanthropologieRegisterTyp.SOUVERAENITAETS_ANTHROPOLOGIE,
    })
    _PROZEDUR_MAP.update({
        KulturanthropologieRegisterGeltung.GESPERRT: KulturanthropologieRegisterProzedur.NOTPROZEDUR,
        KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH: KulturanthropologieRegisterProzedur.REGELPROTOKOLL,
        KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH: KulturanthropologieRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KulturFeldGeltung.GESPERRT: KulturanthropologieRegisterGeltung.GESPERRT,
        KulturFeldGeltung.KULTURELL: KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH,
        KulturFeldGeltung.GRUNDLEGEND_KULTURELL: KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH,
    })


class KulturanthropologieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    ANTHROPOLOGISCH = "anthropologisch"
    GRUNDLEGEND_ANTHROPOLOGISCH = "grundlegend-anthropologisch"


class KulturanthropologieRegisterTyp(Enum):
    SCHUTZ_ANTHROPOLOGIE = "schutz-anthropologie"
    ORDNUNGS_ANTHROPOLOGIE = "ordnungs-anthropologie"
    SOUVERAENITAETS_ANTHROPOLOGIE = "souveraenitaets-anthropologie"


class KulturanthropologieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KulturanthropologieRegisterNorm:
    kulturanthropologie_register_id: str
    kultur_typ: KulturanthropologieRegisterTyp
    prozedur: KulturanthropologieRegisterProzedur
    geltung: KulturanthropologieRegisterGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturanthropologieRegister:
    register_id: str
    kultur_feld: KulturFeld
    normen: tuple[KulturanthropologieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kulturanthropologie_register_id
            for n in self.normen
            if n.geltung is KulturanthropologieRegisterGeltung.GESPERRT
        )

    @property
    def anthropologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kulturanthropologie_register_id
            for n in self.normen
            if n.geltung is KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kulturanthropologie_register_id
            for n in self.normen
            if n.geltung is KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH
        )

    @property
    def register_signal(self) -> SimpleNamespace:
        if any(n.geltung is KulturanthropologieRegisterGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is KulturanthropologieRegisterGeltung.ANTHROPOLOGISCH for n in self.normen):
            return SimpleNamespace(status="register-anthropologisch")
        return SimpleNamespace(status="register-grundlegend-anthropologisch")


_init_map()


def build_kulturanthropologie_register(
    kultur_feld: KulturFeld | None = None,
    *,
    register_id: str = "kulturanthropologie-register",
) -> KulturanthropologieRegister:
    if kultur_feld is None:
        kultur_feld = build_kultur_feld(feld_id=f"{register_id}-feld")

    normen: list[KulturanthropologieRegisterNorm] = []
    for parent_norm in kultur_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.kultur_feld_id.removeprefix(f'{kultur_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (
            new_geltung is KulturanthropologieRegisterGeltung.GRUNDLEGEND_ANTHROPOLOGISCH
        )
        normen.append(
            KulturanthropologieRegisterNorm(
                kulturanthropologie_register_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"kulturanthropologie-register:{new_geltung.value}",),
            )
        )
    return KulturanthropologieRegister(
        register_id=register_id,
        kultur_feld=kultur_feld,
        normen=tuple(normen),
    )
