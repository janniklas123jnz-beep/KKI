"""
#402 MengenRegister — Mengenlehre: Cantor (1874) begründet die Mengenlehre.
Diagonalargument beweist Überabzählbarkeit reeller Zahlen. ZFC-Axiome
(Zermelo-Fraenkel + Auswahlaxiom): 9 Axiome als vollständiges Mengensystem.
Russellsche Antinomie (1901) durch ZFC ausgeschlossen. Kontinuumshypothese
(Cantor 1878): unentscheidbar in ZFC (Cohen 1963). Ordinal- und Kardinalzahlen
als Hierarchieskala. Leitsterns Agenten sind mengentheoretisch fundiert:
ihre Zustandsräume sind wohlgeordnete Mengen mit definierter Mächtigkeit.
Geltungsstufen: GESPERRT / MENGENTHEORETISCH / GRUNDLEGEND_MENGENTHEORETISCH
Parent: MathematikFeld (#401)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mathematik_feld import (
    MathematikFeld,
    MathematikFeldGeltung,
    build_mathematik_feld,
)

_GELTUNG_MAP: dict[MathematikFeldGeltung, "MengenRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MathematikFeldGeltung.GESPERRT] = MengenRegisterGeltung.GESPERRT
    _GELTUNG_MAP[MathematikFeldGeltung.MATHEMATISCH] = MengenRegisterGeltung.MENGENTHEORETISCH
    _GELTUNG_MAP[MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH] = MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH


class MengenRegisterTyp(Enum):
    SCHUTZ_MENGEN = "schutz-mengen"
    ORDNUNGS_MENGEN = "ordnungs-mengen"
    SOUVERAENITAETS_MENGEN = "souveraenitaets-mengen"


class MengenRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MengenRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    MENGENTHEORETISCH = "mengentheoretisch"
    GRUNDLEGEND_MENGENTHEORETISCH = "grundlegend-mengentheoretisch"


_init_map()

_TYP_MAP: dict[MengenRegisterGeltung, MengenRegisterTyp] = {
    MengenRegisterGeltung.GESPERRT: MengenRegisterTyp.SCHUTZ_MENGEN,
    MengenRegisterGeltung.MENGENTHEORETISCH: MengenRegisterTyp.ORDNUNGS_MENGEN,
    MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH: MengenRegisterTyp.SOUVERAENITAETS_MENGEN,
}

_PROZEDUR_MAP: dict[MengenRegisterGeltung, MengenRegisterProzedur] = {
    MengenRegisterGeltung.GESPERRT: MengenRegisterProzedur.NOTPROZEDUR,
    MengenRegisterGeltung.MENGENTHEORETISCH: MengenRegisterProzedur.REGELPROTOKOLL,
    MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH: MengenRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MengenRegisterGeltung, float] = {
    MengenRegisterGeltung.GESPERRT: 0.0,
    MengenRegisterGeltung.MENGENTHEORETISCH: 0.04,
    MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[MengenRegisterGeltung, int] = {
    MengenRegisterGeltung.GESPERRT: 0,
    MengenRegisterGeltung.MENGENTHEORETISCH: 1,
    MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MengenRegisterNorm:
    mengen_register_id: str
    mengen_typ: MengenRegisterTyp
    prozedur: MengenRegisterProzedur
    geltung: MengenRegisterGeltung
    mengen_weight: float
    mengen_tier: int
    canonical: bool
    mengen_ids: tuple[str, ...]
    mengen_tags: tuple[str, ...]


@dataclass(frozen=True)
class MengenRegister:
    register_id: str
    mathematik_feld: MathematikFeld
    normen: tuple[MengenRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mengen_register_id for n in self.normen if n.geltung is MengenRegisterGeltung.GESPERRT)

    @property
    def mengentheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mengen_register_id for n in self.normen if n.geltung is MengenRegisterGeltung.MENGENTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mengen_register_id for n in self.normen if n.geltung is MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH)

    @property
    def register_signal(self):
        if any(n.geltung is MengenRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is MengenRegisterGeltung.MENGENTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-mengentheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-mengentheoretisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_mengen_register(
    mathematik_feld: MathematikFeld | None = None,
    *,
    register_id: str = "mengen-register",
) -> MengenRegister:
    if mathematik_feld is None:
        mathematik_feld = build_mathematik_feld(feld_id=f"{register_id}-feld")

    normen: list[MengenRegisterNorm] = []
    for parent_norm in mathematik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.mathematik_feld_id.removeprefix(f'{mathematik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.mathematik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.mathematik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH)
        normen.append(
            MengenRegisterNorm(
                mengen_register_id=new_id,
                mengen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                mengen_weight=new_weight,
                mengen_tier=new_tier,
                canonical=is_canonical,
                mengen_ids=parent_norm.mathematik_ids + (new_id,),
                mengen_tags=parent_norm.mathematik_tags + (f"mengen:{new_geltung.value}",),
            )
        )
    return MengenRegister(
        register_id=register_id,
        mathematik_feld=mathematik_feld,
        normen=tuple(normen),
    )
