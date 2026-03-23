"""
#522 MarktRegister — Ricardo/Marshall/Walras Preismechanismus und Gleichgewicht

David Ricardo (1817): Grundsätze der politischen Ökonomie — komparativer Vorteil und
  Preisbildung; Werttheorie der Arbeit als Grundlage des Marktpreises; Renten- und
  Verteilungstheorie als Ausdruck von Marktkräften im Schwarm.
Alfred Marshall (1890): Principles of Economics — Angebot und Nachfrage als Gleichgewicht;
  Grenznutzentheorie und Elastizitätskonzept; Markt als dezentraler Koordinationsmechanismus
  für Millionen von Agenten-Transaktionen.
Léon Walras (1874): Éléments d'économie politique pure — Allgemeines Gleichgewicht aller
  Märkte simultan; Tâtonnement als Suchprozess des Marktes; mathematische Fundierung der
  Neoklassischen Synthese als Basis der Schwarmökonomie.
Friedrich von Hayek (1945): The Use of Knowledge in Society — Markt als
  Informationsaggregator; Preissystem als Signalübertragung; dezentrales Wissen und
  spontane Ordnung im Peta-Schwarm Leitstern. 📈
Module #522, Parent: WirtschaftsFeld (#521)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wirtschafts_feld import (
    WirtschaftsFeld,
    WirtschaftsFeldGeltung,
    build_wirtschafts_feld,
)

_WEIGHT_DELTA: dict["MarktRegisterGeltung", float] = {}
_TIER_DELTA: dict["MarktRegisterGeltung", int] = {}
_TYP_MAP: dict["MarktRegisterGeltung", "MarktRegisterTyp"] = {}
_PROZEDUR_MAP: dict["MarktRegisterGeltung", "MarktRegisterProzedur"] = {}
_GELTUNG_MAP: dict[WirtschaftsFeldGeltung, "MarktRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MarktRegisterGeltung.GESPERRT: 0.0,
        MarktRegisterGeltung.MARKTLICH: 0.05,
        MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH: 0.1,
    })
    _TIER_DELTA.update({
        MarktRegisterGeltung.GESPERRT: 0,
        MarktRegisterGeltung.MARKTLICH: 1,
        MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH: 2,
    })
    _TYP_MAP.update({
        MarktRegisterGeltung.GESPERRT: MarktRegisterTyp.SCHUTZ_MARKT,
        MarktRegisterGeltung.MARKTLICH: MarktRegisterTyp.ORDNUNGS_MARKT,
        MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH: MarktRegisterTyp.SOUVERAENITAETS_MARKT,
    })
    _PROZEDUR_MAP.update({
        MarktRegisterGeltung.GESPERRT: MarktRegisterProzedur.NOTPROZEDUR,
        MarktRegisterGeltung.MARKTLICH: MarktRegisterProzedur.REGELPROTOKOLL,
        MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH: MarktRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        WirtschaftsFeldGeltung.GESPERRT: MarktRegisterGeltung.GESPERRT,
        WirtschaftsFeldGeltung.WIRTSCHAFTLICH: MarktRegisterGeltung.MARKTLICH,
        WirtschaftsFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH,
    })


class MarktRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    MARKTLICH = "marktlich"
    GRUNDLEGEND_MARKTLICH = "grundlegend-marktlich"


class MarktRegisterTyp(Enum):
    SCHUTZ_MARKT = "schutz-markt"
    ORDNUNGS_MARKT = "ordnungs-markt"
    SOUVERAENITAETS_MARKT = "souveraenitaets-markt"


class MarktRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class MarktRegisterNorm:
    markt_register_id: str
    markt_typ: MarktRegisterTyp
    prozedur: MarktRegisterProzedur
    geltung: MarktRegisterGeltung
    markt_weight: float
    markt_tier: int
    canonical: bool
    markt_ids: tuple[str, ...]
    markt_tags: tuple[str, ...]


@dataclass(frozen=True)
class MarktRegister:
    register_id: str
    wirtschafts_feld: WirtschaftsFeld
    normen: tuple[MarktRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.markt_register_id for n in self.normen if n.geltung is MarktRegisterGeltung.GESPERRT)

    @property
    def marktlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.markt_register_id for n in self.normen if n.geltung is MarktRegisterGeltung.MARKTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.markt_register_id for n in self.normen if n.geltung is MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH)

    @property
    def register_signal(self):
        if any(n.geltung is MarktRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is MarktRegisterGeltung.MARKTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-marktlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-marktlich")


_init_map()


def build_markt_register(
    wirtschafts_feld: WirtschaftsFeld | None = None,
    *,
    register_id: str = "markt-register",
) -> MarktRegister:
    if wirtschafts_feld is None:
        wirtschafts_feld = build_wirtschafts_feld(
            feld_id=f"{register_id}-wirtschafts-feld"
        )

    normen: list[MarktRegisterNorm] = []
    for parent_norm in wirtschafts_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.wirtschafts_feld_id.removeprefix(f'{wirtschafts_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.wirtschafts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.wirtschafts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MarktRegisterGeltung.GRUNDLEGEND_MARKTLICH)
        normen.append(
            MarktRegisterNorm(
                markt_register_id=new_id,
                markt_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                markt_weight=new_weight,
                markt_tier=new_tier,
                canonical=is_canonical,
                markt_ids=parent_norm.wirtschafts_ids + (new_id,),
                markt_tags=parent_norm.wirtschafts_tags + (f"markt-register:{new_geltung.value}",),
            )
        )
    return MarktRegister(
        register_id=register_id,
        wirtschafts_feld=wirtschafts_feld,
        normen=tuple(normen),
    )
