"""
#454 MutationsKodex — Mutation und genetische Rekombination: Quellen der Variation.
Morgan (1915): Chromosomentheorie der Vererbung — Gene auf Chromosomen, Crossing-Over.
Muller (1927): Röntgenstrahlen erzeugen Mutationen — künstliche Mutagenese. Nobel 1946.
Kimura (1968): Neutrale Theorie der molekularen Evolution — Drift dominiert über Selektion.
Leitsterns Mutations-Kodex: kontrollierte Variation schützt vor Monokultur und Stagnation.
Geltungsstufen: GESPERRT / MUTATIV / GRUNDLEGEND_MUTATIV
Parent: SeletkionsCharta (#453)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .selektions_charta import (
    SeletkionsCharta,
    SeletkionsChartaGeltung,
    build_selektions_charta,
)

_GELTUNG_MAP: dict[SeletkionsChartaGeltung, "MutationsKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SeletkionsChartaGeltung.GESPERRT] = MutationsKodexGeltung.GESPERRT
    _GELTUNG_MAP[SeletkionsChartaGeltung.SELEKTIV] = MutationsKodexGeltung.MUTATIV
    _GELTUNG_MAP[SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV] = MutationsKodexGeltung.GRUNDLEGEND_MUTATIV


class MutationsKodexTyp(Enum):
    SCHUTZ_MUTATION = "schutz-mutation"
    ORDNUNGS_MUTATION = "ordnungs-mutation"
    SOUVERAENITAETS_MUTATION = "souveraenitaets-mutation"


class MutationsKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MutationsKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    MUTATIV = "mutativ"
    GRUNDLEGEND_MUTATIV = "grundlegend-mutativ"


_init_map()

_TYP_MAP: dict[MutationsKodexGeltung, MutationsKodexTyp] = {
    MutationsKodexGeltung.GESPERRT: MutationsKodexTyp.SCHUTZ_MUTATION,
    MutationsKodexGeltung.MUTATIV: MutationsKodexTyp.ORDNUNGS_MUTATION,
    MutationsKodexGeltung.GRUNDLEGEND_MUTATIV: MutationsKodexTyp.SOUVERAENITAETS_MUTATION,
}

_PROZEDUR_MAP: dict[MutationsKodexGeltung, MutationsKodexProzedur] = {
    MutationsKodexGeltung.GESPERRT: MutationsKodexProzedur.NOTPROZEDUR,
    MutationsKodexGeltung.MUTATIV: MutationsKodexProzedur.REGELPROTOKOLL,
    MutationsKodexGeltung.GRUNDLEGEND_MUTATIV: MutationsKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MutationsKodexGeltung, float] = {
    MutationsKodexGeltung.GESPERRT: 0.0,
    MutationsKodexGeltung.MUTATIV: 0.04,
    MutationsKodexGeltung.GRUNDLEGEND_MUTATIV: 0.08,
}

_TIER_DELTA: dict[MutationsKodexGeltung, int] = {
    MutationsKodexGeltung.GESPERRT: 0,
    MutationsKodexGeltung.MUTATIV: 1,
    MutationsKodexGeltung.GRUNDLEGEND_MUTATIV: 2,
}


@dataclass(frozen=True)
class MutationsKodexNorm:
    mutations_kodex_id: str
    mutations_kodex_typ: MutationsKodexTyp
    prozedur: MutationsKodexProzedur
    geltung: MutationsKodexGeltung
    mutations_weight: float
    mutations_tier: int
    canonical: bool
    mutations_ids: tuple[str, ...]
    mutations_tags: tuple[str, ...]


@dataclass(frozen=True)
class MutationsKodex:
    kodex_id: str
    selektions_charta: SeletkionsCharta
    normen: tuple[MutationsKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mutations_kodex_id for n in self.normen if n.geltung is MutationsKodexGeltung.GESPERRT)

    @property
    def mutativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mutations_kodex_id for n in self.normen if n.geltung is MutationsKodexGeltung.MUTATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mutations_kodex_id for n in self.normen if n.geltung is MutationsKodexGeltung.GRUNDLEGEND_MUTATIV)

    @property
    def kodex_signal(self):
        if any(n.geltung is MutationsKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is MutationsKodexGeltung.MUTATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-mutativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-mutativ")


def build_mutations_kodex(
    selektions_charta: SeletkionsCharta | None = None,
    *,
    kodex_id: str = "mutations-kodex",
) -> MutationsKodex:
    if selektions_charta is None:
        selektions_charta = build_selektions_charta(charta_id=f"{kodex_id}-charta")

    normen: list[MutationsKodexNorm] = []
    for parent_norm in selektions_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.selektions_charta_id.removeprefix(f'{selektions_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.selektions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.selektions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MutationsKodexGeltung.GRUNDLEGEND_MUTATIV)
        normen.append(
            MutationsKodexNorm(
                mutations_kodex_id=new_id,
                mutations_kodex_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                mutations_weight=new_weight,
                mutations_tier=new_tier,
                canonical=is_canonical,
                mutations_ids=parent_norm.selektions_ids + (new_id,),
                mutations_tags=parent_norm.selektions_tags + (f"mutations-kodex:{new_geltung.value}",),
            )
        )
    return MutationsKodex(
        kodex_id=kodex_id,
        selektions_charta=selektions_charta,
        normen=tuple(normen),
    )
