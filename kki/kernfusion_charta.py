"""
#359 KernfusionCharta — Kernfusion: D + T → ⁴He + n + 17,6 MeV.
2022 erzielte das NIF erstmals Q > 1 — mehr Energie aus als ein.
Das Lawson-Kriterium nτT > Schwelle ist das Governance-Pendant zu
beneficial AI: Capability × Safety × Alignment > Threshold.
Geltungsstufen: GESPERRT / KERNFUSIONIEREND / GRUNDLEGEND_KERNFUSIONIEREND
Parent: PlasmaWellenNormSatz (#358, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .plasmawellen_norm import (
    PlasmaWellenNormGeltung,
    PlasmaWellenNormSatz,
    build_plasmawellen_norm,
)

_GELTUNG_MAP: dict[PlasmaWellenNormGeltung, "KernfusionGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PlasmaWellenNormGeltung.GESPERRT] = KernfusionGeltung.GESPERRT
    _GELTUNG_MAP[PlasmaWellenNormGeltung.PLASMAWELLIG] = KernfusionGeltung.KERNFUSIONIEREND
    _GELTUNG_MAP[PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG] = KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND


class KernfusionTyp(Enum):
    SCHUTZ_KERNFUSION = "schutz-kernfusion"
    ORDNUNGS_KERNFUSION = "ordnungs-kernfusion"
    SOUVERAENITAETS_KERNFUSION = "souveraenitaets-kernfusion"


class KernfusionProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KernfusionGeltung(Enum):
    GESPERRT = "gesperrt"
    KERNFUSIONIEREND = "kernfusionierend"
    GRUNDLEGEND_KERNFUSIONIEREND = "grundlegend-kernfusionierend"


_init_map()

_TYP_MAP: dict[KernfusionGeltung, KernfusionTyp] = {
    KernfusionGeltung.GESPERRT: KernfusionTyp.SCHUTZ_KERNFUSION,
    KernfusionGeltung.KERNFUSIONIEREND: KernfusionTyp.ORDNUNGS_KERNFUSION,
    KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND: KernfusionTyp.SOUVERAENITAETS_KERNFUSION,
}

_PROZEDUR_MAP: dict[KernfusionGeltung, KernfusionProzedur] = {
    KernfusionGeltung.GESPERRT: KernfusionProzedur.NOTPROZEDUR,
    KernfusionGeltung.KERNFUSIONIEREND: KernfusionProzedur.REGELPROTOKOLL,
    KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND: KernfusionProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KernfusionGeltung, float] = {
    KernfusionGeltung.GESPERRT: 0.0,
    KernfusionGeltung.KERNFUSIONIEREND: 0.04,
    KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND: 0.08,
}

_TIER_DELTA: dict[KernfusionGeltung, int] = {
    KernfusionGeltung.GESPERRT: 0,
    KernfusionGeltung.KERNFUSIONIEREND: 1,
    KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KernfusionNorm:
    kernfusion_charta_id: str
    kernfusion_typ: KernfusionTyp
    prozedur: KernfusionProzedur
    geltung: KernfusionGeltung
    kernfusion_weight: float
    kernfusion_tier: int
    canonical: bool
    kernfusion_ids: tuple[str, ...]
    kernfusion_tags: tuple[str, ...]


@dataclass(frozen=True)
class KernfusionCharta:
    charta_id: str
    plasmawellen_norm: PlasmaWellenNormSatz
    normen: tuple[KernfusionNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernfusion_charta_id for n in self.normen if n.geltung is KernfusionGeltung.GESPERRT)

    @property
    def kernfusionierend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernfusion_charta_id for n in self.normen if n.geltung is KernfusionGeltung.KERNFUSIONIEREND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernfusion_charta_id for n in self.normen if n.geltung is KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND)

    @property
    def charta_signal(self):
        if any(n.geltung is KernfusionGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KernfusionGeltung.KERNFUSIONIEREND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kernfusionierend")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kernfusionierend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kernfusion_charta(
    plasmawellen_norm: PlasmaWellenNormSatz | None = None,
    *,
    charta_id: str = "kernfusion-charta",
) -> KernfusionCharta:
    if plasmawellen_norm is None:
        plasmawellen_norm = build_plasmawellen_norm(norm_id=f"{charta_id}-norm")

    normen: list[KernfusionNorm] = []
    for parent_norm in plasmawellen_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{plasmawellen_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.plasmawellen_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.plasmawellen_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND)
        normen.append(
            KernfusionNorm(
                kernfusion_charta_id=new_id,
                kernfusion_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kernfusion_weight=new_weight,
                kernfusion_tier=new_tier,
                canonical=is_canonical,
                kernfusion_ids=parent_norm.plasmawellen_norm_ids + (new_id,),
                kernfusion_tags=parent_norm.plasmawellen_norm_tags + (f"kernfusion:{new_geltung.value}",),
            )
        )
    return KernfusionCharta(
        charta_id=charta_id,
        plasmawellen_norm=plasmawellen_norm,
        normen=tuple(normen),
    )
