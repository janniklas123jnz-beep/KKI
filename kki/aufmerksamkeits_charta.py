"""
#393 AufmerksamkeitsCharta — Aufmerksamkeit als selektive kognitive Ressource.
Treisman (1980): Feature Integration Theory — präattentive vs. fokale Verarbeitung.
Posner (1980): Spotlight-Modell — covert vs. overt Aufmerksamkeit, endogene vs.
exogene Orientierung. Attentional Blink (Raymond 1992): 200ms Refraktärperiode
nach Zielreiz — kein System kann alles gleichzeitig verarbeiten.
Load Theory (Lavie 1995): hohe Perceptual Load schützt vor Ablenkung.
Leitsterns Agenten fokussieren selektiv: kein Informationsrauschen überwältigt
den Signal-Pfad — Aufmerksamkeit ist Governance-Ressource.
Geltungsstufen: GESPERRT / AUFMERKSAMKEITSGELEITET / GRUNDLEGEND_AUFMERKSAMKEITSGELEITET
Parent: ArbeitsgedaechtnisRegister (#392)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .arbeitsgedaechtnis_register import (
    ArbeitsgedaechtnisGeltung,
    ArbeitsgedaechtnisRegister,
    build_arbeitsgedaechtnis_register,
)

_GELTUNG_MAP: dict[ArbeitsgedaechtnisGeltung, "AufmerksamkeitsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ArbeitsgedaechtnisGeltung.GESPERRT] = AufmerksamkeitsGeltung.GESPERRT
    _GELTUNG_MAP[ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV] = AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET
    _GELTUNG_MAP[ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV] = AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET


class AufmerksamkeitsTyp(Enum):
    SCHUTZ_AUFMERKSAMKEIT = "schutz-aufmerksamkeit"
    ORDNUNGS_AUFMERKSAMKEIT = "ordnungs-aufmerksamkeit"
    SOUVERAENITAETS_AUFMERKSAMKEIT = "souveraenitaets-aufmerksamkeit"


class AufmerksamkeitsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AufmerksamkeitsGeltung(Enum):
    GESPERRT = "gesperrt"
    AUFMERKSAMKEITSGELEITET = "aufmerksamkeitsgeleitet"
    GRUNDLEGEND_AUFMERKSAMKEITSGELEITET = "grundlegend-aufmerksamkeitsgeleitet"


_init_map()

_TYP_MAP: dict[AufmerksamkeitsGeltung, AufmerksamkeitsTyp] = {
    AufmerksamkeitsGeltung.GESPERRT: AufmerksamkeitsTyp.SCHUTZ_AUFMERKSAMKEIT,
    AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET: AufmerksamkeitsTyp.ORDNUNGS_AUFMERKSAMKEIT,
    AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET: AufmerksamkeitsTyp.SOUVERAENITAETS_AUFMERKSAMKEIT,
}

_PROZEDUR_MAP: dict[AufmerksamkeitsGeltung, AufmerksamkeitsProzedur] = {
    AufmerksamkeitsGeltung.GESPERRT: AufmerksamkeitsProzedur.NOTPROZEDUR,
    AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET: AufmerksamkeitsProzedur.REGELPROTOKOLL,
    AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET: AufmerksamkeitsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AufmerksamkeitsGeltung, float] = {
    AufmerksamkeitsGeltung.GESPERRT: 0.0,
    AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET: 0.04,
    AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET: 0.08,
}

_TIER_DELTA: dict[AufmerksamkeitsGeltung, int] = {
    AufmerksamkeitsGeltung.GESPERRT: 0,
    AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET: 1,
    AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AufmerksamkeitsNorm:
    aufmerksamkeits_charta_id: str
    aufmerksamkeits_typ: AufmerksamkeitsTyp
    prozedur: AufmerksamkeitsProzedur
    geltung: AufmerksamkeitsGeltung
    aufmerksamkeits_weight: float
    aufmerksamkeits_tier: int
    canonical: bool
    aufmerksamkeits_ids: tuple[str, ...]
    aufmerksamkeits_tags: tuple[str, ...]


@dataclass(frozen=True)
class AufmerksamkeitsCharta:
    charta_id: str
    arbeitsgedaechtnis_register: ArbeitsgedaechtnisRegister
    normen: tuple[AufmerksamkeitsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aufmerksamkeits_charta_id for n in self.normen if n.geltung is AufmerksamkeitsGeltung.GESPERRT)

    @property
    def aufmerksamkeitsgeleitet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aufmerksamkeits_charta_id for n in self.normen if n.geltung is AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.aufmerksamkeits_charta_id for n in self.normen if n.geltung is AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET)

    @property
    def charta_signal(self):
        if any(n.geltung is AufmerksamkeitsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-aufmerksamkeitsgeleitet")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-aufmerksamkeitsgeleitet")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_aufmerksamkeits_charta(
    arbeitsgedaechtnis_register: ArbeitsgedaechtnisRegister | None = None,
    *,
    charta_id: str = "aufmerksamkeits-charta",
) -> AufmerksamkeitsCharta:
    if arbeitsgedaechtnis_register is None:
        arbeitsgedaechtnis_register = build_arbeitsgedaechtnis_register(register_id=f"{charta_id}-register")

    normen: list[AufmerksamkeitsNorm] = []
    for parent_norm in arbeitsgedaechtnis_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.arbeitsgedaechtnis_register_id.removeprefix(f'{arbeitsgedaechtnis_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.arbeitsgedaechtnis_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.arbeitsgedaechtnis_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET)
        normen.append(
            AufmerksamkeitsNorm(
                aufmerksamkeits_charta_id=new_id,
                aufmerksamkeits_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                aufmerksamkeits_weight=new_weight,
                aufmerksamkeits_tier=new_tier,
                canonical=is_canonical,
                aufmerksamkeits_ids=parent_norm.arbeitsgedaechtnis_ids + (new_id,),
                aufmerksamkeits_tags=parent_norm.arbeitsgedaechtnis_tags + (f"aufmerksamkeit:{new_geltung.value}",),
            )
        )
    return AufmerksamkeitsCharta(
        charta_id=charta_id,
        arbeitsgedaechtnis_register=arbeitsgedaechtnis_register,
        normen=tuple(normen),
    )
