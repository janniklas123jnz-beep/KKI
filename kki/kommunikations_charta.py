"""
#469 KommunikationsCharta — Shannon-Weaver und Information in der Sprache.
Shannon & Weaver (1949): A Mathematical Theory of Communication — Kanal, Rauschen, Redundanz;
  angewandt auf natürliche Sprache: Entropie des Lexikons, Redundanz der Grammatik.
Zipf (1935): Human Behavior and the Principle of Least Effort — Zipf-Gesetz der Wortfrequenz.
Kolmogorov (1965): Algorithmic complexity — Beschreibungskomplexität sprachlicher Strukturen.
Leitsterns Kommunikationscharta: Informationsgehalt von Agentennachrichten optimiert nach
Shannon-Effizienz; Rauschen wird durch redundante Codierung im Schwarm-Protokoll gemindert.
Geltungsstufen: GESPERRT / KOMMUNIKATIV / GRUNDLEGEND_KOMMUNIKATIV
Parent: SprachNormSatz (#468)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .sprach_norm import (
    SprachNormSatz,
    SprachNormGeltung,
    build_sprach_norm,
)

_GELTUNG_MAP: dict[SprachNormGeltung, "KommunikationsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SprachNormGeltung.GESPERRT] = KommunikationsChartaGeltung.GESPERRT
    _GELTUNG_MAP[SprachNormGeltung.SPRACHNORMATIV] = KommunikationsChartaGeltung.KOMMUNIKATIV
    _GELTUNG_MAP[SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV] = KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV


class KommunikationsChartaTyp(Enum):
    SCHUTZ_KOMMUNIKATION = "schutz-kommunikation"
    ORDNUNGS_KOMMUNIKATION = "ordnungs-kommunikation"
    SOUVERAENITAETS_KOMMUNIKATION = "souveraenitaets-kommunikation"


class KommunikationsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KommunikationsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMMUNIKATIV = "kommunikativ"
    GRUNDLEGEND_KOMMUNIKATIV = "grundlegend-kommunikativ"


_init_map()

_TYP_MAP: dict[KommunikationsChartaGeltung, KommunikationsChartaTyp] = {
    KommunikationsChartaGeltung.GESPERRT: KommunikationsChartaTyp.SCHUTZ_KOMMUNIKATION,
    KommunikationsChartaGeltung.KOMMUNIKATIV: KommunikationsChartaTyp.ORDNUNGS_KOMMUNIKATION,
    KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV: KommunikationsChartaTyp.SOUVERAENITAETS_KOMMUNIKATION,
}

_PROZEDUR_MAP: dict[KommunikationsChartaGeltung, KommunikationsChartaProzedur] = {
    KommunikationsChartaGeltung.GESPERRT: KommunikationsChartaProzedur.NOTPROZEDUR,
    KommunikationsChartaGeltung.KOMMUNIKATIV: KommunikationsChartaProzedur.REGELPROTOKOLL,
    KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV: KommunikationsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KommunikationsChartaGeltung, float] = {
    KommunikationsChartaGeltung.GESPERRT: 0.0,
    KommunikationsChartaGeltung.KOMMUNIKATIV: 0.04,
    KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV: 0.08,
}

_TIER_DELTA: dict[KommunikationsChartaGeltung, int] = {
    KommunikationsChartaGeltung.GESPERRT: 0,
    KommunikationsChartaGeltung.KOMMUNIKATIV: 1,
    KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV: 2,
}


@dataclass(frozen=True)
class KommunikationsChartaNorm:
    kommunikations_charta_id: str
    kommunikations_charta_typ: KommunikationsChartaTyp
    prozedur: KommunikationsChartaProzedur
    geltung: KommunikationsChartaGeltung
    kommunikations_weight: float
    kommunikations_tier: int
    canonical: bool
    kommunikations_ids: tuple[str, ...]
    kommunikations_tags: tuple[str, ...]


@dataclass(frozen=True)
class KommunikationsCharta:
    charta_id: str
    sprach_norm: SprachNormSatz
    normen: tuple[KommunikationsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikations_charta_id for n in self.normen if n.geltung is KommunikationsChartaGeltung.GESPERRT)

    @property
    def kommunikativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikations_charta_id for n in self.normen if n.geltung is KommunikationsChartaGeltung.KOMMUNIKATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kommunikations_charta_id for n in self.normen if n.geltung is KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV)

    @property
    def charta_signal(self):
        if any(n.geltung is KommunikationsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KommunikationsChartaGeltung.KOMMUNIKATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kommunikativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kommunikativ")


def build_kommunikations_charta(
    sprach_norm: SprachNormSatz | None = None,
    *,
    charta_id: str = "kommunikations-charta",
) -> KommunikationsCharta:
    if sprach_norm is None:
        sprach_norm = build_sprach_norm(norm_id=f"{charta_id}-norm")

    normen: list[KommunikationsChartaNorm] = []
    for parent_norm in sprach_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{sprach_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.sprach_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.sprach_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV)
        normen.append(
            KommunikationsChartaNorm(
                kommunikations_charta_id=new_id,
                kommunikations_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kommunikations_weight=new_weight,
                kommunikations_tier=new_tier,
                canonical=is_canonical,
                kommunikations_ids=parent_norm.sprach_norm_ids + (new_id,),
                kommunikations_tags=parent_norm.sprach_norm_tags + (f"kommunikations-charta:{new_geltung.value}",),
            )
        )
    return KommunikationsCharta(
        charta_id=charta_id,
        sprach_norm=sprach_norm,
        normen=tuple(normen),
    )
