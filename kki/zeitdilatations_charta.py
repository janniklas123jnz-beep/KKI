"""#279 – ZeitdilatationsCharta: Zeitdilatation als Governance-Rhythmus.

Parent: ereignishorizont_norm (#278)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ereignishorizont_norm import (
    EreignishorizontGeltung,
    EreignishorizontNorm,
    build_ereignishorizont_norm,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ZeitdilatationsTyp(Enum):
    SCHUTZ_ZEITDILATATION = "schutz-zeitdilatation"
    ORDNUNGS_ZEITDILATATION = "ordnungs-zeitdilatation"
    SOUVERAENITAETS_ZEITDILATATION = "souveraenitaets-zeitdilatation"


class ZeitdilatationsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ZeitdilatationsGeltung(Enum):
    GESPERRT = "gesperrt"
    ZEITDILATATIERT = "zeitdilatatiert"
    GRUNDLEGEND_ZEITDILATATIERT = "grundlegend-zeitdilatatiert"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[EreignishorizontGeltung, ZeitdilatationsGeltung] = {
    EreignishorizontGeltung.GESPERRT: ZeitdilatationsGeltung.GESPERRT,
    EreignishorizontGeltung.HORIZONTIERT: ZeitdilatationsGeltung.ZEITDILATATIERT,
    EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT: ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT,
}

_TYP_MAP: dict[EreignishorizontGeltung, ZeitdilatationsTyp] = {
    EreignishorizontGeltung.GESPERRT: ZeitdilatationsTyp.SCHUTZ_ZEITDILATATION,
    EreignishorizontGeltung.HORIZONTIERT: ZeitdilatationsTyp.ORDNUNGS_ZEITDILATATION,
    EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT: ZeitdilatationsTyp.SOUVERAENITAETS_ZEITDILATATION,
}

_PROZEDUR_MAP: dict[EreignishorizontGeltung, ZeitdilatationsProzedur] = {
    EreignishorizontGeltung.GESPERRT: ZeitdilatationsProzedur.NOTPROZEDUR,
    EreignishorizontGeltung.HORIZONTIERT: ZeitdilatationsProzedur.REGELPROTOKOLL,
    EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT: ZeitdilatationsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[EreignishorizontGeltung, float] = {
    EreignishorizontGeltung.GESPERRT: 0.0,
    EreignishorizontGeltung.HORIZONTIERT: 0.04,
    EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT: 0.08,
}

_TIER_BONUS: dict[EreignishorizontGeltung, int] = {
    EreignishorizontGeltung.GESPERRT: 0,
    EreignishorizontGeltung.HORIZONTIERT: 1,
    EreignishorizontGeltung.GRUNDLEGEND_HORIZONTIERT: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZeitdilatationsNorm:
    zeitdilatations_charta_id: str
    zeitdilatations_typ: ZeitdilatationsTyp
    prozedur: ZeitdilatationsProzedur
    geltung: ZeitdilatationsGeltung
    zeitdilatations_weight: float
    zeitdilatations_tier: int
    canonical: bool
    zeitdilatations_ids: tuple[str, ...]
    zeitdilatations_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZeitdilatationsCharta:
    charta_id: str
    ereignishorizont_norm: EreignishorizontNorm
    normen: tuple[ZeitdilatationsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zeitdilatations_charta_id for n in self.normen if n.geltung is ZeitdilatationsGeltung.GESPERRT)

    @property
    def zeitdilatatiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zeitdilatations_charta_id for n in self.normen if n.geltung is ZeitdilatationsGeltung.ZEITDILATATIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zeitdilatations_charta_id for n in self.normen if n.geltung is ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is ZeitdilatationsGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is ZeitdilatationsGeltung.ZEITDILATATIERT for n in self.normen):
            status = "charta-zeitdilatatiert"
            severity = "warning"
        else:
            status = "charta-grundlegend-zeitdilatatiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_zeitdilatations_charta(
    ereignishorizont_norm: EreignishorizontNorm | None = None,
    *,
    charta_id: str = "zeitdilatations-charta",
) -> ZeitdilatationsCharta:
    if ereignishorizont_norm is None:
        ereignishorizont_norm = build_ereignishorizont_norm(norm_id=f"{charta_id}-horizont")

    normen: list[ZeitdilatationsNorm] = []
    for parent_eintrag in ereignishorizont_norm.normen:
        parent_geltung = parent_eintrag.geltung
        new_id = f"{charta_id}-{parent_eintrag.ereignishorizont_norm_id.removeprefix(f'{ereignishorizont_norm.norm_id}-')}"
        raw_weight = min(1.0, round(parent_eintrag.ereignishorizont_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_eintrag.ereignishorizont_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_eintrag.canonical and (new_geltung is ZeitdilatationsGeltung.GRUNDLEGEND_ZEITDILATATIERT)
        normen.append(
            ZeitdilatationsNorm(
                zeitdilatations_charta_id=new_id,
                zeitdilatations_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                zeitdilatations_weight=raw_weight,
                zeitdilatations_tier=new_tier,
                canonical=is_canonical,
                zeitdilatations_ids=parent_eintrag.ereignishorizont_norm_ids + (new_id,),
                zeitdilatations_tags=parent_eintrag.ereignishorizont_norm_tags + (f"zeitdilatations-charta:{new_geltung.value}",),
            )
        )

    return ZeitdilatationsCharta(
        charta_id=charta_id,
        ereignishorizont_norm=ereignishorizont_norm,
        normen=tuple(normen),
    )
