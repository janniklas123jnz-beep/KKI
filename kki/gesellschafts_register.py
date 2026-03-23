"""
#492 GesellschaftsRegister — Weber: Bürokratie/Herrschaft; Simmel: Vergesellschaftung

Max Weber (1922): Wirtschaft und Gesellschaft — drei Herrschaftstypen (traditional,
  charismatisch, rational-legal); Bürokratie als reinste Form rationaler Herrschaft;
  Rationalisierung als unaufhaltsamer Modernisierungsprozess.
Max Weber (1904): Protestantische Ethik — Wahlverwandtschaft zwischen protestantischer
  Ethik und kapitalistischem Geist als Motor gesellschaftlicher Rationalisierung.
Georg Simmel (1908): Soziologie — Vergesellschaftung als kontinuierlicher Prozess
  wechselseitiger Einwirkung; Gesellschaft entsteht stets neu im sozialen Handeln.
Leitsterns Terra-Schwarm registriert Gesellschaftsstrukturen: GESPERRT sichert
institutionelle Normkerne, GESELLSCHAFTLICH ermöglicht bürokratische Koordination,
GRUNDLEGEND_GESELLSCHAFTLICH synthetisiert rationale Herrschaftsordnung für den Weg
zur Peta-Schwarmgröße.
Parent: SoziologieFeld (#491)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .soziologie_feld import (
    SoziologieFeld,
    SoziologieFeldGeltung,
    build_soziologie_feld,
)

_GELTUNG_MAP: dict[SoziologieFeldGeltung, "GesellschaftsRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SoziologieFeldGeltung.GESPERRT] = GesellschaftsRegisterGeltung.GESPERRT
    _GELTUNG_MAP[SoziologieFeldGeltung.SOZIOLOGISCH] = GesellschaftsRegisterGeltung.GESELLSCHAFTLICH
    _GELTUNG_MAP[SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH] = GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH


class GesellschaftsRegisterTyp(Enum):
    SCHUTZ_GESELLSCHAFT = "schutz-gesellschaft"
    ORDNUNGS_GESELLSCHAFT = "ordnungs-gesellschaft"
    SOUVERAENITAETS_GESELLSCHAFT = "souveraenitaets-gesellschaft"


class GesellschaftsRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GesellschaftsRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    GESELLSCHAFTLICH = "gesellschaftlich"
    GRUNDLEGEND_GESELLSCHAFTLICH = "grundlegend-gesellschaftlich"


_init_map()

_TYP_MAP: dict[GesellschaftsRegisterGeltung, GesellschaftsRegisterTyp] = {
    GesellschaftsRegisterGeltung.GESPERRT: GesellschaftsRegisterTyp.SCHUTZ_GESELLSCHAFT,
    GesellschaftsRegisterGeltung.GESELLSCHAFTLICH: GesellschaftsRegisterTyp.ORDNUNGS_GESELLSCHAFT,
    GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH: GesellschaftsRegisterTyp.SOUVERAENITAETS_GESELLSCHAFT,
}

_PROZEDUR_MAP: dict[GesellschaftsRegisterGeltung, GesellschaftsRegisterProzedur] = {
    GesellschaftsRegisterGeltung.GESPERRT: GesellschaftsRegisterProzedur.NOTPROZEDUR,
    GesellschaftsRegisterGeltung.GESELLSCHAFTLICH: GesellschaftsRegisterProzedur.REGELPROTOKOLL,
    GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH: GesellschaftsRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GesellschaftsRegisterGeltung, float] = {
    GesellschaftsRegisterGeltung.GESPERRT: 0.0,
    GesellschaftsRegisterGeltung.GESELLSCHAFTLICH: 0.04,
    GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH: 0.08,
}

_TIER_DELTA: dict[GesellschaftsRegisterGeltung, int] = {
    GesellschaftsRegisterGeltung.GESPERRT: 0,
    GesellschaftsRegisterGeltung.GESELLSCHAFTLICH: 1,
    GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH: 2,
}


@dataclass(frozen=True)
class GesellschaftsRegisterNorm:
    gesellschafts_register_id: str
    gesellschafts_typ: GesellschaftsRegisterTyp
    prozedur: GesellschaftsRegisterProzedur
    geltung: GesellschaftsRegisterGeltung
    gesellschafts_weight: float
    gesellschafts_tier: int
    canonical: bool
    gesellschafts_ids: tuple[str, ...]
    gesellschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class GesellschaftsRegister:
    register_id: str
    soziologie_feld: SoziologieFeld
    normen: tuple[GesellschaftsRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gesellschafts_register_id for n in self.normen if n.geltung is GesellschaftsRegisterGeltung.GESPERRT)

    @property
    def gesellschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gesellschafts_register_id for n in self.normen if n.geltung is GesellschaftsRegisterGeltung.GESELLSCHAFTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gesellschafts_register_id for n in self.normen if n.geltung is GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH)

    @property
    def register_signal(self):
        if any(n.geltung is GesellschaftsRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is GesellschaftsRegisterGeltung.GESELLSCHAFTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesellschaftlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-gesellschaftlich")


def build_gesellschafts_register(
    soziologie_feld: SoziologieFeld | None = None,
    *,
    register_id: str = "gesellschafts-register",
) -> GesellschaftsRegister:
    if soziologie_feld is None:
        soziologie_feld = build_soziologie_feld(feld_id=f"{register_id}-feld")

    normen: list[GesellschaftsRegisterNorm] = []
    for parent_norm in soziologie_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.soziologie_feld_id.removeprefix(f'{soziologie_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.soziologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.soziologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GesellschaftsRegisterGeltung.GRUNDLEGEND_GESELLSCHAFTLICH)
        normen.append(
            GesellschaftsRegisterNorm(
                gesellschafts_register_id=new_id,
                gesellschafts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gesellschafts_weight=new_weight,
                gesellschafts_tier=new_tier,
                canonical=is_canonical,
                gesellschafts_ids=parent_norm.soziologie_ids + (new_id,),
                gesellschafts_tags=parent_norm.soziologie_tags + (f"gesellschafts-register:{new_geltung.value}",),
            )
        )
    return GesellschaftsRegister(
        register_id=register_id,
        soziologie_feld=soziologie_feld,
        normen=tuple(normen),
    )
