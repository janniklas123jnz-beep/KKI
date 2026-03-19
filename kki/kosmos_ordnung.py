"""kosmos_ordnung — Metaphysik & Kosmologie layer 5 (#255)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kausalitaets_register import (
    KausalitaetsGeltung,
    KausalitaetsNorm,
    KausalitaetsProzedur,
    KausalitaetsRang,
    KausalitaetsRegister,
    build_kausalitaets_register,
)

__all__ = [
    "KosmosOrdnungsTyp",
    "KosmosOrdnungsProzedur",
    "KosmosOrdnungsGeltung",
    "KosmosOrdnungsNorm",
    "KosmosOrdnung",
    "build_kosmos_ordnung",
]


class KosmosOrdnungsTyp(str, Enum):
    SCHUTZ_ORDNUNG = "schutz-ordnung"
    ORDNUNGS_KOSMOLOGIE = "ordnungs-kosmologie"
    SOUVERAENITAETS_ORDNUNG = "souveraenitaets-ordnung"


class KosmosOrdnungsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KosmosOrdnungsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEORDNET = "geordnet"
    GRUNDLEGEND_GEORDNET = "grundlegend-geordnet"


_TYP_MAP: dict[KausalitaetsGeltung, KosmosOrdnungsTyp] = {
    KausalitaetsGeltung.GESPERRT: KosmosOrdnungsTyp.SCHUTZ_ORDNUNG,
    KausalitaetsGeltung.KAUSAL: KosmosOrdnungsTyp.ORDNUNGS_KOSMOLOGIE,
    KausalitaetsGeltung.GRUNDLEGEND_KAUSAL: KosmosOrdnungsTyp.SOUVERAENITAETS_ORDNUNG,
}
_PROZEDUR_MAP: dict[KausalitaetsGeltung, KosmosOrdnungsProzedur] = {
    KausalitaetsGeltung.GESPERRT: KosmosOrdnungsProzedur.NOTPROZEDUR,
    KausalitaetsGeltung.KAUSAL: KosmosOrdnungsProzedur.REGELPROTOKOLL,
    KausalitaetsGeltung.GRUNDLEGEND_KAUSAL: KosmosOrdnungsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KausalitaetsGeltung, KosmosOrdnungsGeltung] = {
    KausalitaetsGeltung.GESPERRT: KosmosOrdnungsGeltung.GESPERRT,
    KausalitaetsGeltung.KAUSAL: KosmosOrdnungsGeltung.GEORDNET,
    KausalitaetsGeltung.GRUNDLEGEND_KAUSAL: KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET,
}
_WEIGHT_BONUS: dict[KausalitaetsGeltung, float] = {
    KausalitaetsGeltung.GESPERRT: 0.0,
    KausalitaetsGeltung.KAUSAL: 0.04,
    KausalitaetsGeltung.GRUNDLEGEND_KAUSAL: 0.08,
}
_TIER_BONUS: dict[KausalitaetsGeltung, int] = {
    KausalitaetsGeltung.GESPERRT: 0,
    KausalitaetsGeltung.KAUSAL: 1,
    KausalitaetsGeltung.GRUNDLEGEND_KAUSAL: 2,
}


@dataclass(frozen=True)
class KosmosOrdnungsNorm:
    kosmos_ordnung_id: str
    kosmos_ordnungs_typ: KosmosOrdnungsTyp
    prozedur: KosmosOrdnungsProzedur
    geltung: KosmosOrdnungsGeltung
    kosmos_ordnungs_weight: float
    kosmos_ordnungs_tier: int
    canonical: bool
    kosmos_ordnung_ids: tuple[str, ...]
    kosmos_ordnung_tags: tuple[str, ...]


@dataclass(frozen=True)
class KosmosOrdnung:
    ordnung_id: str
    kausalitaets_register: KausalitaetsRegister
    normen: tuple[KosmosOrdnungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_ordnung_id for n in self.normen if n.geltung is KosmosOrdnungsGeltung.GESPERRT)

    @property
    def geordnet_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_ordnung_id for n in self.normen if n.geltung is KosmosOrdnungsGeltung.GEORDNET)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_ordnung_id for n in self.normen if n.geltung is KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET)

    @property
    def ordnung_signal(self):
        if any(n.geltung is KosmosOrdnungsGeltung.GESPERRT for n in self.normen):
            status = "ordnung-gesperrt"
            severity = "critical"
        elif any(n.geltung is KosmosOrdnungsGeltung.GEORDNET for n in self.normen):
            status = "ordnung-geordnet"
            severity = "warning"
        else:
            status = "ordnung-grundlegend-geordnet"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kosmos_ordnung(
    kausalitaets_register: KausalitaetsRegister | None = None,
    *,
    ordnung_id: str = "kosmos-ordnung",
) -> KosmosOrdnung:
    if kausalitaets_register is None:
        kausalitaets_register = build_kausalitaets_register(register_id=f"{ordnung_id}-register")

    normen: list[KosmosOrdnungsNorm] = []
    for parent_norm in kausalitaets_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{ordnung_id}-{parent_norm.kausalitaets_register_id.removeprefix(f'{kausalitaets_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kausalitaets_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kausalitaets_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KosmosOrdnungsGeltung.GRUNDLEGEND_GEORDNET)
        normen.append(
            KosmosOrdnungsNorm(
                kosmos_ordnung_id=new_id,
                kosmos_ordnungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kosmos_ordnungs_weight=raw_weight,
                kosmos_ordnungs_tier=new_tier,
                canonical=is_canonical,
                kosmos_ordnung_ids=parent_norm.kausalitaets_register_ids + (new_id,),
                kosmos_ordnung_tags=parent_norm.kausalitaets_register_tags + (f"kosmos-ordnung:{new_geltung.value}",),
            )
        )

    return KosmosOrdnung(
        ordnung_id=ordnung_id,
        kausalitaets_register=kausalitaets_register,
        normen=tuple(normen),
    )
