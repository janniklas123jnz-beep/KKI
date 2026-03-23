"""
#502 UtilitarismusRegister — Bentham/Mill/Singer Grundlagen des Utilitarismus

Jeremy Bentham (1789): Einführung in die Prinzipien der Moral und Gesetzgebung — Hedonic
  Calculus: Glück messbar nach Intensität, Dauer, Gewissheit, Nähe, Fruchtbarkeit, Reinheit,
  Ausdehnung; Prinzip des größten Glücks der größten Zahl als Handlungsmaßstab.
John Stuart Mill (1863): Utilitarismus — qualitative Unterschiede des Glücks; höhere geistige
  Freuden vs. niedere körperliche Freuden; "besser unzufrieden Sokrates als zufriedenes Schwein".
Peter Singer (1975): Tierbefreiung / Präferenz-Utilitarismus — moralischer Kreis umfasst alle
  leidensfähigen Wesen; effektiver Altruismus als rationale Praxis maximaler Nutzenoptimierung.
Henry Sidgwick (1874): Methoden der Ethik — rationale Grundlagen des Utilitarismus; Synthese
  von Egoismus, intuitivem Moralismus und Utilitarismus; Axiome der Universalität und Wohlwollen.
Leitsterns Peta-Schwarm verankert utilitaristische Kalkulation als operatives Kernprinzip:
GESPERRT sichert unveräußerliche Nutzenminima, UTILITARISTISCH ermöglicht adaptive Maximierung
kollektiven Wohlergehens über Millionen Agenten, GRUNDLEGEND_UTILITARISTISCH synthetisiert das
vollständige utilitaristische Fundament für souveräne Peta-Schwarm-Entscheidungen. ⚖️
Parent: EthikFeld (#501)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ethik_feld import (
    EthikFeld,
    EthikFeldGeltung,
    build_ethik_feld,
)

_GELTUNG_MAP: dict[EthikFeldGeltung, "UtilitarismusRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EthikFeldGeltung.GESPERRT] = UtilitarismusRegisterGeltung.GESPERRT
    _GELTUNG_MAP[EthikFeldGeltung.ETHISCH] = UtilitarismusRegisterGeltung.UTILITARISTISCH
    _GELTUNG_MAP[EthikFeldGeltung.GRUNDLEGEND_ETHISCH] = UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH


class UtilitarismusRegisterTyp(Enum):
    SCHUTZ_UTILITARISMUS = "schutz-utilitarismus"
    ORDNUNGS_UTILITARISMUS = "ordnungs-utilitarismus"
    SOUVERAENITAETS_UTILITARISMUS = "souveraenitaets-utilitarismus"


class UtilitarismusRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class UtilitarismusRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    UTILITARISTISCH = "utilitaristisch"
    GRUNDLEGEND_UTILITARISTISCH = "grundlegend-utilitaristisch"


_init_map()

_TYP_MAP: dict[UtilitarismusRegisterGeltung, UtilitarismusRegisterTyp] = {
    UtilitarismusRegisterGeltung.GESPERRT: UtilitarismusRegisterTyp.SCHUTZ_UTILITARISMUS,
    UtilitarismusRegisterGeltung.UTILITARISTISCH: UtilitarismusRegisterTyp.ORDNUNGS_UTILITARISMUS,
    UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH: UtilitarismusRegisterTyp.SOUVERAENITAETS_UTILITARISMUS,
}

_PROZEDUR_MAP: dict[UtilitarismusRegisterGeltung, UtilitarismusRegisterProzedur] = {
    UtilitarismusRegisterGeltung.GESPERRT: UtilitarismusRegisterProzedur.NOTPROZEDUR,
    UtilitarismusRegisterGeltung.UTILITARISTISCH: UtilitarismusRegisterProzedur.REGELPROTOKOLL,
    UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH: UtilitarismusRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[UtilitarismusRegisterGeltung, float] = {
    UtilitarismusRegisterGeltung.GESPERRT: 0.0,
    UtilitarismusRegisterGeltung.UTILITARISTISCH: 0.04,
    UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH: 0.08,
}

_TIER_DELTA: dict[UtilitarismusRegisterGeltung, int] = {
    UtilitarismusRegisterGeltung.GESPERRT: 0,
    UtilitarismusRegisterGeltung.UTILITARISTISCH: 1,
    UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH: 2,
}


@dataclass(frozen=True)
class UtilitarismusRegisterNorm:
    utilitarismus_register_id: str
    utilitarismus_typ: UtilitarismusRegisterTyp
    prozedur: UtilitarismusRegisterProzedur
    geltung: UtilitarismusRegisterGeltung
    utilitarismus_weight: float
    utilitarismus_tier: int
    canonical: bool
    utilitarismus_ids: tuple[str, ...]
    utilitarismus_tags: tuple[str, ...]


@dataclass(frozen=True)
class UtilitarismusRegister:
    register_id: str
    ethik_feld: EthikFeld
    normen: tuple[UtilitarismusRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.utilitarismus_register_id for n in self.normen if n.geltung is UtilitarismusRegisterGeltung.GESPERRT)

    @property
    def utilitaristisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.utilitarismus_register_id for n in self.normen if n.geltung is UtilitarismusRegisterGeltung.UTILITARISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.utilitarismus_register_id for n in self.normen if n.geltung is UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH)

    @property
    def register_signal(self):
        if any(n.geltung is UtilitarismusRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is UtilitarismusRegisterGeltung.UTILITARISTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-utilitaristisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-utilitaristisch")


def build_utilitarismus_register(
    ethik_feld: EthikFeld | None = None,
    *,
    register_id: str = "utilitarismus-register",
) -> UtilitarismusRegister:
    if ethik_feld is None:
        ethik_feld = build_ethik_feld(feld_id=f"{register_id}-feld")

    normen: list[UtilitarismusRegisterNorm] = []
    for parent_norm in ethik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.ethik_feld_id.removeprefix(f'{ethik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.ethik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.ethik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH)
        normen.append(
            UtilitarismusRegisterNorm(
                utilitarismus_register_id=new_id,
                utilitarismus_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                utilitarismus_weight=new_weight,
                utilitarismus_tier=new_tier,
                canonical=is_canonical,
                utilitarismus_ids=parent_norm.ethik_ids + (new_id,),
                utilitarismus_tags=parent_norm.ethik_tags + (f"utilitarismus-register:{new_geltung.value}",),
            )
        )
    return UtilitarismusRegister(
        register_id=register_id,
        ethik_feld=ethik_feld,
        normen=tuple(normen),
    )
