"""
#419 KuenstlichesLebenCharta — Künstliches Leben: Leben als Prozess.
Langton (1990): Artificial Life — Leben als Prozess, nicht als Substrat.
λ-Parameter: 0=Tod, 1=Chaos, λ_kritisch ≈ Rand des Chaos = maximale Komplexität.
Von Neumann'scher universeller Konstruktor: Selbstreproduktion durch Beschreibung
+ Kopiermaschine. Metabolismus als informationsverarbeitender Prozess.
Tierra (Ray 1991): Digitale Ökosysteme, Parasiten, Evolution in silico.
Avida: experimentelle Evolution digitaler Organismen. Leitsterns Agenten: ALife-Entitäten.
Geltungsstufen: GESPERRT / ALIFE / GRUNDLEGEND_ALIFE
Parent: SynergetikNormSatz (#418, *_norm)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .synergetik_norm import (
    SynergetikNormGeltung,
    SynergetikNormSatz,
    build_synergetik_norm,
)

_GELTUNG_MAP: dict[SynergetikNormGeltung, "KuenstlichesLebenChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SynergetikNormGeltung.GESPERRT] = KuenstlichesLebenChartaGeltung.GESPERRT
    _GELTUNG_MAP[SynergetikNormGeltung.SYNERGETISCH] = KuenstlichesLebenChartaGeltung.ALIFE
    _GELTUNG_MAP[SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH] = KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE


class KuenstlichesLebenChartaTyp(Enum):
    SCHUTZ_KUENSTLICHES_LEBEN = "schutz-kuenstliches-leben"
    ORDNUNGS_KUENSTLICHES_LEBEN = "ordnungs-kuenstliches-leben"
    SOUVERAENITAETS_KUENSTLICHES_LEBEN = "souveraenitaets-kuenstliches-leben"


class KuenstlichesLebenChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KuenstlichesLebenChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    ALIFE = "alife"
    GRUNDLEGEND_ALIFE = "grundlegend-alife"


_init_map()

_TYP_MAP: dict[KuenstlichesLebenChartaGeltung, KuenstlichesLebenChartaTyp] = {
    KuenstlichesLebenChartaGeltung.GESPERRT: KuenstlichesLebenChartaTyp.SCHUTZ_KUENSTLICHES_LEBEN,
    KuenstlichesLebenChartaGeltung.ALIFE: KuenstlichesLebenChartaTyp.ORDNUNGS_KUENSTLICHES_LEBEN,
    KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE: KuenstlichesLebenChartaTyp.SOUVERAENITAETS_KUENSTLICHES_LEBEN,
}

_PROZEDUR_MAP: dict[KuenstlichesLebenChartaGeltung, KuenstlichesLebenChartaProzedur] = {
    KuenstlichesLebenChartaGeltung.GESPERRT: KuenstlichesLebenChartaProzedur.NOTPROZEDUR,
    KuenstlichesLebenChartaGeltung.ALIFE: KuenstlichesLebenChartaProzedur.REGELPROTOKOLL,
    KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE: KuenstlichesLebenChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KuenstlichesLebenChartaGeltung, float] = {
    KuenstlichesLebenChartaGeltung.GESPERRT: 0.0,
    KuenstlichesLebenChartaGeltung.ALIFE: 0.04,
    KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE: 0.08,
}

_TIER_DELTA: dict[KuenstlichesLebenChartaGeltung, int] = {
    KuenstlichesLebenChartaGeltung.GESPERRT: 0,
    KuenstlichesLebenChartaGeltung.ALIFE: 1,
    KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KuenstlichesLebenChartaNorm:
    kuenstliches_leben_charta_id: str
    kuenstliches_leben_typ: KuenstlichesLebenChartaTyp
    prozedur: KuenstlichesLebenChartaProzedur
    geltung: KuenstlichesLebenChartaGeltung
    kuenstliches_leben_weight: float
    kuenstliches_leben_tier: int
    canonical: bool
    kuenstliches_leben_ids: tuple[str, ...]
    kuenstliches_leben_tags: tuple[str, ...]


@dataclass(frozen=True)
class KuenstlichesLebenCharta:
    charta_id: str
    synergetik_norm: SynergetikNormSatz
    normen: tuple[KuenstlichesLebenChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kuenstliches_leben_charta_id for n in self.normen if n.geltung is KuenstlichesLebenChartaGeltung.GESPERRT)

    @property
    def alife_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kuenstliches_leben_charta_id for n in self.normen if n.geltung is KuenstlichesLebenChartaGeltung.ALIFE)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kuenstliches_leben_charta_id for n in self.normen if n.geltung is KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE)

    @property
    def charta_signal(self):
        if any(n.geltung is KuenstlichesLebenChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KuenstlichesLebenChartaGeltung.ALIFE for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-alife")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-alife")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kuenstliches_leben_charta(
    synergetik_norm: SynergetikNormSatz | None = None,
    *,
    charta_id: str = "kuenstliches-leben-charta",
) -> KuenstlichesLebenCharta:
    if synergetik_norm is None:
        synergetik_norm = build_synergetik_norm(norm_id=f"{charta_id}-norm")

    normen: list[KuenstlichesLebenChartaNorm] = []
    for parent_norm in synergetik_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{synergetik_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.synergetik_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.synergetik_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE)
        normen.append(
            KuenstlichesLebenChartaNorm(
                kuenstliches_leben_charta_id=new_id,
                kuenstliches_leben_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kuenstliches_leben_weight=new_weight,
                kuenstliches_leben_tier=new_tier,
                canonical=is_canonical,
                kuenstliches_leben_ids=parent_norm.synergetik_norm_ids + (new_id,),
                kuenstliches_leben_tags=parent_norm.synergetik_norm_tags + (f"kuenstliches-leben:{new_geltung.value}",),
            )
        )
    return KuenstlichesLebenCharta(
        charta_id=charta_id,
        synergetik_norm=synergetik_norm,
        normen=tuple(normen),
    )
