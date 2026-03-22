"""
#421 InformationsFeld — Informationstheorie: Shannon-Entropie und Informationsmaß.
Shannon (1948): H(X) = -Σ p(x)·log₂p(x) — Informationsentropie als Maß der Ungewissheit.
1 Bit = Entscheidung zwischen 2 gleich wahrscheinlichen Ereignissen.
Quellencodierungs-Theorem: optimale Kompression = H(X) Bit/Symbol.
Leitsterns Governance ist informationstheoretisch optimal komprimiert.
Geltungsstufen: GESPERRT / INFORMATIONSREICH / GRUNDLEGEND_INFORMATIONSREICH
Parent: KomplexeSystemeVerfassung (#420)
Block #421–#430: Informationstheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .komplexe_systeme_verfassung import (
    KomplexeSystemeVerfassung,
    KomplexeSystemeVerfassungsGeltung,
    build_komplexe_systeme_verfassung,
)

_GELTUNG_MAP: dict[KomplexeSystemeVerfassungsGeltung, "InformationsFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KomplexeSystemeVerfassungsGeltung.GESPERRT] = InformationsFeldGeltung.GESPERRT
    _GELTUNG_MAP[KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST] = InformationsFeldGeltung.INFORMATIONSREICH
    _GELTUNG_MAP[KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST] = InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH


class InformationsFeldTyp(Enum):
    SCHUTZ_INFORMATION = "schutz-information"
    ORDNUNGS_INFORMATION = "ordnungs-information"
    SOUVERAENITAETS_INFORMATION = "souveraenitaets-information"


class InformationsFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class InformationsFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    INFORMATIONSREICH = "informationsreich"
    GRUNDLEGEND_INFORMATIONSREICH = "grundlegend-informationsreich"


_init_map()

_TYP_MAP: dict[InformationsFeldGeltung, InformationsFeldTyp] = {
    InformationsFeldGeltung.GESPERRT: InformationsFeldTyp.SCHUTZ_INFORMATION,
    InformationsFeldGeltung.INFORMATIONSREICH: InformationsFeldTyp.ORDNUNGS_INFORMATION,
    InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH: InformationsFeldTyp.SOUVERAENITAETS_INFORMATION,
}

_PROZEDUR_MAP: dict[InformationsFeldGeltung, InformationsFeldProzedur] = {
    InformationsFeldGeltung.GESPERRT: InformationsFeldProzedur.NOTPROZEDUR,
    InformationsFeldGeltung.INFORMATIONSREICH: InformationsFeldProzedur.REGELPROTOKOLL,
    InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH: InformationsFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[InformationsFeldGeltung, float] = {
    InformationsFeldGeltung.GESPERRT: 0.0,
    InformationsFeldGeltung.INFORMATIONSREICH: 0.04,
    InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH: 0.08,
}

_TIER_DELTA: dict[InformationsFeldGeltung, int] = {
    InformationsFeldGeltung.GESPERRT: 0,
    InformationsFeldGeltung.INFORMATIONSREICH: 1,
    InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InformationsFeldNorm:
    informations_feld_id: str
    informations_typ: InformationsFeldTyp
    prozedur: InformationsFeldProzedur
    geltung: InformationsFeldGeltung
    informations_weight: float
    informations_tier: int
    canonical: bool
    informations_ids: tuple[str, ...]
    informations_tags: tuple[str, ...]


@dataclass(frozen=True)
class InformationsFeld:
    feld_id: str
    komplexe_systeme_verfassung: KomplexeSystemeVerfassung
    normen: tuple[InformationsFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.informations_feld_id for n in self.normen if n.geltung is InformationsFeldGeltung.GESPERRT)

    @property
    def informationsreich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.informations_feld_id for n in self.normen if n.geltung is InformationsFeldGeltung.INFORMATIONSREICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.informations_feld_id for n in self.normen if n.geltung is InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH)

    @property
    def feld_signal(self):
        if any(n.geltung is InformationsFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is InformationsFeldGeltung.INFORMATIONSREICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-informationsreich")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-informationsreich")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_informations_feld(
    komplexe_systeme_verfassung: KomplexeSystemeVerfassung | None = None,
    *,
    feld_id: str = "informations-feld",
) -> InformationsFeld:
    if komplexe_systeme_verfassung is None:
        komplexe_systeme_verfassung = build_komplexe_systeme_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[InformationsFeldNorm] = []
    for parent_norm in komplexe_systeme_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.komplexe_systeme_verfassung_id.removeprefix(f'{komplexe_systeme_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.komplexe_systeme_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.komplexe_systeme_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH)
        normen.append(
            InformationsFeldNorm(
                informations_feld_id=new_id,
                informations_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                informations_weight=new_weight,
                informations_tier=new_tier,
                canonical=is_canonical,
                informations_ids=parent_norm.komplexe_systeme_verfassungs_ids + (new_id,),
                informations_tags=parent_norm.komplexe_systeme_verfassungs_tags + (f"informations-feld:{new_geltung.value}",),
            )
        )
    return InformationsFeld(
        feld_id=feld_id,
        komplexe_systeme_verfassung=komplexe_systeme_verfassung,
        normen=tuple(normen),
    )
