"""
#543 QuellenCharta — Charta der Quellenkritik und Quellenklassifikation

Ernst Bernheim (1889): Lehrbuch der Historischen Methode — systematische Quellenklassifikation;
  Unterscheidung von Tradition und Überrest als Grundtypologie historischer Quellen;
  Quellenkritik als mehrstufiges Verfahren von äußerer und innerer Kritik.
Theodor Mommsen (1854): Römische Geschichte — kritische Erschließung antiker Quellen;
  Inschriftenkunde (CIL) als monumentale Quellenedition für die Altertumswissenschaft;
  philologisch-historische Methode als Maßstab der Quelleninterpretation.
Marc Bloch (1949): Apologie der Geschichte — Zeugenkritik und Unfreiwilligkeit der Quelle;
  Unterscheidung zwischen bewussten und unbewussten Zeugnissen der Vergangenheit;
  kritisches Misstrauen als epistemische Grundhaltung des Historikers gegenüber Quellen.
Parent: HistoriographieRegister (#542)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .historiographie_register import (
    HistoriographieRegister,
    HistoriographieRegisterGeltung,
    build_historiographie_register,
)

_WEIGHT_DELTA: dict["QuellenChartaGeltung", float] = {}
_TIER_DELTA: dict["QuellenChartaGeltung", int] = {}
_TYP_MAP: dict["QuellenChartaGeltung", "QuellenChartaTyp"] = {}
_PROZEDUR_MAP: dict["QuellenChartaGeltung", "QuellenChartaProzedur"] = {}
_GELTUNG_MAP: dict[HistoriographieRegisterGeltung, "QuellenChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        QuellenChartaGeltung.GESPERRT: 0.0,
        QuellenChartaGeltung.QUELLENKRITISCH: 0.05,
        QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH: 0.1,
    })
    _TIER_DELTA.update({
        QuellenChartaGeltung.GESPERRT: 0,
        QuellenChartaGeltung.QUELLENKRITISCH: 1,
        QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH: 2,
    })
    _TYP_MAP.update({
        QuellenChartaGeltung.GESPERRT: QuellenChartaTyp.SCHUTZ_QUELLE,
        QuellenChartaGeltung.QUELLENKRITISCH: QuellenChartaTyp.ORDNUNGS_QUELLE,
        QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH: QuellenChartaTyp.SOUVERAENITAETS_QUELLE,
    })
    _PROZEDUR_MAP.update({
        QuellenChartaGeltung.GESPERRT: QuellenChartaProzedur.NOTPROZEDUR,
        QuellenChartaGeltung.QUELLENKRITISCH: QuellenChartaProzedur.REGELPROTOKOLL,
        QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH: QuellenChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        HistoriographieRegisterGeltung.GESPERRT: QuellenChartaGeltung.GESPERRT,
        HistoriographieRegisterGeltung.HISTORIOGRAPHISCH: QuellenChartaGeltung.QUELLENKRITISCH,
        HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH: QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH,
    })


class QuellenChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    QUELLENKRITISCH = "quellenkritisch"
    GRUNDLEGEND_QUELLENKRITISCH = "grundlegend-quellenkritisch"


class QuellenChartaTyp(Enum):
    SCHUTZ_QUELLE = "schutz-quelle"
    ORDNUNGS_QUELLE = "ordnungs-quelle"
    SOUVERAENITAETS_QUELLE = "souveraenitaets-quelle"


class QuellenChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class QuellenChartaNorm:
    quellen_charta_id: str
    geschichts_typ: QuellenChartaTyp
    prozedur: QuellenChartaProzedur
    geltung: QuellenChartaGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuellenCharta:
    charta_id: str
    historiographie_register: HistoriographieRegister
    normen: tuple[QuellenChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.quellen_charta_id for n in self.normen
            if n.geltung is QuellenChartaGeltung.GESPERRT
        )

    @property
    def quellenkritisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.quellen_charta_id for n in self.normen
            if n.geltung is QuellenChartaGeltung.QUELLENKRITISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.quellen_charta_id for n in self.normen
            if n.geltung is QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH
        )

    @property
    def charta_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is QuellenChartaGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is QuellenChartaGeltung.QUELLENKRITISCH for n in self.normen):
            return SimpleNamespace(status="charta-quellenkritisch")
        return SimpleNamespace(status="charta-grundlegend-quellenkritisch")


_init_map()


def build_quellen_charta(
    historiographie_register: HistoriographieRegister | None = None,
    *,
    charta_id: str = "quellen-charta",
) -> QuellenCharta:
    if historiographie_register is None:
        historiographie_register = build_historiographie_register(
            register_id=f"{charta_id}-register"
        )
    normen: list[QuellenChartaNorm] = []
    for parent_norm in historiographie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.historiographie_register_id.removeprefix(f'{historiographie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuellenChartaGeltung.GRUNDLEGEND_QUELLENKRITISCH)
        normen.append(QuellenChartaNorm(
            quellen_charta_id=new_id,
            geschichts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            geschichts_weight=new_weight,
            geschichts_tier=new_tier,
            canonical=is_canonical,
            geschichts_ids=parent_norm.geschichts_ids + (new_id,),
            geschichts_tags=parent_norm.geschichts_tags + (f"quellen-charta:{new_geltung.value}",),
        ))
    return QuellenCharta(
        charta_id=charta_id,
        historiographie_register=historiographie_register,
        normen=tuple(normen),
    )
