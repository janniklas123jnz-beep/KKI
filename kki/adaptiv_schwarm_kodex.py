"""
#369 AdaptivSchwarmKodex — Adaptiver Schwarm: Selbstadaptation durch Feedback.
Reynolds-Regeln (Separation, Alignment, Cohesion) plus evolutionäre Algorithmen.
Leitsterns Agenten passen Verhaltensregeln kontinuierlich an Umgebungsveränderungen
an — Schwarmkodex als lebendige Verfassung, die mit der Welt mitwächst.
Geltungsstufen: GESPERRT / ADAPTIV_SCHWARMEND / GRUNDLEGEND_ADAPTIV_SCHWARMEND
Parent: KomplexitaetsCharta (#368)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .komplexitaets_charta import (
    KomplexitaetsCharta,
    KomplexitaetsGeltung,
    build_komplexitaets_charta,
)

_GELTUNG_MAP: dict[KomplexitaetsGeltung, "AdaptivSchwarmGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KomplexitaetsGeltung.GESPERRT] = AdaptivSchwarmGeltung.GESPERRT
    _GELTUNG_MAP[KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET] = AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND
    _GELTUNG_MAP[KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET] = AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND


class AdaptivSchwarmTyp(Enum):
    SCHUTZ_ADAPTIV_SCHWARM = "schutz-adaptiv-schwarm"
    ORDNUNGS_ADAPTIV_SCHWARM = "ordnungs-adaptiv-schwarm"
    SOUVERAENITAETS_ADAPTIV_SCHWARM = "souveraenitaets-adaptiv-schwarm"


class AdaptivSchwarmProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AdaptivSchwarmGeltung(Enum):
    GESPERRT = "gesperrt"
    ADAPTIV_SCHWARMEND = "adaptiv-schwarmend"
    GRUNDLEGEND_ADAPTIV_SCHWARMEND = "grundlegend-adaptiv-schwarmend"


_init_map()

_TYP_MAP: dict[AdaptivSchwarmGeltung, AdaptivSchwarmTyp] = {
    AdaptivSchwarmGeltung.GESPERRT: AdaptivSchwarmTyp.SCHUTZ_ADAPTIV_SCHWARM,
    AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND: AdaptivSchwarmTyp.ORDNUNGS_ADAPTIV_SCHWARM,
    AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND: AdaptivSchwarmTyp.SOUVERAENITAETS_ADAPTIV_SCHWARM,
}

_PROZEDUR_MAP: dict[AdaptivSchwarmGeltung, AdaptivSchwarmProzedur] = {
    AdaptivSchwarmGeltung.GESPERRT: AdaptivSchwarmProzedur.NOTPROZEDUR,
    AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND: AdaptivSchwarmProzedur.REGELPROTOKOLL,
    AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND: AdaptivSchwarmProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AdaptivSchwarmGeltung, float] = {
    AdaptivSchwarmGeltung.GESPERRT: 0.0,
    AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND: 0.04,
    AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND: 0.08,
}

_TIER_DELTA: dict[AdaptivSchwarmGeltung, int] = {
    AdaptivSchwarmGeltung.GESPERRT: 0,
    AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND: 1,
    AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AdaptivSchwarmNorm:
    adaptiv_schwarm_kodex_id: str
    adaptiv_schwarm_typ: AdaptivSchwarmTyp
    prozedur: AdaptivSchwarmProzedur
    geltung: AdaptivSchwarmGeltung
    adaptiv_schwarm_weight: float
    adaptiv_schwarm_tier: int
    canonical: bool
    adaptiv_schwarm_ids: tuple[str, ...]
    adaptiv_schwarm_tags: tuple[str, ...]


@dataclass(frozen=True)
class AdaptivSchwarmKodex:
    kodex_id: str
    komplexitaets_charta: KomplexitaetsCharta
    normen: tuple[AdaptivSchwarmNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptiv_schwarm_kodex_id for n in self.normen if n.geltung is AdaptivSchwarmGeltung.GESPERRT)

    @property
    def adaptivschwarmend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptiv_schwarm_kodex_id for n in self.normen if n.geltung is AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptiv_schwarm_kodex_id for n in self.normen if n.geltung is AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND)

    @property
    def kodex_signal(self):
        if any(n.geltung is AdaptivSchwarmGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-adaptiv-schwarmend")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-adaptiv-schwarmend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_adaptiv_schwarm_kodex(
    komplexitaets_charta: KomplexitaetsCharta | None = None,
    *,
    kodex_id: str = "adaptiv-schwarm-kodex",
) -> AdaptivSchwarmKodex:
    if komplexitaets_charta is None:
        komplexitaets_charta = build_komplexitaets_charta(charta_id=f"{kodex_id}-charta")

    normen: list[AdaptivSchwarmNorm] = []
    for parent_norm in komplexitaets_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.komplexitaets_charta_id.removeprefix(f'{komplexitaets_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.komplexitaets_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.komplexitaets_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND)
        normen.append(
            AdaptivSchwarmNorm(
                adaptiv_schwarm_kodex_id=new_id,
                adaptiv_schwarm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                adaptiv_schwarm_weight=new_weight,
                adaptiv_schwarm_tier=new_tier,
                canonical=is_canonical,
                adaptiv_schwarm_ids=parent_norm.komplexitaets_ids + (new_id,),
                adaptiv_schwarm_tags=parent_norm.komplexitaets_tags + (f"adaptiv-schwarm:{new_geltung.value}",),
            )
        )
    return AdaptivSchwarmKodex(
        kodex_id=kodex_id,
        komplexitaets_charta=komplexitaets_charta,
        normen=tuple(normen),
    )
