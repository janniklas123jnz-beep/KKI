"""zivilisations_pakt — Zivilisation & Transzendenz layer 4 (#244)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .erbe_register import (
    ErbeGeltung,
    ErbeKlasse,
    ErbeNorm,
    ErbeProzedur,
    ErbeRegister,
    build_erbe_register,
)

__all__ = [
    "ZivilisationsTyp",
    "ZivilisationsProzedur",
    "ZivilisationsGeltung",
    "ZivilisationsNorm",
    "ZivilisationsPakt",
    "build_zivilisations_pakt",
]


class ZivilisationsTyp(str, Enum):
    SCHUTZ_ZIVILISATION = "schutz-zivilisation"
    ORDNUNGS_ZIVILISATION = "ordnungs-zivilisation"
    SOUVERAENITAETS_ZIVILISATION = "souveraenitaets-zivilisation"


class ZivilisationsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ZivilisationsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GESCHLOSSEN = "geschlossen"
    GRUNDLEGEND_GESCHLOSSEN = "grundlegend-geschlossen"


_TYP_MAP: dict[ErbeGeltung, ZivilisationsTyp] = {
    ErbeGeltung.GESPERRT: ZivilisationsTyp.SCHUTZ_ZIVILISATION,
    ErbeGeltung.UEBERLIEFERT: ZivilisationsTyp.ORDNUNGS_ZIVILISATION,
    ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT: ZivilisationsTyp.SOUVERAENITAETS_ZIVILISATION,
}
_PROZEDUR_MAP: dict[ErbeGeltung, ZivilisationsProzedur] = {
    ErbeGeltung.GESPERRT: ZivilisationsProzedur.NOTPROZEDUR,
    ErbeGeltung.UEBERLIEFERT: ZivilisationsProzedur.REGELPROTOKOLL,
    ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT: ZivilisationsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[ErbeGeltung, ZivilisationsGeltung] = {
    ErbeGeltung.GESPERRT: ZivilisationsGeltung.GESPERRT,
    ErbeGeltung.UEBERLIEFERT: ZivilisationsGeltung.GESCHLOSSEN,
    ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT: ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN,
}
_WEIGHT_BONUS: dict[ErbeGeltung, float] = {
    ErbeGeltung.GESPERRT: 0.0,
    ErbeGeltung.UEBERLIEFERT: 0.04,
    ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT: 0.08,
}
_TIER_BONUS: dict[ErbeGeltung, int] = {
    ErbeGeltung.GESPERRT: 0,
    ErbeGeltung.UEBERLIEFERT: 1,
    ErbeGeltung.GRUNDLEGEND_UEBERLIEFERT: 2,
}


@dataclass(frozen=True)
class ZivilisationsNorm:
    zivilisations_pakt_id: str
    zivilisations_typ: ZivilisationsTyp
    prozedur: ZivilisationsProzedur
    geltung: ZivilisationsGeltung
    zivilisations_weight: float
    zivilisations_tier: int
    canonical: bool
    zivilisations_pakt_ids: tuple[str, ...]
    zivilisations_pakt_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZivilisationsPakt:
    pakt_id: str
    erbe_register: ErbeRegister
    normen: tuple[ZivilisationsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilisations_pakt_id for n in self.normen if n.geltung is ZivilisationsGeltung.GESPERRT)

    @property
    def geschlossen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilisations_pakt_id for n in self.normen if n.geltung is ZivilisationsGeltung.GESCHLOSSEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilisations_pakt_id for n in self.normen if n.geltung is ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN)

    @property
    def pakt_signal(self):
        if any(n.geltung is ZivilisationsGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is ZivilisationsGeltung.GESCHLOSSEN for n in self.normen):
            status = "pakt-geschlossen"
            severity = "warning"
        else:
            status = "pakt-grundlegend-geschlossen"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_zivilisations_pakt(
    erbe_register: ErbeRegister | None = None,
    *,
    pakt_id: str = "zivilisations-pakt",
) -> ZivilisationsPakt:
    if erbe_register is None:
        erbe_register = build_erbe_register(register_id=f"{pakt_id}-register")

    normen: list[ZivilisationsNorm] = []
    for parent_norm in erbe_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.erbe_register_id.removeprefix(f'{erbe_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.erbe_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.erbe_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN)
        normen.append(
            ZivilisationsNorm(
                zivilisations_pakt_id=new_id,
                zivilisations_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                zivilisations_weight=raw_weight,
                zivilisations_tier=new_tier,
                canonical=is_canonical,
                zivilisations_pakt_ids=parent_norm.erbe_register_ids + (new_id,),
                zivilisations_pakt_tags=parent_norm.erbe_register_tags + (f"zivilisations-pakt:{new_geltung.value}",),
            )
        )

    return ZivilisationsPakt(
        pakt_id=pakt_id,
        erbe_register=erbe_register,
        normen=tuple(normen),
    )
