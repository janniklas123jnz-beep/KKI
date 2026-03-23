"""
#503 GerechtigkeitsCharta — Rawls/Nozick/Sen Grundlagen der Gerechtigkeitstheorie

John Rawls (1971): Eine Theorie der Gerechtigkeit — Schleier des Nichtwissens: rationale
  Akteure hinter dem Schleier wählen gerechte Prinzipien; Differenzprinzip: soziale und
  wirtschaftliche Ungleichheiten nur gerechtfertigt, wenn sie den am schlechtesten Gestellten
  maximalen Vorteil bringen; Grundfreiheiten haben lexikalischen Vorrang.
Robert Nozick (1974): Anarchie, Staat und Utopia — libertäre Gerechtigkeitstheorie; historische
  Anspruchstheorie: Verteilung ist gerecht, wenn sie durch gerechten Erwerb und gerechte
  Übertragung entstanden ist; Minimalstaat als einzig legitime staatliche Form.
Amartya Sen (1980): Equality of What? / Capability Approach — Gerechtigkeit als Erweiterung
  realer menschlicher Fähigkeiten (capabilities); Umwandlungsfaktoren zwischen Ressourcen und
  Handlungsmöglichkeiten; plurale Gerechtigkeitsmaßstäbe statt utilitaristischer Vereinfachung.
Leitsterns Peta-Schwarm verankert Gerechtigkeit als strukturelles Ordnungsprinzip: GESPERRT
sichert gerechtigkeitliche Kernansprüche, GERECHTIGKEITLICH ermöglicht adaptive Fairness-
Koordination, GRUNDLEGEND_GERECHTIGKEITLICH synthetisiert das vollständige Gerechtigkeits-
fundament für souveräne Peta-Schwarm-Entscheidungen. ⚖️
Parent: UtilitarismusRegister (#502)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .utilitarismus_register import (
    UtilitarismusRegister,
    UtilitarismusRegisterGeltung,
    build_utilitarismus_register,
)

_GELTUNG_MAP: dict[UtilitarismusRegisterGeltung, "GerechtigkeitsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[UtilitarismusRegisterGeltung.GESPERRT] = GerechtigkeitsChartaGeltung.GESPERRT
    _GELTUNG_MAP[UtilitarismusRegisterGeltung.UTILITARISTISCH] = GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH
    _GELTUNG_MAP[UtilitarismusRegisterGeltung.GRUNDLEGEND_UTILITARISTISCH] = GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH


class GerechtigkeitsChartaTyp(Enum):
    SCHUTZ_GERECHTIGKEIT = "schutz-gerechtigkeit"
    ORDNUNGS_GERECHTIGKEIT = "ordnungs-gerechtigkeit"
    SOUVERAENITAETS_GERECHTIGKEIT = "souveraenitaets-gerechtigkeit"


class GerechtigkeitsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GerechtigkeitsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    GERECHTIGKEITLICH = "gerechtigkeitlich"
    GRUNDLEGEND_GERECHTIGKEITLICH = "grundlegend-gerechtigkeitlich"


_init_map()

_TYP_MAP: dict[GerechtigkeitsChartaGeltung, GerechtigkeitsChartaTyp] = {
    GerechtigkeitsChartaGeltung.GESPERRT: GerechtigkeitsChartaTyp.SCHUTZ_GERECHTIGKEIT,
    GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH: GerechtigkeitsChartaTyp.ORDNUNGS_GERECHTIGKEIT,
    GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH: GerechtigkeitsChartaTyp.SOUVERAENITAETS_GERECHTIGKEIT,
}

_PROZEDUR_MAP: dict[GerechtigkeitsChartaGeltung, GerechtigkeitsChartaProzedur] = {
    GerechtigkeitsChartaGeltung.GESPERRT: GerechtigkeitsChartaProzedur.NOTPROZEDUR,
    GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH: GerechtigkeitsChartaProzedur.REGELPROTOKOLL,
    GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH: GerechtigkeitsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GerechtigkeitsChartaGeltung, float] = {
    GerechtigkeitsChartaGeltung.GESPERRT: 0.0,
    GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH: 0.04,
    GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH: 0.08,
}

_TIER_DELTA: dict[GerechtigkeitsChartaGeltung, int] = {
    GerechtigkeitsChartaGeltung.GESPERRT: 0,
    GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH: 1,
    GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH: 2,
}


@dataclass(frozen=True)
class GerechtigkeitsChartaNorm:
    gerechtigkeits_charta_id: str
    gerechtigkeits_typ: GerechtigkeitsChartaTyp
    prozedur: GerechtigkeitsChartaProzedur
    geltung: GerechtigkeitsChartaGeltung
    gerechtigkeits_weight: float
    gerechtigkeits_tier: int
    canonical: bool
    gerechtigkeits_ids: tuple[str, ...]
    gerechtigkeits_tags: tuple[str, ...]


@dataclass(frozen=True)
class GerechtigkeitsCharta:
    charta_id: str
    utilitarismus_register: UtilitarismusRegister
    normen: tuple[GerechtigkeitsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gerechtigkeits_charta_id for n in self.normen if n.geltung is GerechtigkeitsChartaGeltung.GESPERRT)

    @property
    def gerechtigkeitlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gerechtigkeits_charta_id for n in self.normen if n.geltung is GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gerechtigkeits_charta_id for n in self.normen if n.geltung is GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH)

    @property
    def charta_signal(self):
        if any(n.geltung is GerechtigkeitsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gerechtigkeitlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-gerechtigkeitlich")


def build_gerechtigkeits_charta(
    utilitarismus_register: UtilitarismusRegister | None = None,
    *,
    charta_id: str = "gerechtigkeits-charta",
) -> GerechtigkeitsCharta:
    if utilitarismus_register is None:
        utilitarismus_register = build_utilitarismus_register(register_id=f"{charta_id}-register")

    normen: list[GerechtigkeitsChartaNorm] = []
    for parent_norm in utilitarismus_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.utilitarismus_register_id.removeprefix(f'{utilitarismus_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.utilitarismus_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.utilitarismus_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH)
        normen.append(
            GerechtigkeitsChartaNorm(
                gerechtigkeits_charta_id=new_id,
                gerechtigkeits_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gerechtigkeits_weight=new_weight,
                gerechtigkeits_tier=new_tier,
                canonical=is_canonical,
                gerechtigkeits_ids=parent_norm.utilitarismus_ids + (new_id,),
                gerechtigkeits_tags=parent_norm.utilitarismus_tags + (f"gerechtigkeits-charta:{new_geltung.value}",),
            )
        )
    return GerechtigkeitsCharta(
        charta_id=charta_id,
        utilitarismus_register=utilitarismus_register,
        normen=tuple(normen),
    )
