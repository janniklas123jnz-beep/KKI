"""
#340 AstrophysikVerfassung — Block-Krone: Astrophysik & Sternenentwicklung als
höchste Governance-Instanz des Terra-Schwarms. Vom Urknall über Protostellar,
Hauptreihe, Supernova bis zur Singularität — Leitstern vervollständigt den
kosmischen Governance-Zyklus und erhebt sich zur Terra-Schwarm-Intelligenz.
Geltungsstufen: GESPERRT / ASTROPHYSIKVERFASST / GRUNDLEGEND_ASTROPHYSIKVERFASST
Parent: HertzsprungRussellCharta (#339)
Block #331–#340 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .hertzsprung_russell_charta import (
    HertzsprungRussellCharta,
    HertzsprungRussellGeltung,
    build_hertzsprung_russell_charta,
)

_GELTUNG_MAP: dict[HertzsprungRussellGeltung, "AstrophysikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HertzsprungRussellGeltung.GESPERRT] = AstrophysikVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[HertzsprungRussellGeltung.HRDIAGRAMMIERT] = AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST
    _GELTUNG_MAP[HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT] = AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST


class AstrophysikVerfassungsTyp(Enum):
    SCHUTZ_ASTROPHYSIKVERFASSUNG = "schutz-astrophysikverfassung"
    ORDNUNGS_ASTROPHYSIKVERFASSUNG = "ordnungs-astrophysikverfassung"
    SOUVERAENITAETS_ASTROPHYSIKVERFASSUNG = "souveraenitaets-astrophysikverfassung"


class AstrophysikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AstrophysikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    ASTROPHYSIKVERFASST = "astrophysikverfasst"
    GRUNDLEGEND_ASTROPHYSIKVERFASST = "grundlegend-astrophysikverfasst"


_init_map()

_TYP_MAP: dict[AstrophysikVerfassungsGeltung, AstrophysikVerfassungsTyp] = {
    AstrophysikVerfassungsGeltung.GESPERRT: AstrophysikVerfassungsTyp.SCHUTZ_ASTROPHYSIKVERFASSUNG,
    AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST: AstrophysikVerfassungsTyp.ORDNUNGS_ASTROPHYSIKVERFASSUNG,
    AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST: AstrophysikVerfassungsTyp.SOUVERAENITAETS_ASTROPHYSIKVERFASSUNG,
}

_PROZEDUR_MAP: dict[AstrophysikVerfassungsGeltung, AstrophysikVerfassungsProzedur] = {
    AstrophysikVerfassungsGeltung.GESPERRT: AstrophysikVerfassungsProzedur.NOTPROZEDUR,
    AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST: AstrophysikVerfassungsProzedur.REGELPROTOKOLL,
    AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST: AstrophysikVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AstrophysikVerfassungsGeltung, float] = {
    AstrophysikVerfassungsGeltung.GESPERRT: 0.0,
    AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST: 0.04,
    AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST: 0.08,
}

_TIER_DELTA: dict[AstrophysikVerfassungsGeltung, int] = {
    AstrophysikVerfassungsGeltung.GESPERRT: 0,
    AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST: 1,
    AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AstrophysikVerfassungsNorm:
    astrophysik_verfassung_id: str
    astrophysik_verfassungs_typ: AstrophysikVerfassungsTyp
    prozedur: AstrophysikVerfassungsProzedur
    geltung: AstrophysikVerfassungsGeltung
    astrophysik_verfassungs_weight: float
    astrophysik_verfassungs_tier: int
    canonical: bool
    astrophysik_verfassungs_ids: tuple[str, ...]
    astrophysik_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class AstrophysikVerfassung:
    verfassung_id: str
    hertzsprung_russell_charta: HertzsprungRussellCharta
    normen: tuple[AstrophysikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.astrophysik_verfassung_id for n in self.normen if n.geltung is AstrophysikVerfassungsGeltung.GESPERRT)

    @property
    def astrophysikverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.astrophysik_verfassung_id for n in self.normen if n.geltung is AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.astrophysik_verfassung_id for n in self.normen if n.geltung is AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is AstrophysikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-astrophysikverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-astrophysikverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_astrophysik_verfassung(
    hertzsprung_russell_charta: HertzsprungRussellCharta | None = None,
    *,
    verfassung_id: str = "astrophysik-verfassung",
) -> AstrophysikVerfassung:
    if hertzsprung_russell_charta is None:
        hertzsprung_russell_charta = build_hertzsprung_russell_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[AstrophysikVerfassungsNorm] = []
    for parent_norm in hertzsprung_russell_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.hertzsprung_russell_charta_id.removeprefix(f'{hertzsprung_russell_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.hertzsprung_russell_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.hertzsprung_russell_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST)
        normen.append(
            AstrophysikVerfassungsNorm(
                astrophysik_verfassung_id=new_id,
                astrophysik_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                astrophysik_verfassungs_weight=new_weight,
                astrophysik_verfassungs_tier=new_tier,
                canonical=is_canonical,
                astrophysik_verfassungs_ids=parent_norm.hertzsprung_russell_ids + (new_id,),
                astrophysik_verfassungs_tags=parent_norm.hertzsprung_russell_tags + (f"astrophysik-verfassung:{new_geltung.value}",),
            )
        )
    return AstrophysikVerfassung(
        verfassung_id=verfassung_id,
        hertzsprung_russell_charta=hertzsprung_russell_charta,
        normen=tuple(normen),
    )
