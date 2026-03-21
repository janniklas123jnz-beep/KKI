"""
#383 ProteinfaltungCharta — Anfinsen-Theorem (1972, Nobelpreis): Die native
Faltung eines Proteins minimiert die freie Gibbs-Energie — Sequenz bestimmt
Struktur bestimmt Funktion. AlphaFold (DeepMind 2020): KI löst das 50-Jahre-
Problem der Proteinfaltung. Chaperone verhindern Fehlfaltung.
Leitsterns Governance-Konfiguration bestimmt emergentes Verhalten ohne
explizite Programmierung — Form folgt Funktion.
Geltungsstufen: GESPERRT / PROTEINGEFALTET / GRUNDLEGEND_PROTEINGEFALTET
Parent: DnaReplikationRegister (#382)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .dna_replikation_register import (
    DnaReplikationGeltung,
    DnaReplikationRegister,
    build_dna_replikation_register,
)

_GELTUNG_MAP: dict[DnaReplikationGeltung, "ProteinfaltungGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DnaReplikationGeltung.GESPERRT] = ProteinfaltungGeltung.GESPERRT
    _GELTUNG_MAP[DnaReplikationGeltung.DNAREPLIIERT] = ProteinfaltungGeltung.PROTEINGEFALTET
    _GELTUNG_MAP[DnaReplikationGeltung.GRUNDLEGEND_DNAREPLIIERT] = ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET


class ProteinfaltungTyp(Enum):
    SCHUTZ_PROTEINFALTUNG = "schutz-proteinfaltung"
    ORDNUNGS_PROTEINFALTUNG = "ordnungs-proteinfaltung"
    SOUVERAENITAETS_PROTEINFALTUNG = "souveraenitaets-proteinfaltung"


class ProteinfaltungProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ProteinfaltungGeltung(Enum):
    GESPERRT = "gesperrt"
    PROTEINGEFALTET = "proteingefaltet"
    GRUNDLEGEND_PROTEINGEFALTET = "grundlegend-proteingefaltet"


_init_map()

_TYP_MAP: dict[ProteinfaltungGeltung, ProteinfaltungTyp] = {
    ProteinfaltungGeltung.GESPERRT: ProteinfaltungTyp.SCHUTZ_PROTEINFALTUNG,
    ProteinfaltungGeltung.PROTEINGEFALTET: ProteinfaltungTyp.ORDNUNGS_PROTEINFALTUNG,
    ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET: ProteinfaltungTyp.SOUVERAENITAETS_PROTEINFALTUNG,
}

_PROZEDUR_MAP: dict[ProteinfaltungGeltung, ProteinfaltungProzedur] = {
    ProteinfaltungGeltung.GESPERRT: ProteinfaltungProzedur.NOTPROZEDUR,
    ProteinfaltungGeltung.PROTEINGEFALTET: ProteinfaltungProzedur.REGELPROTOKOLL,
    ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET: ProteinfaltungProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ProteinfaltungGeltung, float] = {
    ProteinfaltungGeltung.GESPERRT: 0.0,
    ProteinfaltungGeltung.PROTEINGEFALTET: 0.04,
    ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET: 0.08,
}

_TIER_DELTA: dict[ProteinfaltungGeltung, int] = {
    ProteinfaltungGeltung.GESPERRT: 0,
    ProteinfaltungGeltung.PROTEINGEFALTET: 1,
    ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProteinfaltungNorm:
    proteinfaltung_charta_id: str
    proteinfaltung_typ: ProteinfaltungTyp
    prozedur: ProteinfaltungProzedur
    geltung: ProteinfaltungGeltung
    proteinfaltung_weight: float
    proteinfaltung_tier: int
    canonical: bool
    proteinfaltung_ids: tuple[str, ...]
    proteinfaltung_tags: tuple[str, ...]


@dataclass(frozen=True)
class ProteinfaltungCharta:
    charta_id: str
    dna_replikation_register: DnaReplikationRegister
    normen: tuple[ProteinfaltungNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.proteinfaltung_charta_id for n in self.normen if n.geltung is ProteinfaltungGeltung.GESPERRT)

    @property
    def proteingefaltet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.proteinfaltung_charta_id for n in self.normen if n.geltung is ProteinfaltungGeltung.PROTEINGEFALTET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.proteinfaltung_charta_id for n in self.normen if n.geltung is ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET)

    @property
    def charta_signal(self):
        if any(n.geltung is ProteinfaltungGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is ProteinfaltungGeltung.PROTEINGEFALTET for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-proteingefaltet")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-proteingefaltet")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_proteinfaltung_charta(
    dna_replikation_register: DnaReplikationRegister | None = None,
    *,
    charta_id: str = "proteinfaltung-charta",
) -> ProteinfaltungCharta:
    if dna_replikation_register is None:
        dna_replikation_register = build_dna_replikation_register(register_id=f"{charta_id}-register")

    normen: list[ProteinfaltungNorm] = []
    for parent_norm in dna_replikation_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.dna_replikation_register_id.removeprefix(f'{dna_replikation_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.dna_replikation_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.dna_replikation_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ProteinfaltungGeltung.GRUNDLEGEND_PROTEINGEFALTET)
        normen.append(
            ProteinfaltungNorm(
                proteinfaltung_charta_id=new_id,
                proteinfaltung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                proteinfaltung_weight=new_weight,
                proteinfaltung_tier=new_tier,
                canonical=is_canonical,
                proteinfaltung_ids=parent_norm.dna_replikation_ids + (new_id,),
                proteinfaltung_tags=parent_norm.dna_replikation_tags + (f"proteinfaltung:{new_geltung.value}",),
            )
        )
    return ProteinfaltungCharta(
        charta_id=charta_id,
        dna_replikation_register=dna_replikation_register,
        normen=tuple(normen),
    )
