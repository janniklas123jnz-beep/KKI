"""weisheits_norm — Zivilisation & Transzendenz layer 8 (#248)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gedaechtnis_senat import (
    GedaechtnisGeltung,
    GedaechtnisNorm,
    GedaechtnisProzedur,
    GedaechtnisRang,
    GedaechtnisSenat,
    build_gedaechtnis_senat,
)

__all__ = [
    "WeisheitsEbene",
    "WeisheitsProzedur",
    "WeisheitsGeltung",
    "WeisheitsNormEintrag",
    "WeisheitsNorm",
    "build_weisheits_norm",
]


class WeisheitsEbene(str, Enum):
    SCHUTZ_WEISHEIT = "schutz-weisheit"
    ORDNUNGS_WEISHEIT = "ordnungs-weisheit"
    SOUVERAENITAETS_WEISHEIT = "souveraenitaets-weisheit"


class WeisheitsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WeisheitsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEWEIHT = "geweiht"
    GRUNDLEGEND_GEWEIHT = "grundlegend-geweiht"


_EBENE_MAP: dict[GedaechtnisGeltung, WeisheitsEbene] = {
    GedaechtnisGeltung.GESPERRT: WeisheitsEbene.SCHUTZ_WEISHEIT,
    GedaechtnisGeltung.ERINNERT: WeisheitsEbene.ORDNUNGS_WEISHEIT,
    GedaechtnisGeltung.GRUNDLEGEND_ERINNERT: WeisheitsEbene.SOUVERAENITAETS_WEISHEIT,
}
_PROZEDUR_MAP: dict[GedaechtnisGeltung, WeisheitsProzedur] = {
    GedaechtnisGeltung.GESPERRT: WeisheitsProzedur.NOTPROZEDUR,
    GedaechtnisGeltung.ERINNERT: WeisheitsProzedur.REGELPROTOKOLL,
    GedaechtnisGeltung.GRUNDLEGEND_ERINNERT: WeisheitsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[GedaechtnisGeltung, WeisheitsGeltung] = {
    GedaechtnisGeltung.GESPERRT: WeisheitsGeltung.GESPERRT,
    GedaechtnisGeltung.ERINNERT: WeisheitsGeltung.GEWEIHT,
    GedaechtnisGeltung.GRUNDLEGEND_ERINNERT: WeisheitsGeltung.GRUNDLEGEND_GEWEIHT,
}
_WEIGHT_BONUS: dict[GedaechtnisGeltung, float] = {
    GedaechtnisGeltung.GESPERRT: 0.0,
    GedaechtnisGeltung.ERINNERT: 0.04,
    GedaechtnisGeltung.GRUNDLEGEND_ERINNERT: 0.08,
}
_TIER_BONUS: dict[GedaechtnisGeltung, int] = {
    GedaechtnisGeltung.GESPERRT: 0,
    GedaechtnisGeltung.ERINNERT: 1,
    GedaechtnisGeltung.GRUNDLEGEND_ERINNERT: 2,
}


@dataclass(frozen=True)
class WeisheitsNormEintrag:
    weisheits_norm_id: str
    weisheits_ebene: WeisheitsEbene
    prozedur: WeisheitsProzedur
    geltung: WeisheitsGeltung
    weisheits_weight: float
    weisheits_tier: int
    canonical: bool
    weisheits_norm_ids: tuple[str, ...]
    weisheits_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class WeisheitsNorm:
    norm_id: str
    gedaechtnis_senat: GedaechtnisSenat
    normen: tuple[WeisheitsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.weisheits_norm_id for n in self.normen if n.geltung is WeisheitsGeltung.GESPERRT)

    @property
    def geweiht_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.weisheits_norm_id for n in self.normen if n.geltung is WeisheitsGeltung.GEWEIHT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.weisheits_norm_id for n in self.normen if n.geltung is WeisheitsGeltung.GRUNDLEGEND_GEWEIHT)

    @property
    def norm_signal(self):
        if any(n.geltung is WeisheitsGeltung.GESPERRT for n in self.normen):
            status = "norm-gesperrt"
            severity = "critical"
        elif any(n.geltung is WeisheitsGeltung.GEWEIHT for n in self.normen):
            status = "norm-geweiht"
            severity = "warning"
        else:
            status = "norm-grundlegend-geweiht"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_weisheits_norm(
    gedaechtnis_senat: GedaechtnisSenat | None = None,
    *,
    norm_id: str = "weisheits-norm",
) -> WeisheitsNorm:
    if gedaechtnis_senat is None:
        gedaechtnis_senat = build_gedaechtnis_senat(senat_id=f"{norm_id}-senat")

    normen: list[WeisheitsNormEintrag] = []
    for parent_norm in gedaechtnis_senat.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{norm_id}-{parent_norm.gedaechtnis_senat_id.removeprefix(f'{gedaechtnis_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.gedaechtnis_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.gedaechtnis_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WeisheitsGeltung.GRUNDLEGEND_GEWEIHT)
        normen.append(
            WeisheitsNormEintrag(
                weisheits_norm_id=new_id,
                weisheits_ebene=_EBENE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                weisheits_weight=raw_weight,
                weisheits_tier=new_tier,
                canonical=is_canonical,
                weisheits_norm_ids=parent_norm.gedaechtnis_senat_ids + (new_id,),
                weisheits_norm_tags=parent_norm.gedaechtnis_senat_tags + (f"weisheits-norm:{new_geltung.value}",),
            )
        )

    return WeisheitsNorm(
        norm_id=norm_id,
        gedaechtnis_senat=gedaechtnis_senat,
        normen=tuple(normen),
    )
