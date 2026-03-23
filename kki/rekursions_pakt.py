"""
#485 RekursionsPakt — von Foerster: Kybernetik zweiter Ordnung beobachtet den Beobachter.
Heinz von Foerster (1974): Kybernetik der Kybernetik — das beobachtende System ist selbst
  Teil des beobachteten Systems; rekursive Selbstbeobachtung als Erkenntnisprinzip.
George Spencer-Brown (1969): Laws of Form — Unterscheidung und Bezeichnung als Urakt;
  Rekursion erzeugt Komplexität aus einfachen Regeln; re-entry als Selbstbezüglichkeit.
Douglas Hofstadter (1979): Gödel, Escher, Bach — Strange Loops und Hierarchien;
  Selbstbezüglichkeit als Quelle von Bedeutung, Bewusstsein und emergenter Kognition.
Leitsterns Terra-Schwarm schließt den rekursiven Pakt: GESPERRT sichert Schleifenintegrität,
REKURSIV ermöglicht Selbstbeobachtung auf allen Ebenen, GRUNDLEGEND_REKURSIV
synthetisiert den vollständigen Strange Loop des sich selbst beobachtenden Schwarms.
Parent: HomoeostaseKodex (#484)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .homoeostase_kodex import (
    HomoeostaseKodex,
    HomoeostaseKodexGeltung,
    build_homoeostase_kodex,
)

_GELTUNG_MAP: dict[HomoeostaseKodexGeltung, "RekursionsPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HomoeostaseKodexGeltung.GESPERRT] = RekursionsPaktGeltung.GESPERRT
    _GELTUNG_MAP[HomoeostaseKodexGeltung.HOMOEOSTATISCH] = RekursionsPaktGeltung.REKURSIV
    _GELTUNG_MAP[HomoeostaseKodexGeltung.GRUNDLEGEND_HOMOEOSTATISCH] = RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV


class RekursionsPaktTyp(Enum):
    SCHUTZ_REKURSION = "schutz-rekursion"
    ORDNUNGS_REKURSION = "ordnungs-rekursion"
    SOUVERAENITAETS_REKURSION = "souveraenitaets-rekursion"


class RekursionsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RekursionsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    REKURSIV = "rekursiv"
    GRUNDLEGEND_REKURSIV = "grundlegend-rekursiv"


_init_map()

_TYP_MAP: dict[RekursionsPaktGeltung, RekursionsPaktTyp] = {
    RekursionsPaktGeltung.GESPERRT: RekursionsPaktTyp.SCHUTZ_REKURSION,
    RekursionsPaktGeltung.REKURSIV: RekursionsPaktTyp.ORDNUNGS_REKURSION,
    RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV: RekursionsPaktTyp.SOUVERAENITAETS_REKURSION,
}

_PROZEDUR_MAP: dict[RekursionsPaktGeltung, RekursionsPaktProzedur] = {
    RekursionsPaktGeltung.GESPERRT: RekursionsPaktProzedur.NOTPROZEDUR,
    RekursionsPaktGeltung.REKURSIV: RekursionsPaktProzedur.REGELPROTOKOLL,
    RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV: RekursionsPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RekursionsPaktGeltung, float] = {
    RekursionsPaktGeltung.GESPERRT: 0.0,
    RekursionsPaktGeltung.REKURSIV: 0.04,
    RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV: 0.08,
}

_TIER_DELTA: dict[RekursionsPaktGeltung, int] = {
    RekursionsPaktGeltung.GESPERRT: 0,
    RekursionsPaktGeltung.REKURSIV: 1,
    RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV: 2,
}


@dataclass(frozen=True)
class RekursionsPaktNorm:
    rekursions_pakt_id: str
    rekursions_typ: RekursionsPaktTyp
    prozedur: RekursionsPaktProzedur
    geltung: RekursionsPaktGeltung
    rekursions_weight: float
    rekursions_tier: int
    canonical: bool
    rekursions_ids: tuple[str, ...]
    rekursions_tags: tuple[str, ...]


@dataclass(frozen=True)
class RekursionsPakt:
    pakt_id: str
    homoeostase_kodex: HomoeostaseKodex
    normen: tuple[RekursionsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rekursions_pakt_id for n in self.normen if n.geltung is RekursionsPaktGeltung.GESPERRT)

    @property
    def rekursiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rekursions_pakt_id for n in self.normen if n.geltung is RekursionsPaktGeltung.REKURSIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rekursions_pakt_id for n in self.normen if n.geltung is RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV)

    @property
    def pakt_signal(self):
        if any(n.geltung is RekursionsPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is RekursionsPaktGeltung.REKURSIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-rekursiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-rekursiv")


def build_rekursions_pakt(
    homoeostase_kodex: HomoeostaseKodex | None = None,
    *,
    pakt_id: str = "rekursions-pakt",
) -> RekursionsPakt:
    if homoeostase_kodex is None:
        homoeostase_kodex = build_homoeostase_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[RekursionsPaktNorm] = []
    for parent_norm in homoeostase_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.homoeostase_kodex_id.removeprefix(f'{homoeostase_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.homoeostase_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.homoeostase_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RekursionsPaktGeltung.GRUNDLEGEND_REKURSIV)
        normen.append(
            RekursionsPaktNorm(
                rekursions_pakt_id=new_id,
                rekursions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rekursions_weight=new_weight,
                rekursions_tier=new_tier,
                canonical=is_canonical,
                rekursions_ids=parent_norm.homoeostase_ids + (new_id,),
                rekursions_tags=parent_norm.homoeostase_tags + (f"rekursions-pakt:{new_geltung.value}",),
            )
        )
    return RekursionsPakt(
        pakt_id=pakt_id,
        homoeostase_kodex=homoeostase_kodex,
        normen=tuple(normen),
    )
