"""einheits_senat — Metaphysik & Kosmologie layer 7 (#257)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .harmonie_pakt import (
    HarmonieGeltung,
    HarmonieNorm,
    HarmoniePakt,
    HarmonieProzedur,
    HarmonieTyp,
    build_harmonie_pakt,
)

__all__ = [
    "EinheitsTyp",
    "EinheitsProzedur",
    "EinheitsGeltung",
    "EinheitsNorm",
    "EinheitsSenat",
    "build_einheits_senat",
]


class EinheitsTyp(str, Enum):
    SCHUTZ_EINHEIT = "schutz-einheit"
    ORDNUNGS_EINHEIT = "ordnungs-einheit"
    SOUVERAENITAETS_EINHEIT = "souveraenitaets-einheit"


class EinheitsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EinheitsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEEINT = "geeint"
    GRUNDLEGEND_GEEINT = "grundlegend-geeint"


_TYP_MAP: dict[HarmonieGeltung, EinheitsTyp] = {
    HarmonieGeltung.GESPERRT: EinheitsTyp.SCHUTZ_EINHEIT,
    HarmonieGeltung.HARMONISIERT: EinheitsTyp.ORDNUNGS_EINHEIT,
    HarmonieGeltung.GRUNDLEGEND_HARMONISIERT: EinheitsTyp.SOUVERAENITAETS_EINHEIT,
}
_PROZEDUR_MAP: dict[HarmonieGeltung, EinheitsProzedur] = {
    HarmonieGeltung.GESPERRT: EinheitsProzedur.NOTPROZEDUR,
    HarmonieGeltung.HARMONISIERT: EinheitsProzedur.REGELPROTOKOLL,
    HarmonieGeltung.GRUNDLEGEND_HARMONISIERT: EinheitsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[HarmonieGeltung, EinheitsGeltung] = {
    HarmonieGeltung.GESPERRT: EinheitsGeltung.GESPERRT,
    HarmonieGeltung.HARMONISIERT: EinheitsGeltung.GEEINT,
    HarmonieGeltung.GRUNDLEGEND_HARMONISIERT: EinheitsGeltung.GRUNDLEGEND_GEEINT,
}
_WEIGHT_BONUS: dict[HarmonieGeltung, float] = {
    HarmonieGeltung.GESPERRT: 0.0,
    HarmonieGeltung.HARMONISIERT: 0.04,
    HarmonieGeltung.GRUNDLEGEND_HARMONISIERT: 0.08,
}
_TIER_BONUS: dict[HarmonieGeltung, int] = {
    HarmonieGeltung.GESPERRT: 0,
    HarmonieGeltung.HARMONISIERT: 1,
    HarmonieGeltung.GRUNDLEGEND_HARMONISIERT: 2,
}


@dataclass(frozen=True)
class EinheitsNorm:
    einheits_senat_id: str
    einheits_typ: EinheitsTyp
    prozedur: EinheitsProzedur
    geltung: EinheitsGeltung
    einheits_weight: float
    einheits_tier: int
    canonical: bool
    einheits_senat_ids: tuple[str, ...]
    einheits_senat_tags: tuple[str, ...]


@dataclass(frozen=True)
class EinheitsSenat:
    senat_id: str
    harmonie_pakt: HarmoniePakt
    normen: tuple[EinheitsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.einheits_senat_id for n in self.normen if n.geltung is EinheitsGeltung.GESPERRT)

    @property
    def geeint_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.einheits_senat_id for n in self.normen if n.geltung is EinheitsGeltung.GEEINT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.einheits_senat_id for n in self.normen if n.geltung is EinheitsGeltung.GRUNDLEGEND_GEEINT)

    @property
    def senat_signal(self):
        if any(n.geltung is EinheitsGeltung.GESPERRT for n in self.normen):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(n.geltung is EinheitsGeltung.GEEINT for n in self.normen):
            status = "senat-geeint"
            severity = "warning"
        else:
            status = "senat-grundlegend-geeint"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_einheits_senat(
    harmonie_pakt: HarmoniePakt | None = None,
    *,
    senat_id: str = "einheits-senat",
) -> EinheitsSenat:
    if harmonie_pakt is None:
        harmonie_pakt = build_harmonie_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[EinheitsNorm] = []
    for parent_norm in harmonie_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{senat_id}-{parent_norm.harmonie_pakt_id.removeprefix(f'{harmonie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.harmonie_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.harmonie_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EinheitsGeltung.GRUNDLEGEND_GEEINT)
        normen.append(
            EinheitsNorm(
                einheits_senat_id=new_id,
                einheits_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                einheits_weight=raw_weight,
                einheits_tier=new_tier,
                canonical=is_canonical,
                einheits_senat_ids=parent_norm.harmonie_pakt_ids + (new_id,),
                einheits_senat_tags=parent_norm.harmonie_pakt_tags + (f"einheits-senat:{new_geltung.value}",),
            )
        )

    return EinheitsSenat(
        senat_id=senat_id,
        harmonie_pakt=harmonie_pakt,
        normen=tuple(normen),
    )
