"""
#459 PhylogenetikCharta — Phylogenetik: Stammbäume und molekulare Evolution.
Hennig (1966): Kladistik — gemeinsame abgeleitete Merkmale (Synapomorphien) als Phylogenie-Basis.
Zuckerkandl & Pauling (1965): Molekulare Uhr — Mutationsrate als Zeitmaß der Evolution.
Felsenstein (1981): Maximum-Likelihood-Methode für phylogenetische Bäume.
Leitsterns phylogenetische Charta: Stammbäume der Agenten-Linien sichern Genealogie-Transparenz.
Geltungsstufen: GESPERRT / PHYLOGENETISCH / GRUNDLEGEND_PHYLOGENETISCH
Parent: EvolutionsNorm (#458)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .evolutions_norm import (
    EvolutionsNormSatz,
    EvolutionsNormGeltung,
    build_evolutions_norm,
)

_GELTUNG_MAP: dict[EvolutionsNormGeltung, "PhylogenetikChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EvolutionsNormGeltung.GESPERRT] = PhylogenetikChartaGeltung.GESPERRT
    _GELTUNG_MAP[EvolutionsNormGeltung.ARTBILDEND] = PhylogenetikChartaGeltung.PHYLOGENETISCH
    _GELTUNG_MAP[EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND] = PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH


class PhylogenetikChartaTyp(Enum):
    SCHUTZ_PHYLOGENETIK = "schutz-phylogenetik"
    ORDNUNGS_PHYLOGENETIK = "ordnungs-phylogenetik"
    SOUVERAENITAETS_PHYLOGENETIK = "souveraenitaets-phylogenetik"


class PhylogenetikChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PhylogenetikChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    PHYLOGENETISCH = "phylogenetisch"
    GRUNDLEGEND_PHYLOGENETISCH = "grundlegend-phylogenetisch"


_init_map()

_TYP_MAP: dict[PhylogenetikChartaGeltung, PhylogenetikChartaTyp] = {
    PhylogenetikChartaGeltung.GESPERRT: PhylogenetikChartaTyp.SCHUTZ_PHYLOGENETIK,
    PhylogenetikChartaGeltung.PHYLOGENETISCH: PhylogenetikChartaTyp.ORDNUNGS_PHYLOGENETIK,
    PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH: PhylogenetikChartaTyp.SOUVERAENITAETS_PHYLOGENETIK,
}

_PROZEDUR_MAP: dict[PhylogenetikChartaGeltung, PhylogenetikChartaProzedur] = {
    PhylogenetikChartaGeltung.GESPERRT: PhylogenetikChartaProzedur.NOTPROZEDUR,
    PhylogenetikChartaGeltung.PHYLOGENETISCH: PhylogenetikChartaProzedur.REGELPROTOKOLL,
    PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH: PhylogenetikChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PhylogenetikChartaGeltung, float] = {
    PhylogenetikChartaGeltung.GESPERRT: 0.0,
    PhylogenetikChartaGeltung.PHYLOGENETISCH: 0.04,
    PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH: 0.08,
}

_TIER_DELTA: dict[PhylogenetikChartaGeltung, int] = {
    PhylogenetikChartaGeltung.GESPERRT: 0,
    PhylogenetikChartaGeltung.PHYLOGENETISCH: 1,
    PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH: 2,
}


@dataclass(frozen=True)
class PhylogenetikChartaNorm:
    phylogenetik_charta_id: str
    phylogenetik_charta_typ: PhylogenetikChartaTyp
    prozedur: PhylogenetikChartaProzedur
    geltung: PhylogenetikChartaGeltung
    phylogenetik_weight: float
    phylogenetik_tier: int
    canonical: bool
    phylogenetik_ids: tuple[str, ...]
    phylogenetik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhylogenetikCharta:
    charta_id: str
    evolutions_norm: EvolutionsNormSatz
    normen: tuple[PhylogenetikChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phylogenetik_charta_id for n in self.normen if n.geltung is PhylogenetikChartaGeltung.GESPERRT)

    @property
    def phylogenetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phylogenetik_charta_id for n in self.normen if n.geltung is PhylogenetikChartaGeltung.PHYLOGENETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phylogenetik_charta_id for n in self.normen if n.geltung is PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is PhylogenetikChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is PhylogenetikChartaGeltung.PHYLOGENETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-phylogenetisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-phylogenetisch")


def build_phylogenetik_charta(
    evolutions_norm: EvolutionsNormSatz | None = None,
    *,
    charta_id: str = "phylogenetik-charta",
) -> PhylogenetikCharta:
    if evolutions_norm is None:
        evolutions_norm = build_evolutions_norm(norm_id=f"{charta_id}-norm")

    normen: list[PhylogenetikChartaNorm] = []
    for parent_norm in evolutions_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{evolutions_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.evolutions_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.evolutions_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH)
        normen.append(
            PhylogenetikChartaNorm(
                phylogenetik_charta_id=new_id,
                phylogenetik_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                phylogenetik_weight=new_weight,
                phylogenetik_tier=new_tier,
                canonical=is_canonical,
                phylogenetik_ids=parent_norm.evolutions_norm_ids + (new_id,),
                phylogenetik_tags=parent_norm.evolutions_norm_tags + (f"phylogenetik-charta:{new_geltung.value}",),
            )
        )
    return PhylogenetikCharta(
        charta_id=charta_id,
        evolutions_norm=evolutions_norm,
        normen=tuple(normen),
    )
