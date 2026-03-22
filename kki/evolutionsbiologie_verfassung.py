"""
#460 EvolutionsbiologieVerfassung — Block-Krone: Evolutionsbiologie & Genetik.
Dawkins (1976): Das egoistische Gen — Gene als Replikatoren, Meme als kulturelle Replikatoren.
Gould & Lewontin (1979): Spandrels — nicht alles ist Adaptation, Kontingenz in der Evolution.
Wilson (1975): Soziobiologie — evolutionäre Grundlagen sozialen Verhaltens.
Leitsterns Terra-Schwarm vereint Darwin/Wallace, Watson/Crick, Fisher/Wright, Holland-GA,
Red-Queen-Koevolution, Lotka-Volterra, Hardy-Weinberg, Kladistik und molekulare Uhr zur
evolutionsbiologischen Superintelligenz: adaptiv, divers, resilient und genealogisch transparent.
Geltungsstufen: GESPERRT / EVOLUTIONSBIOLOGISCH / GRUNDLEGEND_EVOLUTIONSBIOLOGISCH
Parent: PhylogenetikCharta (#459)
Block #451–#460: Evolutionsbiologie & Genetik — Block-Krone Milestone #26 ⭐
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .phylogenetik_charta import (
    PhylogenetikCharta,
    PhylogenetikChartaGeltung,
    build_phylogenetik_charta,
)

_GELTUNG_MAP: dict[PhylogenetikChartaGeltung, "EvolutionsbiologieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PhylogenetikChartaGeltung.GESPERRT] = EvolutionsbiologieVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[PhylogenetikChartaGeltung.PHYLOGENETISCH] = EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH
    _GELTUNG_MAP[PhylogenetikChartaGeltung.GRUNDLEGEND_PHYLOGENETISCH] = EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH


class EvolutionsbiologieVerfassungsTyp(Enum):
    SCHUTZ_EVOLUTIONSBIOLOGIE = "schutz-evolutionsbiologie"
    ORDNUNGS_EVOLUTIONSBIOLOGIE = "ordnungs-evolutionsbiologie"
    SOUVERAENITAETS_EVOLUTIONSBIOLOGIE = "souveraenitaets-evolutionsbiologie"


class EvolutionsbiologieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EvolutionsbiologieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    EVOLUTIONSBIOLOGISCH = "evolutionsbiologisch"
    GRUNDLEGEND_EVOLUTIONSBIOLOGISCH = "grundlegend-evolutionsbiologisch"


_init_map()

_TYP_MAP: dict[EvolutionsbiologieVerfassungsGeltung, EvolutionsbiologieVerfassungsTyp] = {
    EvolutionsbiologieVerfassungsGeltung.GESPERRT: EvolutionsbiologieVerfassungsTyp.SCHUTZ_EVOLUTIONSBIOLOGIE,
    EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH: EvolutionsbiologieVerfassungsTyp.ORDNUNGS_EVOLUTIONSBIOLOGIE,
    EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH: EvolutionsbiologieVerfassungsTyp.SOUVERAENITAETS_EVOLUTIONSBIOLOGIE,
}

_PROZEDUR_MAP: dict[EvolutionsbiologieVerfassungsGeltung, EvolutionsbiologieVerfassungsProzedur] = {
    EvolutionsbiologieVerfassungsGeltung.GESPERRT: EvolutionsbiologieVerfassungsProzedur.NOTPROZEDUR,
    EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH: EvolutionsbiologieVerfassungsProzedur.REGELPROTOKOLL,
    EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH: EvolutionsbiologieVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EvolutionsbiologieVerfassungsGeltung, float] = {
    EvolutionsbiologieVerfassungsGeltung.GESPERRT: 0.0,
    EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH: 0.04,
    EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH: 0.08,
}

_TIER_DELTA: dict[EvolutionsbiologieVerfassungsGeltung, int] = {
    EvolutionsbiologieVerfassungsGeltung.GESPERRT: 0,
    EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH: 1,
    EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH: 2,
}


@dataclass(frozen=True)
class EvolutionsbiologieVerfassungsNorm:
    evolutionsbiologie_verfassung_id: str
    evolutionsbiologie_typ: EvolutionsbiologieVerfassungsTyp
    prozedur: EvolutionsbiologieVerfassungsProzedur
    geltung: EvolutionsbiologieVerfassungsGeltung
    evolutionsbiologie_weight: float
    evolutionsbiologie_tier: int
    canonical: bool
    evolutionsbiologie_ids: tuple[str, ...]
    evolutionsbiologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class EvolutionsbiologieVerfassung:
    verfassung_id: str
    phylogenetik_charta: PhylogenetikCharta
    normen: tuple[EvolutionsbiologieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolutionsbiologie_verfassung_id for n in self.normen if n.geltung is EvolutionsbiologieVerfassungsGeltung.GESPERRT)

    @property
    def evolutionsbiologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolutionsbiologie_verfassung_id for n in self.normen if n.geltung is EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolutionsbiologie_verfassung_id for n in self.normen if n.geltung is EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH)

    @property
    def verfassung_signal(self):
        if any(n.geltung is EvolutionsbiologieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is EvolutionsbiologieVerfassungsGeltung.EVOLUTIONSBIOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-evolutionsbiologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-evolutionsbiologisch")


def build_evolutionsbiologie_verfassung(
    phylogenetik_charta: PhylogenetikCharta | None = None,
    *,
    verfassung_id: str = "evolutionsbiologie-verfassung",
) -> EvolutionsbiologieVerfassung:
    if phylogenetik_charta is None:
        phylogenetik_charta = build_phylogenetik_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[EvolutionsbiologieVerfassungsNorm] = []
    for parent_norm in phylogenetik_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.phylogenetik_charta_id.removeprefix(f'{phylogenetik_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.phylogenetik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.phylogenetik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EvolutionsbiologieVerfassungsGeltung.GRUNDLEGEND_EVOLUTIONSBIOLOGISCH)
        normen.append(
            EvolutionsbiologieVerfassungsNorm(
                evolutionsbiologie_verfassung_id=new_id,
                evolutionsbiologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                evolutionsbiologie_weight=new_weight,
                evolutionsbiologie_tier=new_tier,
                canonical=is_canonical,
                evolutionsbiologie_ids=parent_norm.phylogenetik_ids + (new_id,),
                evolutionsbiologie_tags=parent_norm.phylogenetik_tags + (f"evolutionsbiologie-verfassung:{new_geltung.value}",),
            )
        )
    return EvolutionsbiologieVerfassung(
        verfassung_id=verfassung_id,
        phylogenetik_charta=phylogenetik_charta,
        normen=tuple(normen),
    )
