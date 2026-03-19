"""erkenntnis_charta — Zivilisation & Transzendenz layer 9 (#249)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .weisheits_norm import (
    WeisheitsEbene,
    WeisheitsGeltung,
    WeisheitsNorm,
    WeisheitsNormEintrag,
    WeisheitsProzedur,
    build_weisheits_norm,
)

__all__ = [
    "ErkenntnisTyp",
    "ErkenntnisProzedur",
    "ErkenntnisGeltung",
    "ErkenntnisNorm",
    "ErkenntnisCharta",
    "build_erkenntnis_charta",
]


class ErkenntnisTyp(str, Enum):
    SCHUTZ_ERKENNTNIS = "schutz-erkenntnis"
    ORDNUNGS_ERKENNTNIS = "ordnungs-erkenntnis"
    SOUVERAENITAETS_ERKENNTNIS = "souveraenitaets-erkenntnis"


class ErkenntnisProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ErkenntnisGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ERLEUCHTET = "erleuchtet"
    GRUNDLEGEND_ERLEUCHTET = "grundlegend-erleuchtet"


_TYP_MAP: dict[WeisheitsGeltung, ErkenntnisTyp] = {
    WeisheitsGeltung.GESPERRT: ErkenntnisTyp.SCHUTZ_ERKENNTNIS,
    WeisheitsGeltung.GEWEIHT: ErkenntnisTyp.ORDNUNGS_ERKENNTNIS,
    WeisheitsGeltung.GRUNDLEGEND_GEWEIHT: ErkenntnisTyp.SOUVERAENITAETS_ERKENNTNIS,
}
_PROZEDUR_MAP: dict[WeisheitsGeltung, ErkenntnisProzedur] = {
    WeisheitsGeltung.GESPERRT: ErkenntnisProzedur.NOTPROZEDUR,
    WeisheitsGeltung.GEWEIHT: ErkenntnisProzedur.REGELPROTOKOLL,
    WeisheitsGeltung.GRUNDLEGEND_GEWEIHT: ErkenntnisProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[WeisheitsGeltung, ErkenntnisGeltung] = {
    WeisheitsGeltung.GESPERRT: ErkenntnisGeltung.GESPERRT,
    WeisheitsGeltung.GEWEIHT: ErkenntnisGeltung.ERLEUCHTET,
    WeisheitsGeltung.GRUNDLEGEND_GEWEIHT: ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET,
}
_WEIGHT_BONUS: dict[WeisheitsGeltung, float] = {
    WeisheitsGeltung.GESPERRT: 0.0,
    WeisheitsGeltung.GEWEIHT: 0.04,
    WeisheitsGeltung.GRUNDLEGEND_GEWEIHT: 0.08,
}
_TIER_BONUS: dict[WeisheitsGeltung, int] = {
    WeisheitsGeltung.GESPERRT: 0,
    WeisheitsGeltung.GEWEIHT: 1,
    WeisheitsGeltung.GRUNDLEGEND_GEWEIHT: 2,
}


@dataclass(frozen=True)
class ErkenntnisNorm:
    erkenntnis_charta_id: str
    erkenntnis_typ: ErkenntnisTyp
    prozedur: ErkenntnisProzedur
    geltung: ErkenntnisGeltung
    erkenntnis_weight: float
    erkenntnis_tier: int
    canonical: bool
    erkenntnis_charta_ids: tuple[str, ...]
    erkenntnis_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class ErkenntnisCharta:
    charta_id: str
    weisheits_norm: WeisheitsNorm
    normen: tuple[ErkenntnisNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erkenntnis_charta_id for n in self.normen if n.geltung is ErkenntnisGeltung.GESPERRT)

    @property
    def erleuchtet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erkenntnis_charta_id for n in self.normen if n.geltung is ErkenntnisGeltung.ERLEUCHTET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erkenntnis_charta_id for n in self.normen if n.geltung is ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET)

    @property
    def charta_signal(self):
        if any(n.geltung is ErkenntnisGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is ErkenntnisGeltung.ERLEUCHTET for n in self.normen):
            status = "charta-erleuchtet"
            severity = "warning"
        else:
            status = "charta-grundlegend-erleuchtet"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_erkenntnis_charta(
    weisheits_norm: WeisheitsNorm | None = None,
    *,
    charta_id: str = "erkenntnis-charta",
) -> ErkenntnisCharta:
    if weisheits_norm is None:
        weisheits_norm = build_weisheits_norm(norm_id=f"{charta_id}-norm")

    normen: list[ErkenntnisNorm] = []
    for parent_norm in weisheits_norm.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.weisheits_norm_id.removeprefix(f'{weisheits_norm.norm_id}-')}"
        raw_weight = min(1.0, round(parent_norm.weisheits_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.weisheits_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET)
        normen.append(
            ErkenntnisNorm(
                erkenntnis_charta_id=new_id,
                erkenntnis_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                erkenntnis_weight=raw_weight,
                erkenntnis_tier=new_tier,
                canonical=is_canonical,
                erkenntnis_charta_ids=parent_norm.weisheits_norm_ids + (new_id,),
                erkenntnis_charta_tags=parent_norm.weisheits_norm_tags + (f"erkenntnis-charta:{new_geltung.value}",),
            )
        )

    return ErkenntnisCharta(
        charta_id=charta_id,
        weisheits_norm=weisheits_norm,
        normen=tuple(normen),
    )
