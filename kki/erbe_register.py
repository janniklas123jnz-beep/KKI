"""erbe_register — Zivilisation & Transzendenz layer 3 (#243)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .schoepfungs_vertrag import (
    SchoepfungsGeltung,
    SchoepfungsGrad,
    SchoepfungsNorm,
    SchoepfungsProzedur,
    SchoepfungsVertrag,
    build_schoepfungs_vertrag,
)

__all__ = [
    "ErbeKlasse",
    "ErbeProzedur",
    "ErbeGeltung",
    "ErbeNorm",
    "ErbeRegister",
    "build_erbe_register",
]


class ErbeKlasse(str, Enum):
    SCHUTZ_ERBE = "schutz-erbe"
    ORDNUNGS_ERBE = "ordnungs-erbe"
    SOUVERAENITAETS_ERBE = "souveraenitaets-erbe"


class ErbeProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ErbeGeltung(str, Enum):
    GESPERRT = "gesperrt"
    UEBERLIEFERT = "ueberliefert"
    GRUNDLEGEND_UEBERLIEFERT = "grundlegend-ueberliefert"


_KLASSE_MAP: dict[SchoepfungsGeltung, ErbeKlasse] = {
    SchoepfungsGeltung.GESPERRT: ErbeKlasse.SCHUTZ_ERBE,
    SchoepfungsGeltung.GESTIFTET: ErbeKlasse.ORDNUNGS_ERBE,
    SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET: ErbeKlasse.SOUVERAENITAETS_ERBE,
}
_PROZEDUR_MAP: dict[SchoepfungsGeltung, ErbeProzedur] = {
    SchoepfungsGeltung.GESPERRT: ErbeProzedur.NOTPROZEDUR,
    SchoepfungsGeltung.GESTIFTET: ErbeProzedur.REGELPROTOKOLL,
    SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET: ErbeProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[SchoepfungsGeltung, ErbeGeltung] = {
    SchoepfungsGeltung.GESPERRT: ErbeGeltung.GESPERRT,
    SchoepfungsGeltung.GESTIFTET: ErbeGeltung.UEBERLIEFERT,
    SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET: ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT,
}
_WEIGHT_BONUS: dict[SchoepfungsGeltung, float] = {
    SchoepfungsGeltung.GESPERRT: 0.0,
    SchoepfungsGeltung.GESTIFTET: 0.04,
    SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET: 0.08,
}
_TIER_BONUS: dict[SchoepfungsGeltung, int] = {
    SchoepfungsGeltung.GESPERRT: 0,
    SchoepfungsGeltung.GESTIFTET: 1,
    SchoepfungsGeltung.GRUNDLEGEND_GESTIFTET: 2,
}


@dataclass(frozen=True)
class ErbeNorm:
    erbe_register_id: str
    erbe_klasse: ErbeKlasse
    prozedur: ErbeProzedur
    geltung: ErbeGeltung
    erbe_weight: float
    erbe_tier: int
    canonical: bool
    erbe_register_ids: tuple[str, ...]
    erbe_register_tags: tuple[str, ...]


@dataclass(frozen=True)
class ErbeRegister:
    register_id: str
    schoepfungs_vertrag: SchoepfungsVertrag
    normen: tuple[ErbeNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erbe_register_id for n in self.normen if n.geltung is ErbeGeltung.GESPERRT)

    @property
    def ueberliefert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erbe_register_id for n in self.normen if n.geltung is ErbeGeltung.UEBERLIEFERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erbe_register_id for n in self.normen if n.geltung is ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT)

    @property
    def register_signal(self):
        if any(n.geltung is ErbeGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is ErbeGeltung.UEBERLIEFERT for n in self.normen):
            status = "register-ueberliefert"
            severity = "warning"
        else:
            status = "register-grundlegend-ueberliefert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_erbe_register(
    schoepfungs_vertrag: SchoepfungsVertrag | None = None,
    *,
    register_id: str = "erbe-register",
) -> ErbeRegister:
    if schoepfungs_vertrag is None:
        schoepfungs_vertrag = build_schoepfungs_vertrag(vertrag_id=f"{register_id}-vertrag")

    normen: list[ErbeNorm] = []
    for parent_norm in schoepfungs_vertrag.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.schoepfungs_vertrag_id.removeprefix(f'{schoepfungs_vertrag.vertrag_id}-')}"
        raw_weight = min(1.0, round(parent_norm.schoepfungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.schoepfungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT)
        normen.append(
            ErbeNorm(
                erbe_register_id=new_id,
                erbe_klasse=_KLASSE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                erbe_weight=raw_weight,
                erbe_tier=new_tier,
                canonical=is_canonical,
                erbe_register_ids=parent_norm.schoepfungs_vertrag_ids + (new_id,),
                erbe_register_tags=parent_norm.schoepfungs_vertrag_tags + (f"erbe-register:{new_geltung.value}",),
            )
        )

    return ErbeRegister(
        register_id=register_id,
        schoepfungs_vertrag=schoepfungs_vertrag,
        normen=tuple(normen),
    )
