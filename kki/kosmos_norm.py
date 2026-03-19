"""kosmos_norm — Weltrecht & Kosmopolitik layer 8 (#238)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .universalrechts_register import (
    UniversalrechtsGeltung,
    UniversalrechtsNorm,
    UniversalrechtsProzedur,
    UniversalrechtsRang,
    UniversalrechtsRegister,
    build_universalrechts_register,
)

__all__ = [
    "KosmosEbene",
    "KosmosProzedur",
    "KosmosGeltung",
    "KosmosNormEintrag",
    "KosmosNorm",
    "build_kosmos_norm",
]


class KosmosEbene(str, Enum):
    SCHUTZ_EBENE = "schutz-ebene"
    ORDNUNGS_EBENE = "ordnungs-ebene"
    SOUVERAENITAETS_EBENE = "souveraenitaets-ebene"


class KosmosProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KosmosGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOSMISCH = "kosmisch"
    GRUNDLEGEND_KOSMISCH = "grundlegend-kosmisch"


_EBENE_MAP: dict[UniversalrechtsGeltung, KosmosEbene] = {
    UniversalrechtsGeltung.GESPERRT: KosmosEbene.SCHUTZ_EBENE,
    UniversalrechtsGeltung.REGISTRIERT: KosmosEbene.ORDNUNGS_EBENE,
    UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT: KosmosEbene.SOUVERAENITAETS_EBENE,
}
_PROZEDUR_MAP: dict[UniversalrechtsGeltung, KosmosProzedur] = {
    UniversalrechtsGeltung.GESPERRT: KosmosProzedur.NOTPROZEDUR,
    UniversalrechtsGeltung.REGISTRIERT: KosmosProzedur.REGELPROTOKOLL,
    UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT: KosmosProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[UniversalrechtsGeltung, KosmosGeltung] = {
    UniversalrechtsGeltung.GESPERRT: KosmosGeltung.GESPERRT,
    UniversalrechtsGeltung.REGISTRIERT: KosmosGeltung.KOSMISCH,
    UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT: KosmosGeltung.GRUNDLEGEND_KOSMISCH,
}
_WEIGHT_BONUS: dict[UniversalrechtsGeltung, float] = {
    UniversalrechtsGeltung.GESPERRT: 0.0,
    UniversalrechtsGeltung.REGISTRIERT: 0.04,
    UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT: 0.08,
}
_TIER_BONUS: dict[UniversalrechtsGeltung, int] = {
    UniversalrechtsGeltung.GESPERRT: 0,
    UniversalrechtsGeltung.REGISTRIERT: 1,
    UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT: 2,
}


@dataclass(frozen=True)
class KosmosNormEintrag:
    kosmos_norm_id: str
    kosmos_ebene: KosmosEbene
    prozedur: KosmosProzedur
    geltung: KosmosGeltung
    kosmos_weight: float
    kosmos_tier: int
    canonical: bool
    kosmos_norm_ids: tuple[str, ...]
    kosmos_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class KosmosNorm:
    norm_id: str
    universalrechts_register: UniversalrechtsRegister
    normen: tuple[KosmosNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_norm_id for n in self.normen if n.geltung is KosmosGeltung.GESPERRT)

    @property
    def kosmisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_norm_id for n in self.normen if n.geltung is KosmosGeltung.KOSMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_norm_id for n in self.normen if n.geltung is KosmosGeltung.GRUNDLEGEND_KOSMISCH)

    @property
    def norm_signal(self):
        if any(n.geltung is KosmosGeltung.GESPERRT for n in self.normen):
            status = "norm-gesperrt"
            severity = "critical"
        elif any(n.geltung is KosmosGeltung.KOSMISCH for n in self.normen):
            status = "norm-kosmisch"
            severity = "warning"
        else:
            status = "norm-grundlegend-kosmisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kosmos_norm(
    universalrechts_register: UniversalrechtsRegister | None = None,
    *,
    norm_id: str = "kosmos-norm",
) -> KosmosNorm:
    if universalrechts_register is None:
        universalrechts_register = build_universalrechts_register(
            register_id=f"{norm_id}-register"
        )

    normen: list[KosmosNormEintrag] = []
    for parent_norm in universalrechts_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{norm_id}-{parent_norm.universalrechts_register_id.removeprefix(f'{universalrechts_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.universalrechts_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.universalrechts_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KosmosGeltung.GRUNDLEGEND_KOSMISCH)
        normen.append(
            KosmosNormEintrag(
                kosmos_norm_id=new_id,
                kosmos_ebene=_EBENE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kosmos_weight=raw_weight,
                kosmos_tier=new_tier,
                canonical=is_canonical,
                kosmos_norm_ids=parent_norm.universalrechts_register_ids + (new_id,),
                kosmos_norm_tags=parent_norm.universalrechts_register_tags + (f"kosmos-norm:{new_geltung.value}",),
            )
        )

    return KosmosNorm(
        norm_id=norm_id,
        universalrechts_register=universalrechts_register,
        normen=tuple(normen),
    )
