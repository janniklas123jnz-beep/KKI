"""#280 – RelativitaetsVerfassung: Block-Krone Relativität & Raumzeit.

Parent: zeitdilatations_charta (#279)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zeitdilatations_charta import (
    ZeitdilatationsGeltung,
    ZeitdilatationsCharta,
    build_zeitdilatations_charta,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RelativitaetsTyp(Enum):
    SCHUTZ_RELATIVITAET = "schutz-relativitaet"
    ORDNUNGS_RELATIVITAET = "ordnungs-relativitaet"
    SOUVERAENITAETS_RELATIVITAET = "souveraenitaets-relativitaet"


class RelativitaetsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RelativitaetsGeltung(Enum):
    GESPERRT = "gesperrt"
    RELATIVVERFASST = "relativverfasst"
    GRUNDLEGEND_RELATIVVERFASST = "grundlegend-relativverfasst"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[ZeitdilatationsGeltung, RelativitaetsGeltung] = {
    ZeitdilatationsGeltung.GESPERRT: RelativitaetsGeltung.GESPERRT,
    ZeitdilatationsGeltung.ZEITDILATATIERT: RelativitaetsGeltung.RELATIVVERFASST,
    ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT: RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST,
}

_TYP_MAP: dict[ZeitdilatationsGeltung, RelativitaetsTyp] = {
    ZeitdilatationsGeltung.GESPERRT: RelativitaetsTyp.SCHUTZ_RELATIVITAET,
    ZeitdilatationsGeltung.ZEITDILATATIERT: RelativitaetsTyp.ORDNUNGS_RELATIVITAET,
    ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT: RelativitaetsTyp.SOUVERAENITAETS_RELATIVITAET,
}

_PROZEDUR_MAP: dict[ZeitdilatationsGeltung, RelativitaetsProzedur] = {
    ZeitdilatationsGeltung.GESPERRT: RelativitaetsProzedur.NOTPROZEDUR,
    ZeitdilatationsGeltung.ZEITDILATATIERT: RelativitaetsProzedur.REGELPROTOKOLL,
    ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT: RelativitaetsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[ZeitdilatationsGeltung, float] = {
    ZeitdilatationsGeltung.GESPERRT: 0.0,
    ZeitdilatationsGeltung.ZEITDILATATIERT: 0.04,
    ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT: 0.08,
}

_TIER_BONUS: dict[ZeitdilatationsGeltung, int] = {
    ZeitdilatationsGeltung.GESPERRT: 0,
    ZeitdilatationsGeltung.ZEITDILATATIERT: 1,
    ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RelativitaetsNorm:
    relativitaets_verfassung_id: str
    relativitaets_typ: RelativitaetsTyp
    prozedur: RelativitaetsProzedur
    geltung: RelativitaetsGeltung
    relativitaets_weight: float
    relativitaets_tier: int
    canonical: bool
    relativitaets_ids: tuple[str, ...]
    relativitaets_tags: tuple[str, ...]


@dataclass(frozen=True)
class RelativitaetsVerfassung:
    verfassung_id: str
    zeitdilatations_charta: ZeitdilatationsCharta
    normen: tuple[RelativitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.relativitaets_verfassung_id for n in self.normen if n.geltung is RelativitaetsGeltung.GESPERRT)

    @property
    def relativverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.relativitaets_verfassung_id for n in self.normen if n.geltung is RelativitaetsGeltung.RELATIVVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.relativitaets_verfassung_id for n in self.normen if n.geltung is RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is RelativitaetsGeltung.GESPERRT for n in self.normen):
            status = "verfassung-gesperrt"
            severity = "critical"
        elif any(n.geltung is RelativitaetsGeltung.RELATIVVERFASST for n in self.normen):
            status = "verfassung-relativverfasst"
            severity = "warning"
        else:
            status = "verfassung-grundlegend-relativverfasst"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_relativitaets_verfassung(
    zeitdilatations_charta: ZeitdilatationsCharta | None = None,
    *,
    verfassung_id: str = "relativitaets-verfassung",
) -> RelativitaetsVerfassung:
    if zeitdilatations_charta is None:
        zeitdilatations_charta = build_zeitdilatations_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[RelativitaetsNorm] = []
    for parent_norm in zeitdilatations_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{verfassung_id}-{parent_norm.zeitdilatations_charta_id.removeprefix(f'{zeitdilatations_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.zeitdilatations_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.zeitdilatations_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST)
        normen.append(
            RelativitaetsNorm(
                relativitaets_verfassung_id=new_id,
                relativitaets_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                relativitaets_weight=raw_weight,
                relativitaets_tier=new_tier,
                canonical=is_canonical,
                relativitaets_ids=parent_norm.zeitdilatations_ids + (new_id,),
                relativitaets_tags=parent_norm.zeitdilatations_tags + (f"relativitaets-verfassung:{new_geltung.value}",),
            )
        )

    return RelativitaetsVerfassung(
        verfassung_id=verfassung_id,
        zeitdilatations_charta=zeitdilatations_charta,
        normen=tuple(normen),
    )
