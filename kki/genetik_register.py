"""
#452 GenetikRegister — Genetik: DNA, Chromosomen und der genetische Code.
Watson & Crick (1953): DNA-Doppelhelix-Struktur — Nobel 1962. Basis aller Erbinformation.
Crick (1958): Zentrales Dogma — DNA → RNA → Protein. Informationsfluss der Zelle.
Nirenberg & Khorana (1968): Entschlüsselung des genetischen Codes — 64 Codons. Nobel 1968.
Leitsterns Agenten tragen einen genetischen Kodex: DNA-Struktur für Trait-Vererbung im Schwarm.
Geltungsstufen: GESPERRT / GENETISCH / GRUNDLEGEND_GENETISCH
Parent: EvolutionsFeld (#451)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .evolutions_feld import (
    EvolutionsFeld,
    EvolutionsFeldGeltung,
    build_evolutions_feld,
)

_GELTUNG_MAP: dict[EvolutionsFeldGeltung, "GenetikRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EvolutionsFeldGeltung.GESPERRT] = GenetikRegisterGeltung.GESPERRT
    _GELTUNG_MAP[EvolutionsFeldGeltung.EVOLUTIONAER] = GenetikRegisterGeltung.GENETISCH
    _GELTUNG_MAP[EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER] = GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH


class GenetikRegisterTyp(Enum):
    SCHUTZ_GENETIK = "schutz-genetik"
    ORDNUNGS_GENETIK = "ordnungs-genetik"
    SOUVERAENITAETS_GENETIK = "souveraenitaets-genetik"


class GenetikRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GenetikRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    GENETISCH = "genetisch"
    GRUNDLEGEND_GENETISCH = "grundlegend-genetisch"


_init_map()

_TYP_MAP: dict[GenetikRegisterGeltung, GenetikRegisterTyp] = {
    GenetikRegisterGeltung.GESPERRT: GenetikRegisterTyp.SCHUTZ_GENETIK,
    GenetikRegisterGeltung.GENETISCH: GenetikRegisterTyp.ORDNUNGS_GENETIK,
    GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH: GenetikRegisterTyp.SOUVERAENITAETS_GENETIK,
}

_PROZEDUR_MAP: dict[GenetikRegisterGeltung, GenetikRegisterProzedur] = {
    GenetikRegisterGeltung.GESPERRT: GenetikRegisterProzedur.NOTPROZEDUR,
    GenetikRegisterGeltung.GENETISCH: GenetikRegisterProzedur.REGELPROTOKOLL,
    GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH: GenetikRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GenetikRegisterGeltung, float] = {
    GenetikRegisterGeltung.GESPERRT: 0.0,
    GenetikRegisterGeltung.GENETISCH: 0.04,
    GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH: 0.08,
}

_TIER_DELTA: dict[GenetikRegisterGeltung, int] = {
    GenetikRegisterGeltung.GESPERRT: 0,
    GenetikRegisterGeltung.GENETISCH: 1,
    GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH: 2,
}


@dataclass(frozen=True)
class GenetikRegisterNorm:
    genetik_register_id: str
    genetik_register_typ: GenetikRegisterTyp
    prozedur: GenetikRegisterProzedur
    geltung: GenetikRegisterGeltung
    genetik_weight: float
    genetik_tier: int
    canonical: bool
    genetik_ids: tuple[str, ...]
    genetik_tags: tuple[str, ...]


@dataclass(frozen=True)
class GenetikRegister:
    register_id: str
    evolutions_feld: EvolutionsFeld
    normen: tuple[GenetikRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.genetik_register_id for n in self.normen if n.geltung is GenetikRegisterGeltung.GESPERRT)

    @property
    def genetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.genetik_register_id for n in self.normen if n.geltung is GenetikRegisterGeltung.GENETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.genetik_register_id for n in self.normen if n.geltung is GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH)

    @property
    def register_signal(self):
        if any(n.geltung is GenetikRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is GenetikRegisterGeltung.GENETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-genetisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-genetisch")


def build_genetik_register(
    evolutions_feld: EvolutionsFeld | None = None,
    *,
    register_id: str = "genetik-register",
) -> GenetikRegister:
    if evolutions_feld is None:
        evolutions_feld = build_evolutions_feld(feld_id=f"{register_id}-feld")

    normen: list[GenetikRegisterNorm] = []
    for parent_norm in evolutions_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.evolutions_feld_id.removeprefix(f'{evolutions_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.evolutions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.evolutions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH)
        normen.append(
            GenetikRegisterNorm(
                genetik_register_id=new_id,
                genetik_register_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                genetik_weight=new_weight,
                genetik_tier=new_tier,
                canonical=is_canonical,
                genetik_ids=parent_norm.evolutions_ids + (new_id,),
                genetik_tags=parent_norm.evolutions_tags + (f"genetik-register:{new_geltung.value}",),
            )
        )
    return GenetikRegister(
        register_id=register_id,
        evolutions_feld=evolutions_feld,
        normen=tuple(normen),
    )
