"""
#418 SynergetikNorm — Synergetik: Ordnungsparameter und Versklavungsprinzip.
Haken (1969): Synergetik — Ordnungsparameter beschreiben Übergänge zu neuer Ordnung.
Versklavungsprinzip: schnelle Variablen folgen langsamen Ordnungsparametern.
Instabilitätspunkt: kleiner Parameter-Change → neue Makrostruktur.
Kollektive Variablen (Ordnungsparameter) regieren Subsysteme. Governance als Ordnungsparameter.
Laser: Paradigma der Synergetik — kohärentes Licht als kollektiver Ordnungsparameter.
Gehirn-Synergetik (Haken 1996): kognitive Muster als Ordnungsparameter.
Geltungsstufen: GESPERRT / SYNERGETISCH / GRUNDLEGEND_SYNERGETISCH
Parent: AdaptiveSystemeSenat (#417) — *_norm-Muster
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adaptive_systeme_senat import (
    AdaptiveSystemeSenat,
    AdaptiveSystemeSenatGeltung,
    build_adaptive_systeme_senat,
)

_GELTUNG_MAP: dict[AdaptiveSystemeSenatGeltung, "SynergetikNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AdaptiveSystemeSenatGeltung.GESPERRT] = SynergetikNormGeltung.GESPERRT
    _GELTUNG_MAP[AdaptiveSystemeSenatGeltung.ADAPTIV] = SynergetikNormGeltung.SYNERGETISCH
    _GELTUNG_MAP[AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV] = SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH


class SynergetikNormTyp(Enum):
    SCHUTZ_SYNERGETIK_NORM = "schutz-synergetik-norm"
    ORDNUNGS_SYNERGETIK_NORM = "ordnungs-synergetik-norm"
    SOUVERAENITAETS_SYNERGETIK_NORM = "souveraenitaets-synergetik-norm"


class SynergetikNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SynergetikNormGeltung(Enum):
    GESPERRT = "gesperrt"
    SYNERGETISCH = "synergetisch"
    GRUNDLEGEND_SYNERGETISCH = "grundlegend-synergetisch"


_init_map()

_TYP_MAP: dict[SynergetikNormGeltung, SynergetikNormTyp] = {
    SynergetikNormGeltung.GESPERRT: SynergetikNormTyp.SCHUTZ_SYNERGETIK_NORM,
    SynergetikNormGeltung.SYNERGETISCH: SynergetikNormTyp.ORDNUNGS_SYNERGETIK_NORM,
    SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH: SynergetikNormTyp.SOUVERAENITAETS_SYNERGETIK_NORM,
}

_PROZEDUR_MAP: dict[SynergetikNormGeltung, SynergetikNormProzedur] = {
    SynergetikNormGeltung.GESPERRT: SynergetikNormProzedur.NOTPROZEDUR,
    SynergetikNormGeltung.SYNERGETISCH: SynergetikNormProzedur.REGELPROTOKOLL,
    SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH: SynergetikNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SynergetikNormGeltung, float] = {
    SynergetikNormGeltung.GESPERRT: 0.0,
    SynergetikNormGeltung.SYNERGETISCH: 0.04,
    SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH: 0.08,
}

_TIER_DELTA: dict[SynergetikNormGeltung, int] = {
    SynergetikNormGeltung.GESPERRT: 0,
    SynergetikNormGeltung.SYNERGETISCH: 1,
    SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SynergetikNormEintrag:
    norm_id: str
    synergetik_norm_typ: SynergetikNormTyp
    prozedur: SynergetikNormProzedur
    geltung: SynergetikNormGeltung
    synergetik_norm_weight: float
    synergetik_norm_tier: int
    canonical: bool
    synergetik_norm_ids: tuple[str, ...]
    synergetik_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class SynergetikNormSatz:
    norm_id: str
    adaptive_systeme_senat: AdaptiveSystemeSenat
    normen: tuple[SynergetikNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SynergetikNormGeltung.GESPERRT)

    @property
    def synergetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SynergetikNormGeltung.SYNERGETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH)

    @property
    def norm_signal(self):
        if any(n.geltung is SynergetikNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is SynergetikNormGeltung.SYNERGETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-synergetisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-synergetisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_synergetik_norm(
    adaptive_systeme_senat: AdaptiveSystemeSenat | None = None,
    *,
    norm_id: str = "synergetik-norm",
) -> SynergetikNormSatz:
    if adaptive_systeme_senat is None:
        adaptive_systeme_senat = build_adaptive_systeme_senat(senat_id=f"{norm_id}-senat")

    normen: list[SynergetikNormEintrag] = []
    for parent_norm in adaptive_systeme_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.adaptive_systeme_senat_id.removeprefix(f'{adaptive_systeme_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.adaptiv_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.adaptiv_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SynergetikNormGeltung.GRUNDLEGEND_SYNERGETISCH)
        normen.append(
            SynergetikNormEintrag(
                norm_id=new_id,
                synergetik_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                synergetik_norm_weight=new_weight,
                synergetik_norm_tier=new_tier,
                canonical=is_canonical,
                synergetik_norm_ids=parent_norm.adaptiv_ids + (new_id,),
                synergetik_norm_tags=parent_norm.adaptiv_tags + (f"synergetik:{new_geltung.value}",),
            )
        )
    return SynergetikNormSatz(
        norm_id=norm_id,
        adaptive_systeme_senat=adaptive_systeme_senat,
        normen=tuple(normen),
    )
