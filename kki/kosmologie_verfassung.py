"""
#330 KosmologieVerfassung — Block-Krone: Kosmologie als höchste Governance-Instanz.
Geltungsstufen: GESPERRT / KOSMOLOGIEVERFASST / GRUNDLEGEND_KOSMOLOGIEVERFASST
Parent: HubbleCharta (#329)
Block #321–#330 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .hubble_charta import (
    HubbleCharta,
    HubbleGeltung,
    build_hubble_charta,
)

_GELTUNG_MAP: dict[HubbleGeltung, "KosmologieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HubbleGeltung.GESPERRT] = KosmologieVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[HubbleGeltung.HUBBLEGEBUNDEN] = KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST
    _GELTUNG_MAP[HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN] = KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST


class KosmologieVerfassungsTyp(Enum):
    SCHUTZ_KOSMOLOGIEVERFASSUNG = "schutz-kosmologieverfassung"
    ORDNUNGS_KOSMOLOGIEVERFASSUNG = "ordnungs-kosmologieverfassung"
    SOUVERAENITAETS_KOSMOLOGIEVERFASSUNG = "souveraenitaets-kosmologieverfassung"


class KosmologieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KosmologieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KOSMOLOGIEVERFASST = "kosmologieverfasst"
    GRUNDLEGEND_KOSMOLOGIEVERFASST = "grundlegend-kosmologieverfasst"


_init_map()

_TYP_MAP: dict[KosmologieVerfassungsGeltung, KosmologieVerfassungsTyp] = {
    KosmologieVerfassungsGeltung.GESPERRT: KosmologieVerfassungsTyp.SCHUTZ_KOSMOLOGIEVERFASSUNG,
    KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST: KosmologieVerfassungsTyp.ORDNUNGS_KOSMOLOGIEVERFASSUNG,
    KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST: KosmologieVerfassungsTyp.SOUVERAENITAETS_KOSMOLOGIEVERFASSUNG,
}

_PROZEDUR_MAP: dict[KosmologieVerfassungsGeltung, KosmologieVerfassungsProzedur] = {
    KosmologieVerfassungsGeltung.GESPERRT: KosmologieVerfassungsProzedur.NOTPROZEDUR,
    KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST: KosmologieVerfassungsProzedur.REGELPROTOKOLL,
    KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST: KosmologieVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KosmologieVerfassungsGeltung, float] = {
    KosmologieVerfassungsGeltung.GESPERRT: 0.0,
    KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST: 0.04,
    KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST: 0.08,
}

_TIER_DELTA: dict[KosmologieVerfassungsGeltung, int] = {
    KosmologieVerfassungsGeltung.GESPERRT: 0,
    KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST: 1,
    KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KosmologieVerfassungsNorm:
    kosmologie_verfassung_id: str
    kosmologie_verfassungs_typ: KosmologieVerfassungsTyp
    prozedur: KosmologieVerfassungsProzedur
    geltung: KosmologieVerfassungsGeltung
    kosmologie_verfassungs_weight: float
    kosmologie_verfassungs_tier: int
    canonical: bool
    kosmologie_verfassungs_ids: tuple[str, ...]
    kosmologie_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class KosmologieVerfassung:
    verfassung_id: str
    hubble_charta: HubbleCharta
    normen: tuple[KosmologieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmologie_verfassung_id for n in self.normen if n.geltung is KosmologieVerfassungsGeltung.GESPERRT)

    @property
    def kosmologieverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmologie_verfassung_id for n in self.normen if n.geltung is KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmologie_verfassung_id for n in self.normen if n.geltung is KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KosmologieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-kosmologieverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-kosmologieverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kosmologie_verfassung(
    hubble_charta: HubbleCharta | None = None,
    *,
    verfassung_id: str = "kosmologie-verfassung",
) -> KosmologieVerfassung:
    if hubble_charta is None:
        hubble_charta = build_hubble_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[KosmologieVerfassungsNorm] = []
    for parent_norm in hubble_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.hubble_charta_id.removeprefix(f'{hubble_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.hubble_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.hubble_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST)
        normen.append(
            KosmologieVerfassungsNorm(
                kosmologie_verfassung_id=new_id,
                kosmologie_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kosmologie_verfassungs_weight=new_weight,
                kosmologie_verfassungs_tier=new_tier,
                canonical=is_canonical,
                kosmologie_verfassungs_ids=parent_norm.hubble_ids + (new_id,),
                kosmologie_verfassungs_tags=parent_norm.hubble_tags + (f"kosmologie-verfassung:{new_geltung.value}",),
            )
        )
    return KosmologieVerfassung(
        verfassung_id=verfassung_id,
        hubble_charta=hubble_charta,
        normen=tuple(normen),
    )
