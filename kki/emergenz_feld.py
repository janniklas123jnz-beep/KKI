"""
#411 EmergenzFeld — Emergenz: Mehr ist anders.
Anderson (1972): 'More is Different' — quantitative Komplexität erzeugt qualitativ
neue Eigenschaften. Emergenz ist nicht reduzierbar auf Bestandteile.
Holland (1995): Emergenz in komplexen adaptiven Systemen. Downward Causation:
emergente Ebene beeinflusst Bestandteile. Leitsterns Schwarm-Intelligenz.
Starke Emergenz (Chalmers): fundamental neue Eigenschaften.
Schwache Emergenz (Bedau): rechnerisch irreduzibel. Leitstern: emergenter Terra-Schwarm.
Geltungsstufen: GESPERRT / EMERGENT / GRUNDLEGEND_EMERGENT
Parent: MathematikVerfassung (#410)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mathematik_verfassung import (
    MathematikVerfassung,
    MathematikVerfassungsGeltung,
    build_mathematik_verfassung,
)

_GELTUNG_MAP: dict[MathematikVerfassungsGeltung, "EmergenzFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MathematikVerfassungsGeltung.GESPERRT] = EmergenzFeldGeltung.GESPERRT
    _GELTUNG_MAP[MathematikVerfassungsGeltung.MATHEMATIKVERFASST] = EmergenzFeldGeltung.EMERGENT
    _GELTUNG_MAP[MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST] = EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT


class EmergenzFeldTyp(Enum):
    SCHUTZ_EMERGENZ = "schutz-emergenz"
    ORDNUNGS_EMERGENZ = "ordnungs-emergenz"
    SOUVERAENITAETS_EMERGENZ = "souveraenitaets-emergenz"


class EmergenzFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EmergenzFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    EMERGENT = "emergent"
    GRUNDLEGEND_EMERGENT = "grundlegend-emergent"


_init_map()

_TYP_MAP: dict[EmergenzFeldGeltung, EmergenzFeldTyp] = {
    EmergenzFeldGeltung.GESPERRT: EmergenzFeldTyp.SCHUTZ_EMERGENZ,
    EmergenzFeldGeltung.EMERGENT: EmergenzFeldTyp.ORDNUNGS_EMERGENZ,
    EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT: EmergenzFeldTyp.SOUVERAENITAETS_EMERGENZ,
}

_PROZEDUR_MAP: dict[EmergenzFeldGeltung, EmergenzFeldProzedur] = {
    EmergenzFeldGeltung.GESPERRT: EmergenzFeldProzedur.NOTPROZEDUR,
    EmergenzFeldGeltung.EMERGENT: EmergenzFeldProzedur.REGELPROTOKOLL,
    EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT: EmergenzFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EmergenzFeldGeltung, float] = {
    EmergenzFeldGeltung.GESPERRT: 0.0,
    EmergenzFeldGeltung.EMERGENT: 0.04,
    EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT: 0.08,
}

_TIER_DELTA: dict[EmergenzFeldGeltung, int] = {
    EmergenzFeldGeltung.GESPERRT: 0,
    EmergenzFeldGeltung.EMERGENT: 1,
    EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmergenzFeldNorm:
    emergenz_feld_id: str
    emergenz_typ: EmergenzFeldTyp
    prozedur: EmergenzFeldProzedur
    geltung: EmergenzFeldGeltung
    emergenz_weight: float
    emergenz_tier: int
    canonical: bool
    emergenz_ids: tuple[str, ...]
    emergenz_tags: tuple[str, ...]


@dataclass(frozen=True)
class EmergenzFeld:
    feld_id: str
    mathematik_verfassung: MathematikVerfassung
    normen: tuple[EmergenzFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emergenz_feld_id for n in self.normen if n.geltung is EmergenzFeldGeltung.GESPERRT)

    @property
    def emergent_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emergenz_feld_id for n in self.normen if n.geltung is EmergenzFeldGeltung.EMERGENT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emergenz_feld_id for n in self.normen if n.geltung is EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT)

    @property
    def feld_signal(self):
        if any(n.geltung is EmergenzFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is EmergenzFeldGeltung.EMERGENT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-emergent")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-emergent")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_emergenz_feld(
    mathematik_verfassung: MathematikVerfassung | None = None,
    *,
    feld_id: str = "emergenz-feld",
) -> EmergenzFeld:
    if mathematik_verfassung is None:
        mathematik_verfassung = build_mathematik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[EmergenzFeldNorm] = []
    for parent_norm in mathematik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.mathematik_verfassung_id.removeprefix(f'{mathematik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.mathematik_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.mathematik_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EmergenzFeldGeltung.GRUNDLEGEND_EMERGENT)
        normen.append(
            EmergenzFeldNorm(
                emergenz_feld_id=new_id,
                emergenz_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                emergenz_weight=new_weight,
                emergenz_tier=new_tier,
                canonical=is_canonical,
                emergenz_ids=parent_norm.mathematik_verfassungs_ids + (new_id,),
                emergenz_tags=parent_norm.mathematik_verfassungs_tags + (f"emergenz:{new_geltung.value}",),
            )
        )
    return EmergenzFeld(
        feld_id=feld_id,
        mathematik_verfassung=mathematik_verfassung,
        normen=tuple(normen),
    )
