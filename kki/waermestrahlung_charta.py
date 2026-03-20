"""#289 – WaermestrahlungsCharta: Schwarzkörperstrahlung als Governance-Charta.

Parent: entropie_norm (#288)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entropie_norm import (
    EntropieNormGeltung,
    EntropieNormSatz,
    build_entropie_norm,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class WaermestrahlungsTyp(Enum):
    SCHUTZ_WAERMESTRAHLUNG = "schutz-waermestrahlung"
    ORDNUNGS_WAERMESTRAHLUNG = "ordnungs-waermestrahlung"
    SOUVERAENITAETS_WAERMESTRAHLUNG = "souveraenitaets-waermestrahlung"


class WaermestrahlungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WaermestrahlungsGeltung(Enum):
    GESPERRT = "gesperrt"
    STRAHLEND = "strahlend"
    GRUNDLEGEND_STRAHLEND = "grundlegend-strahlend"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[EntropieNormGeltung, WaermestrahlungsGeltung] = {
    EntropieNormGeltung.GESPERRT: WaermestrahlungsGeltung.GESPERRT,
    EntropieNormGeltung.ENTROPIENORMIERT: WaermestrahlungsGeltung.STRAHLEND,
    EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT: WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND,
}

_TYP_MAP: dict[EntropieNormGeltung, WaermestrahlungsTyp] = {
    EntropieNormGeltung.GESPERRT: WaermestrahlungsTyp.SCHUTZ_WAERMESTRAHLUNG,
    EntropieNormGeltung.ENTROPIENORMIERT: WaermestrahlungsTyp.ORDNUNGS_WAERMESTRAHLUNG,
    EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT: WaermestrahlungsTyp.SOUVERAENITAETS_WAERMESTRAHLUNG,
}

_PROZEDUR_MAP: dict[EntropieNormGeltung, WaermestrahlungsProzedur] = {
    EntropieNormGeltung.GESPERRT: WaermestrahlungsProzedur.NOTPROZEDUR,
    EntropieNormGeltung.ENTROPIENORMIERT: WaermestrahlungsProzedur.REGELPROTOKOLL,
    EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT: WaermestrahlungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[EntropieNormGeltung, float] = {
    EntropieNormGeltung.GESPERRT: 0.0,
    EntropieNormGeltung.ENTROPIENORMIERT: 0.04,
    EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT: 0.08,
}

_TIER_BONUS: dict[EntropieNormGeltung, int] = {
    EntropieNormGeltung.GESPERRT: 0,
    EntropieNormGeltung.ENTROPIENORMIERT: 1,
    EntropieNormGeltung.GRUNDLEGEND_ENTROPIENORMIERT: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WaermestrahlungsNorm:
    waermestrahlung_charta_id: str
    waermestrahlung_typ: WaermestrahlungsTyp
    prozedur: WaermestrahlungsProzedur
    geltung: WaermestrahlungsGeltung
    waermestrahlung_weight: float
    waermestrahlung_tier: int
    canonical: bool
    waermestrahlung_ids: tuple[str, ...]
    waermestrahlung_tags: tuple[str, ...]


@dataclass(frozen=True)
class WaermestrahlungsCharta:
    charta_id: str
    entropie_norm: EntropieNormSatz
    normen: tuple[WaermestrahlungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.waermestrahlung_charta_id for n in self.normen if n.geltung is WaermestrahlungsGeltung.GESPERRT)

    @property
    def strahlend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.waermestrahlung_charta_id for n in self.normen if n.geltung is WaermestrahlungsGeltung.STRAHLEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.waermestrahlung_charta_id for n in self.normen if n.geltung is WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND)

    @property
    def charta_signal(self):
        if any(n.geltung is WaermestrahlungsGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is WaermestrahlungsGeltung.STRAHLEND for n in self.normen):
            status = "charta-strahlend"
            severity = "warning"
        else:
            status = "charta-grundlegend-strahlend"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_waermestrahlung_charta(
    entropie_norm: EntropieNormSatz | None = None,
    *,
    charta_id: str = "waermestrahlung-charta",
) -> WaermestrahlungsCharta:
    if entropie_norm is None:
        entropie_norm = build_entropie_norm(norm_id=f"{charta_id}-norm")

    normen: list[WaermestrahlungsNorm] = []
    for parent_eintrag in entropie_norm.normen:
        parent_geltung = parent_eintrag.geltung
        new_id = f"{charta_id}-{parent_eintrag.entropie_norm_id.removeprefix(f'{entropie_norm.norm_id}-')}"
        raw_weight = min(1.0, round(parent_eintrag.entropie_norm_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_eintrag.entropie_norm_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_eintrag.canonical and (new_geltung is WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND)
        normen.append(
            WaermestrahlungsNorm(
                waermestrahlung_charta_id=new_id,
                waermestrahlung_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                waermestrahlung_weight=raw_weight,
                waermestrahlung_tier=new_tier,
                canonical=is_canonical,
                waermestrahlung_ids=parent_eintrag.entropie_norm_ids + (new_id,),
                waermestrahlung_tags=parent_eintrag.entropie_norm_tags + (f"waermestrahlung-charta:{new_geltung.value}",),
            )
        )

    return WaermestrahlungsCharta(
        charta_id=charta_id,
        entropie_norm=entropie_norm,
        normen=tuple(normen),
    )
