"""
#489 KomplexitaetsAdaptionsCharta — Komplexitätsadaption & emergente Selbstorganisation.
Stuart Kauffman (1993): The Origins of Order — Selbstorganisation an der Grenze von Ordnung
  und Chaos; NK-Landschaften; Fitness-Landschaften für adaptive Systeme.
John Holland (1975): Adaptation in Natural and Artificial Systems — genetische Algorithmen
  als Paradigma für Anpassung in komplexen Systemen; Schema-Theorie.
Per Bak (1987): Self-Organized Criticality — Sandpile-Modell; Systeme organisieren sich
  spontan in kritische Zustände; Avalanchen als emergente Phänomene.
Leitsterns Komplexitätsadaption: Der Schwarm hält sich an der Grenze von Ordnung und Chaos
(KOMPLEXITAETSADAPTIV), stabilisiert Peta-Skala-Operationen durch Criticality-Protokolle
(GRUNDLEGEND_KOMPLEXITAETSADAPTIV) und schützt Kernfunktionen (GESPERRT).
Parent: SystemNormSatz (#488)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .system_norm import (
    SystemNormSatz,
    SystemNormGeltung,
    build_system_norm,
)

_GELTUNG_MAP: dict[SystemNormGeltung, "KomplexitaetsAdaptionsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SystemNormGeltung.GESPERRT] = KomplexitaetsAdaptionsChartaGeltung.GESPERRT
    _GELTUNG_MAP[SystemNormGeltung.SYSTEMNORMATIV] = KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV
    _GELTUNG_MAP[SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV] = KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV


class KomplexitaetsAdaptionsChartaTyp(Enum):
    SCHUTZ_KOMPLEXITAETSADAPTION = "schutz-komplexitaetsadaption"
    ORDNUNGS_KOMPLEXITAETSADAPTION = "ordnungs-komplexitaetsadaption"
    SOUVERAENITAETS_KOMPLEXITAETSADAPTION = "souveraenitaets-komplexitaetsadaption"


class KomplexitaetsAdaptionsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KomplexitaetsAdaptionsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMPLEXITAETSADAPTIV = "komplexitaetsadaptiv"
    GRUNDLEGEND_KOMPLEXITAETSADAPTIV = "grundlegend-komplexitaetsadaptiv"


_init_map()

_TYP_MAP: dict[KomplexitaetsAdaptionsChartaGeltung, KomplexitaetsAdaptionsChartaTyp] = {
    KomplexitaetsAdaptionsChartaGeltung.GESPERRT: KomplexitaetsAdaptionsChartaTyp.SCHUTZ_KOMPLEXITAETSADAPTION,
    KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV: KomplexitaetsAdaptionsChartaTyp.ORDNUNGS_KOMPLEXITAETSADAPTION,
    KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV: KomplexitaetsAdaptionsChartaTyp.SOUVERAENITAETS_KOMPLEXITAETSADAPTION,
}

_PROZEDUR_MAP: dict[KomplexitaetsAdaptionsChartaGeltung, KomplexitaetsAdaptionsChartaProzedur] = {
    KomplexitaetsAdaptionsChartaGeltung.GESPERRT: KomplexitaetsAdaptionsChartaProzedur.NOTPROZEDUR,
    KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV: KomplexitaetsAdaptionsChartaProzedur.REGELPROTOKOLL,
    KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV: KomplexitaetsAdaptionsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KomplexitaetsAdaptionsChartaGeltung, float] = {
    KomplexitaetsAdaptionsChartaGeltung.GESPERRT: 0.0,
    KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV: 0.04,
    KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV: 0.08,
}

_TIER_DELTA: dict[KomplexitaetsAdaptionsChartaGeltung, int] = {
    KomplexitaetsAdaptionsChartaGeltung.GESPERRT: 0,
    KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV: 1,
    KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV: 2,
}


@dataclass(frozen=True)
class KomplexitaetsAdaptionsChartaNorm:
    komplexitaets_adaptions_charta_id: str
    komplexitaets_adaptions_typ: KomplexitaetsAdaptionsChartaTyp
    prozedur: KomplexitaetsAdaptionsChartaProzedur
    geltung: KomplexitaetsAdaptionsChartaGeltung
    komplexitaets_adaptions_weight: float
    komplexitaets_adaptions_tier: int
    canonical: bool
    komplexitaets_adaptions_ids: tuple[str, ...]
    komplexitaets_adaptions_tags: tuple[str, ...]


@dataclass(frozen=True)
class KomplexitaetsAdaptionsCharta:
    charta_id: str
    system_norm: SystemNormSatz
    normen: tuple[KomplexitaetsAdaptionsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_adaptions_charta_id for n in self.normen if n.geltung is KomplexitaetsAdaptionsChartaGeltung.GESPERRT)

    @property
    def komplexitaetsadaptiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_adaptions_charta_id for n in self.normen if n.geltung is KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_adaptions_charta_id for n in self.normen if n.geltung is KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV)

    @property
    def charta_signal(self):
        if any(n.geltung is KomplexitaetsAdaptionsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-komplexitaetsadaptiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-komplexitaetsadaptiv")


def build_komplexitaets_adaptions_charta(
    system_norm: SystemNormSatz | None = None,
    *,
    charta_id: str = "komplexitaets-adaptions-charta",
) -> KomplexitaetsAdaptionsCharta:
    if system_norm is None:
        system_norm = build_system_norm(norm_id=f"{charta_id}-norm")

    normen: list[KomplexitaetsAdaptionsChartaNorm] = []
    for parent_norm in system_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{system_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.system_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.system_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV)
        normen.append(
            KomplexitaetsAdaptionsChartaNorm(
                komplexitaets_adaptions_charta_id=new_id,
                komplexitaets_adaptions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                komplexitaets_adaptions_weight=new_weight,
                komplexitaets_adaptions_tier=new_tier,
                canonical=is_canonical,
                komplexitaets_adaptions_ids=parent_norm.system_norm_ids + (new_id,),
                komplexitaets_adaptions_tags=parent_norm.system_norm_tags + (f"komplexitaets-adaptions-charta:{new_geltung.value}",),
            )
        )
    return KomplexitaetsAdaptionsCharta(
        charta_id=charta_id,
        system_norm=system_norm,
        normen=tuple(normen),
    )
