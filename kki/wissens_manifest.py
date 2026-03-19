"""wissens_manifest — Zivilisation & Transzendenz layer 6 (#246)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kulturgut_kodex import (
    KulturgutGeltung,
    KulturgutKodex,
    KulturgutNorm,
    KulturgutProzedur,
    KulturgutRang,
    build_kulturgut_kodex,
)

__all__ = [
    "WissensGrad",
    "WissensProzedur",
    "WissensGeltung",
    "WissensNorm",
    "WissensManifest",
    "build_wissens_manifest",
]


class WissensGrad(str, Enum):
    SCHUTZ_WISSEN = "schutz-wissen"
    ORDNUNGS_WISSEN = "ordnungs-wissen"
    SOUVERAENITAETS_WISSEN = "souveraenitaets-wissen"


class WissensProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WissensGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERBREITET = "verbreitet"
    GRUNDLEGEND_VERBREITET = "grundlegend-verbreitet"


_GRAD_MAP: dict[KulturgutGeltung, WissensGrad] = {
    KulturgutGeltung.GESPERRT: WissensGrad.SCHUTZ_WISSEN,
    KulturgutGeltung.BEWAHRT: WissensGrad.ORDNUNGS_WISSEN,
    KulturgutGeltung.GRUNDLEGEND_BEWAHRT: WissensGrad.SOUVERAENITAETS_WISSEN,
}
_PROZEDUR_MAP: dict[KulturgutGeltung, WissensProzedur] = {
    KulturgutGeltung.GESPERRT: WissensProzedur.NOTPROZEDUR,
    KulturgutGeltung.BEWAHRT: WissensProzedur.REGELPROTOKOLL,
    KulturgutGeltung.GRUNDLEGEND_BEWAHRT: WissensProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KulturgutGeltung, WissensGeltung] = {
    KulturgutGeltung.GESPERRT: WissensGeltung.GESPERRT,
    KulturgutGeltung.BEWAHRT: WissensGeltung.VERBREITET,
    KulturgutGeltung.GRUNDLEGEND_BEWAHRT: WissensGeltung.GRUNDLEGEND_VERBREITET,
}
_WEIGHT_BONUS: dict[KulturgutGeltung, float] = {
    KulturgutGeltung.GESPERRT: 0.0,
    KulturgutGeltung.BEWAHRT: 0.04,
    KulturgutGeltung.GRUNDLEGEND_BEWAHRT: 0.08,
}
_TIER_BONUS: dict[KulturgutGeltung, int] = {
    KulturgutGeltung.GESPERRT: 0,
    KulturgutGeltung.BEWAHRT: 1,
    KulturgutGeltung.GRUNDLEGEND_BEWAHRT: 2,
}


@dataclass(frozen=True)
class WissensNorm:
    wissens_manifest_id: str
    wissens_grad: WissensGrad
    prozedur: WissensProzedur
    geltung: WissensGeltung
    wissens_weight: float
    wissens_tier: int
    canonical: bool
    wissens_manifest_ids: tuple[str, ...]
    wissens_manifest_tags: tuple[str, ...]


@dataclass(frozen=True)
class WissensManifest:
    manifest_id: str
    kulturgut_kodex: KulturgutKodex
    normen: tuple[WissensNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wissens_manifest_id for n in self.normen if n.geltung is WissensGeltung.GESPERRT)

    @property
    def verbreitet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wissens_manifest_id for n in self.normen if n.geltung is WissensGeltung.VERBREITET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wissens_manifest_id for n in self.normen if n.geltung is WissensGeltung.GRUNDLEGEND_VERBREITET)

    @property
    def manifest_signal(self):
        if any(n.geltung is WissensGeltung.GESPERRT for n in self.normen):
            status = "manifest-gesperrt"
            severity = "critical"
        elif any(n.geltung is WissensGeltung.VERBREITET for n in self.normen):
            status = "manifest-verbreitet"
            severity = "warning"
        else:
            status = "manifest-grundlegend-verbreitet"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_wissens_manifest(
    kulturgut_kodex: KulturgutKodex | None = None,
    *,
    manifest_id: str = "wissens-manifest",
) -> WissensManifest:
    if kulturgut_kodex is None:
        kulturgut_kodex = build_kulturgut_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[WissensNorm] = []
    for parent_norm in kulturgut_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{manifest_id}-{parent_norm.kulturgut_kodex_id.removeprefix(f'{kulturgut_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kulturgut_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kulturgut_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WissensGeltung.GRUNDLEGEND_VERBREITET)
        normen.append(
            WissensNorm(
                wissens_manifest_id=new_id,
                wissens_grad=_GRAD_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                wissens_weight=raw_weight,
                wissens_tier=new_tier,
                canonical=is_canonical,
                wissens_manifest_ids=parent_norm.kulturgut_kodex_ids + (new_id,),
                wissens_manifest_tags=parent_norm.kulturgut_kodex_tags + (f"wissens-manifest:{new_geltung.value}",),
            )
        )

    return WissensManifest(
        manifest_id=manifest_id,
        kulturgut_kodex=kulturgut_kodex,
        normen=tuple(normen),
    )
