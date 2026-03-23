"""
#527 WohlfahrtsSenat — Sen/Arrow/Pigou Capability Approach und Wohlfahrtsstaat

Amartya Sen (1999): Development as Freedom — Capability Approach und Entwicklungsfreiheit;
  Wohlfahrt als Verwirklichungschancen, nicht nur Ressourcenausstattung; Freiheit als
  Zweck und Mittel der Entwicklung im Peta-Schwarm Leitstern.
Kenneth Arrow (1951): Social Choice and Individual Values — Unmöglichkeitstheorem der
  sozialen Wohlfahrtsfunktion; Pareto-Effizienz und Gerechtigkeit; kollektive
  Entscheidungstheorie als Grundlage demokratischer Schwarmgovernance.
Arthur Cecil Pigou (1920): The Economics of Welfare — externe Effekte und Marktversagen;
  Pigou-Steuer als Internalisierungsinstrument negativer Externalitäten; staatliche
  Wohlfahrtspolitik zur Korrektur von Marktmängeln im Schwarm.
John Rawls (1971): A Theory of Justice — Schleier des Nichtwissens; Differenzprinzip
  zur Maximierung der Lage der Schwächsten; Grundgüter als Basis gerechter Verteilung
  im Peta-Schwarm Leitstern. ⚖️
Module #527, Parent: InnovationsPakt (#526)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .innovations_pakt import (
    InnovationsPakt,
    InnovationsPaktGeltung,
    build_innovations_pakt,
)

_WEIGHT_DELTA: dict["WohlfahrtsSenatGeltung", float] = {}
_TIER_DELTA: dict["WohlfahrtsSenatGeltung", int] = {}
_TYP_MAP: dict["WohlfahrtsSenatGeltung", "WohlfahrtsSenatTyp"] = {}
_PROZEDUR_MAP: dict["WohlfahrtsSenatGeltung", "WohlfahrtsSenatProzedur"] = {}
_GELTUNG_MAP: dict[InnovationsPaktGeltung, "WohlfahrtsSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WohlfahrtsSenatGeltung.GESPERRT: 0.0,
        WohlfahrtsSenatGeltung.WOHLFAHRTLICH: 0.05,
        WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH: 0.1,
    })
    _TIER_DELTA.update({
        WohlfahrtsSenatGeltung.GESPERRT: 0,
        WohlfahrtsSenatGeltung.WOHLFAHRTLICH: 1,
        WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH: 2,
    })
    _TYP_MAP.update({
        WohlfahrtsSenatGeltung.GESPERRT: WohlfahrtsSenatTyp.SCHUTZ_WOHLFAHRT,
        WohlfahrtsSenatGeltung.WOHLFAHRTLICH: WohlfahrtsSenatTyp.ORDNUNGS_WOHLFAHRT,
        WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH: WohlfahrtsSenatTyp.SOUVERAENITAETS_WOHLFAHRT,
    })
    _PROZEDUR_MAP.update({
        WohlfahrtsSenatGeltung.GESPERRT: WohlfahrtsSenatProzedur.NOTPROZEDUR,
        WohlfahrtsSenatGeltung.WOHLFAHRTLICH: WohlfahrtsSenatProzedur.REGELPROTOKOLL,
        WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH: WohlfahrtsSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        InnovationsPaktGeltung.GESPERRT: WohlfahrtsSenatGeltung.GESPERRT,
        InnovationsPaktGeltung.INNOVATIV: WohlfahrtsSenatGeltung.WOHLFAHRTLICH,
        InnovationsPaktGeltung.GRUNDLEGEND_INNOVATIV: WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH,
    })


class WohlfahrtsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    WOHLFAHRTLICH = "wohlfahrtlich"
    GRUNDLEGEND_WOHLFAHRTLICH = "grundlegend-wohlfahrtlich"


class WohlfahrtsSenatTyp(Enum):
    SCHUTZ_WOHLFAHRT = "schutz-wohlfahrt"
    ORDNUNGS_WOHLFAHRT = "ordnungs-wohlfahrt"
    SOUVERAENITAETS_WOHLFAHRT = "souveraenitaets-wohlfahrt"


class WohlfahrtsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class WohlfahrtsSenatNorm:
    wohlfahrts_senat_id: str
    wohlfahrts_typ: WohlfahrtsSenatTyp
    prozedur: WohlfahrtsSenatProzedur
    geltung: WohlfahrtsSenatGeltung
    wohlfahrts_weight: float
    wohlfahrts_tier: int
    canonical: bool
    wohlfahrts_ids: tuple[str, ...]
    wohlfahrts_tags: tuple[str, ...]


@dataclass(frozen=True)
class WohlfahrtsSenat:
    senat_id: str
    innovations_pakt: InnovationsPakt
    normen: tuple[WohlfahrtsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wohlfahrts_senat_id for n in self.normen if n.geltung is WohlfahrtsSenatGeltung.GESPERRT)

    @property
    def wohlfahrtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wohlfahrts_senat_id for n in self.normen if n.geltung is WohlfahrtsSenatGeltung.WOHLFAHRTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wohlfahrts_senat_id for n in self.normen if n.geltung is WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH)

    @property
    def senat_signal(self):
        if any(n.geltung is WohlfahrtsSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is WohlfahrtsSenatGeltung.WOHLFAHRTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-wohlfahrtlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-wohlfahrtlich")


_init_map()


def build_wohlfahrts_senat(
    innovations_pakt: InnovationsPakt | None = None,
    *,
    senat_id: str = "wohlfahrts-senat",
) -> WohlfahrtsSenat:
    if innovations_pakt is None:
        innovations_pakt = build_innovations_pakt(
            pakt_id=f"{senat_id}-innovations-pakt"
        )

    normen: list[WohlfahrtsSenatNorm] = []
    for parent_norm in innovations_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.innovations_pakt_id.removeprefix(f'{innovations_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.innovations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.innovations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH)
        normen.append(
            WohlfahrtsSenatNorm(
                wohlfahrts_senat_id=new_id,
                wohlfahrts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                wohlfahrts_weight=new_weight,
                wohlfahrts_tier=new_tier,
                canonical=is_canonical,
                wohlfahrts_ids=parent_norm.innovations_ids + (new_id,),
                wohlfahrts_tags=parent_norm.innovations_tags + (f"wohlfahrts-senat:{new_geltung.value}",),
            )
        )
    return WohlfahrtsSenat(
        senat_id=senat_id,
        innovations_pakt=innovations_pakt,
        normen=tuple(normen),
    )
