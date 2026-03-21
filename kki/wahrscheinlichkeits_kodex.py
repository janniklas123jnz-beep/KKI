"""
#404 WahrscheinlichkeitsKodex — Wahrscheinlichkeitstheorie: Kolmogorov-Axiome (1933):
Wahrscheinlichkeitsraum (Ω, ℱ, P). Nicht-Negativität, Normierung, σ-Additivität.
Bayes-Theorem: P(H|E) = P(E|H)·P(H)/P(E). Bayesianisches Updating als rationale
Normanpassung. Gesetz der großen Zahlen (Bernoulli): Häufigkeitskonvergenz.
Zentraler Grenzwertsatz: Summe unabhängiger ZV → Normalverteilung. Cox-Axiome (1946):
Wahrscheinlichkeit als einzig konsistente Logikerweiterung.
Leitsterns Agenten sind probabilistisch kalibriert: sie quantifizieren Unsicherheit
korrekt und updaten rational gemäß Bayes.
Geltungsstufen: GESPERRT / PROBABILISTISCH / GRUNDLEGEND_PROBABILISTISCH
Parent: LogikCharta (#403)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .logik_charta import (
    LogikCharta,
    LogikChartaGeltung,
    build_logik_charta,
)

_GELTUNG_MAP: dict[LogikChartaGeltung, "WahrscheinlichkeitsKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LogikChartaGeltung.GESPERRT] = WahrscheinlichkeitsKodexGeltung.GESPERRT
    _GELTUNG_MAP[LogikChartaGeltung.LOGISCH] = WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH
    _GELTUNG_MAP[LogikChartaGeltung.GRUNDLEGEND_LOGISCH] = WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH


class WahrscheinlichkeitsKodexTyp(Enum):
    SCHUTZ_WAHRSCHEINLICHKEIT = "schutz-wahrscheinlichkeit"
    ORDNUNGS_WAHRSCHEINLICHKEIT = "ordnungs-wahrscheinlichkeit"
    SOUVERAENITAETS_WAHRSCHEINLICHKEIT = "souveraenitaets-wahrscheinlichkeit"


class WahrscheinlichkeitsKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WahrscheinlichkeitsKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    PROBABILISTISCH = "probabilistisch"
    GRUNDLEGEND_PROBABILISTISCH = "grundlegend-probabilistisch"


_init_map()

_TYP_MAP: dict[WahrscheinlichkeitsKodexGeltung, WahrscheinlichkeitsKodexTyp] = {
    WahrscheinlichkeitsKodexGeltung.GESPERRT: WahrscheinlichkeitsKodexTyp.SCHUTZ_WAHRSCHEINLICHKEIT,
    WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH: WahrscheinlichkeitsKodexTyp.ORDNUNGS_WAHRSCHEINLICHKEIT,
    WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH: WahrscheinlichkeitsKodexTyp.SOUVERAENITAETS_WAHRSCHEINLICHKEIT,
}

_PROZEDUR_MAP: dict[WahrscheinlichkeitsKodexGeltung, WahrscheinlichkeitsKodexProzedur] = {
    WahrscheinlichkeitsKodexGeltung.GESPERRT: WahrscheinlichkeitsKodexProzedur.NOTPROZEDUR,
    WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH: WahrscheinlichkeitsKodexProzedur.REGELPROTOKOLL,
    WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH: WahrscheinlichkeitsKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[WahrscheinlichkeitsKodexGeltung, float] = {
    WahrscheinlichkeitsKodexGeltung.GESPERRT: 0.0,
    WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH: 0.04,
    WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH: 0.08,
}

_TIER_DELTA: dict[WahrscheinlichkeitsKodexGeltung, int] = {
    WahrscheinlichkeitsKodexGeltung.GESPERRT: 0,
    WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH: 1,
    WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WahrscheinlichkeitsKodexNorm:
    wahrscheinlichkeits_kodex_id: str
    wahrscheinlichkeits_typ: WahrscheinlichkeitsKodexTyp
    prozedur: WahrscheinlichkeitsKodexProzedur
    geltung: WahrscheinlichkeitsKodexGeltung
    wahrscheinlichkeits_weight: float
    wahrscheinlichkeits_tier: int
    canonical: bool
    wahrscheinlichkeits_ids: tuple[str, ...]
    wahrscheinlichkeits_tags: tuple[str, ...]


@dataclass(frozen=True)
class WahrscheinlichkeitsKodex:
    kodex_id: str
    logik_charta: LogikCharta
    normen: tuple[WahrscheinlichkeitsKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wahrscheinlichkeits_kodex_id for n in self.normen if n.geltung is WahrscheinlichkeitsKodexGeltung.GESPERRT)

    @property
    def probabilistisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wahrscheinlichkeits_kodex_id for n in self.normen if n.geltung is WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wahrscheinlichkeits_kodex_id for n in self.normen if n.geltung is WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is WahrscheinlichkeitsKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-probabilistisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-probabilistisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_wahrscheinlichkeits_kodex(
    logik_charta: LogikCharta | None = None,
    *,
    kodex_id: str = "wahrscheinlichkeits-kodex",
) -> WahrscheinlichkeitsKodex:
    if logik_charta is None:
        logik_charta = build_logik_charta(charta_id=f"{kodex_id}-charta")

    normen: list[WahrscheinlichkeitsKodexNorm] = []
    for parent_norm in logik_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.logik_charta_id.removeprefix(f'{logik_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.logik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.logik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH)
        normen.append(
            WahrscheinlichkeitsKodexNorm(
                wahrscheinlichkeits_kodex_id=new_id,
                wahrscheinlichkeits_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                wahrscheinlichkeits_weight=new_weight,
                wahrscheinlichkeits_tier=new_tier,
                canonical=is_canonical,
                wahrscheinlichkeits_ids=parent_norm.logik_ids + (new_id,),
                wahrscheinlichkeits_tags=parent_norm.logik_tags + (f"wahrscheinlichkeit:{new_geltung.value}",),
            )
        )
    return WahrscheinlichkeitsKodex(
        kodex_id=kodex_id,
        logik_charta=logik_charta,
        normen=tuple(normen),
    )
