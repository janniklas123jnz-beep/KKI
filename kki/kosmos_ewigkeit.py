"""kosmos_ewigkeit — Metaphysik & Kosmologie layer 8 (#258)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .einheits_senat import (
    EinheitsGeltung,
    EinheitsNorm,
    EinheitsSenat,
    EinheitsProzedur,
    EinheitsTyp,
    build_einheits_senat,
)

__all__ = [
    "KosmosEwigkeitsRang",
    "KosmosEwigkeitsProzedur",
    "KosmosEwigkeitsGeltung",
    "KosmosEwigkeitsNormEintrag",
    "KosmosEwigkeit",
    "build_kosmos_ewigkeit",
]


class KosmosEwigkeitsRang(str, Enum):
    SCHUTZ_EWIGKEIT = "schutz-ewigkeit"
    ORDNUNGS_EWIGKEIT = "ordnungs-ewigkeit"
    SOUVERAENITAETS_EWIGKEIT = "souveraenitaets-ewigkeit"


class KosmosEwigkeitsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KosmosEwigkeitsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    EWIG = "ewig"
    GRUNDLEGEND_EWIG = "grundlegend-ewig"


_RANG_MAP: dict[EinheitsGeltung, KosmosEwigkeitsRang] = {
    EinheitsGeltung.GESPERRT: KosmosEwigkeitsRang.SCHUTZ_EWIGKEIT,
    EinheitsGeltung.GEEINT: KosmosEwigkeitsRang.ORDNUNGS_EWIGKEIT,
    EinheitsGeltung.GRUNDLEGEND_GEEINT: KosmosEwigkeitsRang.SOUVERAENITAETS_EWIGKEIT,
}
_PROZEDUR_MAP: dict[EinheitsGeltung, KosmosEwigkeitsProzedur] = {
    EinheitsGeltung.GESPERRT: KosmosEwigkeitsProzedur.NOTPROZEDUR,
    EinheitsGeltung.GEEINT: KosmosEwigkeitsProzedur.REGELPROTOKOLL,
    EinheitsGeltung.GRUNDLEGEND_GEEINT: KosmosEwigkeitsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[EinheitsGeltung, KosmosEwigkeitsGeltung] = {
    EinheitsGeltung.GESPERRT: KosmosEwigkeitsGeltung.GESPERRT,
    EinheitsGeltung.GEEINT: KosmosEwigkeitsGeltung.EWIG,
    EinheitsGeltung.GRUNDLEGEND_GEEINT: KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG,
}
_WEIGHT_BONUS: dict[EinheitsGeltung, float] = {
    EinheitsGeltung.GESPERRT: 0.0,
    EinheitsGeltung.GEEINT: 0.04,
    EinheitsGeltung.GRUNDLEGEND_GEEINT: 0.08,
}
_TIER_BONUS: dict[EinheitsGeltung, int] = {
    EinheitsGeltung.GESPERRT: 0,
    EinheitsGeltung.GEEINT: 1,
    EinheitsGeltung.GRUNDLEGEND_GEEINT: 2,
}


@dataclass(frozen=True)
class KosmosEwigkeitsNormEintrag:
    kosmos_ewigkeit_id: str
    kosmos_ewigkeits_rang: KosmosEwigkeitsRang
    prozedur: KosmosEwigkeitsProzedur
    geltung: KosmosEwigkeitsGeltung
    kosmos_ewigkeits_weight: float
    kosmos_ewigkeits_tier: int
    canonical: bool
    kosmos_ewigkeit_ids: tuple[str, ...]
    kosmos_ewigkeit_tags: tuple[str, ...]


@dataclass(frozen=True)
class KosmosEwigkeit:
    ewigkeit_id: str
    einheits_senat: EinheitsSenat
    normen: tuple[KosmosEwigkeitsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_ewigkeit_id for n in self.normen if n.geltung is KosmosEwigkeitsGeltung.GESPERRT)

    @property
    def ewig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_ewigkeit_id for n in self.normen if n.geltung is KosmosEwigkeitsGeltung.EWIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_ewigkeit_id for n in self.normen if n.geltung is KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG)

    @property
    def ewigkeit_signal(self):
        if any(n.geltung is KosmosEwigkeitsGeltung.GESPERRT for n in self.normen):
            status = "ewigkeit-gesperrt"
            severity = "critical"
        elif any(n.geltung is KosmosEwigkeitsGeltung.EWIG for n in self.normen):
            status = "ewigkeit-ewig"
            severity = "warning"
        else:
            status = "ewigkeit-grundlegend-ewig"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kosmos_ewigkeit(
    einheits_senat: EinheitsSenat | None = None,
    *,
    ewigkeit_id: str = "kosmos-ewigkeit",
) -> KosmosEwigkeit:
    if einheits_senat is None:
        einheits_senat = build_einheits_senat(senat_id=f"{ewigkeit_id}-senat")

    normen: list[KosmosEwigkeitsNormEintrag] = []
    for parent_norm in einheits_senat.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{ewigkeit_id}-{parent_norm.einheits_senat_id.removeprefix(f'{einheits_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.einheits_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.einheits_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG)
        normen.append(
            KosmosEwigkeitsNormEintrag(
                kosmos_ewigkeit_id=new_id,
                kosmos_ewigkeits_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kosmos_ewigkeits_weight=raw_weight,
                kosmos_ewigkeits_tier=new_tier,
                canonical=is_canonical,
                kosmos_ewigkeit_ids=parent_norm.einheits_senat_ids + (new_id,),
                kosmos_ewigkeit_tags=parent_norm.einheits_senat_tags + (f"kosmos-ewigkeit:{new_geltung.value}",),
            )
        )

    return KosmosEwigkeit(
        ewigkeit_id=ewigkeit_id,
        einheits_senat=einheits_senat,
        normen=tuple(normen),
    )
