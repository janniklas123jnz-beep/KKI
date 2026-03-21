"""
#368 KomplexitaetsCharta — Komplexitätstheorie: Kolmogorov-Komplexität K(x),
algorithmische Information und Berechnungskomplexität. Die minimale Beschreibungs-
länge eines Schwarmzustandes begrenzt Governance-Overhead. Leitsterns Charta
definiert Komplexitätsobergrenzen pro Entscheidungsschicht.
Geltungsstufen: GESPERRT / KOMPLEXITAETSBEWERTET / GRUNDLEGEND_KOMPLEXITAETSBEWERTET
Parent: PerkolationsNorm (#367, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .perkolations_norm import (
    PerkolationsNormGeltung,
    PerkolationsNormSatz,
    build_perkolations_norm,
)

_GELTUNG_MAP: dict[PerkolationsNormGeltung, "KomplexitaetsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PerkolationsNormGeltung.GESPERRT] = KomplexitaetsGeltung.GESPERRT
    _GELTUNG_MAP[PerkolationsNormGeltung.PERKOLIEREND] = KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET
    _GELTUNG_MAP[PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND] = KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET


class KomplexitaetsTyp(Enum):
    SCHUTZ_KOMPLEXITAET = "schutz-komplexitaet"
    ORDNUNGS_KOMPLEXITAET = "ordnungs-komplexitaet"
    SOUVERAENITAETS_KOMPLEXITAET = "souveraenitaets-komplexitaet"


class KomplexitaetsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KomplexitaetsGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMPLEXITAETSBEWERTET = "komplexitaetsbewertet"
    GRUNDLEGEND_KOMPLEXITAETSBEWERTET = "grundlegend-komplexitaetsbewertet"


_init_map()

_TYP_MAP: dict[KomplexitaetsGeltung, KomplexitaetsTyp] = {
    KomplexitaetsGeltung.GESPERRT: KomplexitaetsTyp.SCHUTZ_KOMPLEXITAET,
    KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET: KomplexitaetsTyp.ORDNUNGS_KOMPLEXITAET,
    KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET: KomplexitaetsTyp.SOUVERAENITAETS_KOMPLEXITAET,
}

_PROZEDUR_MAP: dict[KomplexitaetsGeltung, KomplexitaetsProzedur] = {
    KomplexitaetsGeltung.GESPERRT: KomplexitaetsProzedur.NOTPROZEDUR,
    KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET: KomplexitaetsProzedur.REGELPROTOKOLL,
    KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET: KomplexitaetsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KomplexitaetsGeltung, float] = {
    KomplexitaetsGeltung.GESPERRT: 0.0,
    KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET: 0.04,
    KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET: 0.08,
}

_TIER_DELTA: dict[KomplexitaetsGeltung, int] = {
    KomplexitaetsGeltung.GESPERRT: 0,
    KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET: 1,
    KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KomplexitaetsNorm:
    komplexitaets_charta_id: str
    komplexitaets_typ: KomplexitaetsTyp
    prozedur: KomplexitaetsProzedur
    geltung: KomplexitaetsGeltung
    komplexitaets_weight: float
    komplexitaets_tier: int
    canonical: bool
    komplexitaets_ids: tuple[str, ...]
    komplexitaets_tags: tuple[str, ...]


@dataclass(frozen=True)
class KomplexitaetsCharta:
    charta_id: str
    perkolations_norm: PerkolationsNormSatz
    normen: tuple[KomplexitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_charta_id for n in self.normen if n.geltung is KomplexitaetsGeltung.GESPERRT)

    @property
    def komplexitaetsbewertet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_charta_id for n in self.normen if n.geltung is KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_charta_id for n in self.normen if n.geltung is KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET)

    @property
    def charta_signal(self):
        if any(n.geltung is KomplexitaetsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KomplexitaetsGeltung.KOMPLEXITAETSBEWERTET for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-komplexitaetsbewertet")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-komplexitaetsbewertet")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_komplexitaets_charta(
    perkolations_norm: PerkolationsNormSatz | None = None,
    *,
    charta_id: str = "komplexitaets-charta",
) -> KomplexitaetsCharta:
    if perkolations_norm is None:
        perkolations_norm = build_perkolations_norm(norm_id=f"{charta_id}-norm")

    normen: list[KomplexitaetsNorm] = []
    for parent_norm in perkolations_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{perkolations_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.perkolations_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.perkolations_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KomplexitaetsGeltung.GRUNDLEGEND_KOMPLEXITAETSBEWERTET)
        normen.append(
            KomplexitaetsNorm(
                komplexitaets_charta_id=new_id,
                komplexitaets_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                komplexitaets_weight=new_weight,
                komplexitaets_tier=new_tier,
                canonical=is_canonical,
                komplexitaets_ids=parent_norm.perkolations_norm_ids + (new_id,),
                komplexitaets_tags=parent_norm.perkolations_norm_tags + (f"komplexitaet:{new_geltung.value}",),
            )
        )
    return KomplexitaetsCharta(
        charta_id=charta_id,
        perkolations_norm=perkolations_norm,
        normen=tuple(normen),
    )
