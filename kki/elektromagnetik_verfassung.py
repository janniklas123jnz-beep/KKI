"""#300 – ElektromagnetikVerfassung: Block-Krone Elektromagnetismus & Licht.

Parent: photoeffekt_charta (#299)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .photoeffekt_charta import (
    PhotoeffektGeltung,
    PhotoeffektCharta,
    build_photoeffekt_charta,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ElektroverfassungsTyp(Enum):
    SCHUTZ_ELEKTROVERFASSUNG = "schutz-elektroverfassung"
    ORDNUNGS_ELEKTROVERFASSUNG = "ordnungs-elektroverfassung"
    SOUVERAENITAETS_ELEKTROVERFASSUNG = "souveraenitaets-elektroverfassung"


class ElektroverfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ElektroverfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    ELEKTROVERFASST = "elektroverfasst"
    GRUNDLEGEND_ELEKTROVERFASST = "grundlegend-elektroverfasst"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[PhotoeffektGeltung, ElektroverfassungsGeltung] = {
    PhotoeffektGeltung.GESPERRT: ElektroverfassungsGeltung.GESPERRT,
    PhotoeffektGeltung.PHOTOEFFEKTIV: ElektroverfassungsGeltung.ELEKTROVERFASST,
    PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV: ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST,
}

_TYP_MAP: dict[PhotoeffektGeltung, ElektroverfassungsTyp] = {
    PhotoeffektGeltung.GESPERRT: ElektroverfassungsTyp.SCHUTZ_ELEKTROVERFASSUNG,
    PhotoeffektGeltung.PHOTOEFFEKTIV: ElektroverfassungsTyp.ORDNUNGS_ELEKTROVERFASSUNG,
    PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV: ElektroverfassungsTyp.SOUVERAENITAETS_ELEKTROVERFASSUNG,
}

_PROZEDUR_MAP: dict[PhotoeffektGeltung, ElektroverfassungsProzedur] = {
    PhotoeffektGeltung.GESPERRT: ElektroverfassungsProzedur.NOTPROZEDUR,
    PhotoeffektGeltung.PHOTOEFFEKTIV: ElektroverfassungsProzedur.REGELPROTOKOLL,
    PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV: ElektroverfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[PhotoeffektGeltung, float] = {
    PhotoeffektGeltung.GESPERRT: 0.0,
    PhotoeffektGeltung.PHOTOEFFEKTIV: 0.04,
    PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV: 0.08,
}

_TIER_BONUS: dict[PhotoeffektGeltung, int] = {
    PhotoeffektGeltung.GESPERRT: 0,
    PhotoeffektGeltung.PHOTOEFFEKTIV: 1,
    PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ElektroverfassungsNorm:
    elektromagnetik_verfassung_id: str
    elektroverfassungs_typ: ElektroverfassungsTyp
    prozedur: ElektroverfassungsProzedur
    geltung: ElektroverfassungsGeltung
    elektroverfassungs_weight: float
    elektroverfassungs_tier: int
    canonical: bool
    elektroverfassungs_ids: tuple[str, ...]
    elektroverfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class ElektromagnetikVerfassung:
    verfassung_id: str
    photoeffekt_charta: PhotoeffektCharta
    normen: tuple[ElektroverfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.elektromagnetik_verfassung_id for n in self.normen if n.geltung is ElektroverfassungsGeltung.GESPERRT)

    @property
    def elektroverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.elektromagnetik_verfassung_id for n in self.normen if n.geltung is ElektroverfassungsGeltung.ELEKTROVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.elektromagnetik_verfassung_id for n in self.normen if n.geltung is ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is ElektroverfassungsGeltung.GESPERRT for n in self.normen):
            status = "verfassung-gesperrt"
            severity = "critical"
        elif any(n.geltung is ElektroverfassungsGeltung.ELEKTROVERFASST for n in self.normen):
            status = "verfassung-elektroverfasst"
            severity = "warning"
        else:
            status = "verfassung-grundlegend-elektroverfasst"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_elektromagnetik_verfassung(
    photoeffekt_charta: PhotoeffektCharta | None = None,
    *,
    verfassung_id: str = "elektromagnetik-verfassung",
) -> ElektromagnetikVerfassung:
    if photoeffekt_charta is None:
        photoeffekt_charta = build_photoeffekt_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[ElektroverfassungsNorm] = []
    for parent_norm in photoeffekt_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{verfassung_id}-{parent_norm.photoeffekt_charta_id.removeprefix(f'{photoeffekt_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.photoeffekt_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.photoeffekt_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST)
        normen.append(
            ElektroverfassungsNorm(
                elektromagnetik_verfassung_id=new_id,
                elektroverfassungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                elektroverfassungs_weight=raw_weight,
                elektroverfassungs_tier=new_tier,
                canonical=is_canonical,
                elektroverfassungs_ids=parent_norm.photoeffekt_ids + (new_id,),
                elektroverfassungs_tags=parent_norm.photoeffekt_tags + (f"elektromagnetik-verfassung:{new_geltung.value}",),
            )
        )

    return ElektromagnetikVerfassung(
        verfassung_id=verfassung_id,
        photoeffekt_charta=photoeffekt_charta,
        normen=tuple(normen),
    )
