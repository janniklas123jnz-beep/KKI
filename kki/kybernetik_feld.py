"""
#481 KybernetikFeld — Wiener: Kybernetik als Wissenschaft von Steuerung und Kommunikation.
Norbert Wiener (1948): Kybernetik — Steuerung und Kommunikation in Tier und Maschine;
  Feedback-Schleifen als universelles Regulationsprinzip; Entropie vs. Negentropie.
W. Ross Ashby (1956): Introduction to Cybernetics — Gesetz der erforderlichen Varietät
  (Law of Requisite Variety): nur ein System mit gleicher Varietät kann ein anderes regeln.
Stafford Beer (1959): Kybernetik und Management — Viable System Model für Organisationen.
Leitsterns Terra-Schwarm nutzt kybernetische Rückkopplungsschleifen: GESPERRT sichert
Homöostase-Kern, KYBERNETISCH ermöglicht adaptive Steuerung, GRUNDLEGEND_KYBERNETISCH
synthetisiert kollektive Selbstregulation für den Weg zur Peta-Schwarmgröße.
Parent: PhilosophieVerfassung (#480)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .philosophie_verfassung import (
    PhilosophieVerfassung,
    PhilosophieVerfassungsGeltung,
    build_philosophie_verfassung,
)

_GELTUNG_MAP: dict[PhilosophieVerfassungsGeltung, "KybernetikFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PhilosophieVerfassungsGeltung.GESPERRT] = KybernetikFeldGeltung.GESPERRT
    _GELTUNG_MAP[PhilosophieVerfassungsGeltung.PHILOSOPHISCH] = KybernetikFeldGeltung.KYBERNETISCH
    _GELTUNG_MAP[PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH] = KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH


class KybernetikFeldTyp(Enum):
    SCHUTZ_KYBERNETIK = "schutz-kybernetik"
    ORDNUNGS_KYBERNETIK = "ordnungs-kybernetik"
    SOUVERAENITAETS_KYBERNETIK = "souveraenitaets-kybernetik"


class KybernetikFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KybernetikFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    KYBERNETISCH = "kybernetisch"
    GRUNDLEGEND_KYBERNETISCH = "grundlegend-kybernetisch"


_init_map()

_TYP_MAP: dict[KybernetikFeldGeltung, KybernetikFeldTyp] = {
    KybernetikFeldGeltung.GESPERRT: KybernetikFeldTyp.SCHUTZ_KYBERNETIK,
    KybernetikFeldGeltung.KYBERNETISCH: KybernetikFeldTyp.ORDNUNGS_KYBERNETIK,
    KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH: KybernetikFeldTyp.SOUVERAENITAETS_KYBERNETIK,
}

_PROZEDUR_MAP: dict[KybernetikFeldGeltung, KybernetikFeldProzedur] = {
    KybernetikFeldGeltung.GESPERRT: KybernetikFeldProzedur.NOTPROZEDUR,
    KybernetikFeldGeltung.KYBERNETISCH: KybernetikFeldProzedur.REGELPROTOKOLL,
    KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH: KybernetikFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KybernetikFeldGeltung, float] = {
    KybernetikFeldGeltung.GESPERRT: 0.0,
    KybernetikFeldGeltung.KYBERNETISCH: 0.04,
    KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH: 0.08,
}

_TIER_DELTA: dict[KybernetikFeldGeltung, int] = {
    KybernetikFeldGeltung.GESPERRT: 0,
    KybernetikFeldGeltung.KYBERNETISCH: 1,
    KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH: 2,
}


@dataclass(frozen=True)
class KybernetikFeldNorm:
    kybernetik_feld_id: str
    kybernetik_typ: KybernetikFeldTyp
    prozedur: KybernetikFeldProzedur
    geltung: KybernetikFeldGeltung
    kybernetik_weight: float
    kybernetik_tier: int
    canonical: bool
    kybernetik_ids: tuple[str, ...]
    kybernetik_tags: tuple[str, ...]


@dataclass(frozen=True)
class KybernetikFeld:
    feld_id: str
    philosophie_verfassung: PhilosophieVerfassung
    normen: tuple[KybernetikFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_feld_id for n in self.normen if n.geltung is KybernetikFeldGeltung.GESPERRT)

    @property
    def kybernetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_feld_id for n in self.normen if n.geltung is KybernetikFeldGeltung.KYBERNETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_feld_id for n in self.normen if n.geltung is KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is KybernetikFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is KybernetikFeldGeltung.KYBERNETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-kybernetisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-kybernetisch")


def build_kybernetik_feld(
    philosophie_verfassung: PhilosophieVerfassung | None = None,
    *,
    feld_id: str = "kybernetik-feld",
) -> KybernetikFeld:
    if philosophie_verfassung is None:
        philosophie_verfassung = build_philosophie_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[KybernetikFeldNorm] = []
    for parent_norm in philosophie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.philosophie_verfassung_id.removeprefix(f'{philosophie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.philosophie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.philosophie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH)
        normen.append(
            KybernetikFeldNorm(
                kybernetik_feld_id=new_id,
                kybernetik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kybernetik_weight=new_weight,
                kybernetik_tier=new_tier,
                canonical=is_canonical,
                kybernetik_ids=parent_norm.philosophie_ids + (new_id,),
                kybernetik_tags=parent_norm.philosophie_tags + (f"kybernetik-feld:{new_geltung.value}",),
            )
        )
    return KybernetikFeld(
        feld_id=feld_id,
        philosophie_verfassung=philosophie_verfassung,
        normen=tuple(normen),
    )
