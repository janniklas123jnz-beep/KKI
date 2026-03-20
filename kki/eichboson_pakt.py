"""
#315 EichbosonPakt — Eichbosonen (W/Z/γ) als Kraftmediatoren-Pakt.
Geltungsstufen: GESPERRT / EICHBOSONAL / GRUNDLEGEND_EICHBOSONAL
Parent: GluonKodex (#314)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gluon_kodex import GluonGeltung, GluonKodex, build_gluon_kodex

_GELTUNG_MAP: dict[GluonGeltung, "EichbosonGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GluonGeltung.GESPERRT] = EichbosonGeltung.GESPERRT
    _GELTUNG_MAP[GluonGeltung.GLUONISCH] = EichbosonGeltung.EICHBOSONAL
    _GELTUNG_MAP[GluonGeltung.GRUNDLEGEND_GLUONISCH] = EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL


class EichbosonTyp(Enum):
    SCHUTZ_EICHBOSON = "schutz-eichboson"
    ORDNUNGS_EICHBOSON = "ordnungs-eichboson"
    SOUVERAENITAETS_EICHBOSON = "souveraenitaets-eichboson"


class EichbosonProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EichbosonGeltung(Enum):
    GESPERRT = "gesperrt"
    EICHBOSONAL = "eichbosonal"
    GRUNDLEGEND_EICHBOSONAL = "grundlegend-eichbosonal"


_init_map()

_TYP_MAP: dict[EichbosonGeltung, EichbosonTyp] = {
    EichbosonGeltung.GESPERRT: EichbosonTyp.SCHUTZ_EICHBOSON,
    EichbosonGeltung.EICHBOSONAL: EichbosonTyp.ORDNUNGS_EICHBOSON,
    EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL: EichbosonTyp.SOUVERAENITAETS_EICHBOSON,
}

_PROZEDUR_MAP: dict[EichbosonGeltung, EichbosonProzedur] = {
    EichbosonGeltung.GESPERRT: EichbosonProzedur.NOTPROZEDUR,
    EichbosonGeltung.EICHBOSONAL: EichbosonProzedur.REGELPROTOKOLL,
    EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL: EichbosonProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EichbosonGeltung, float] = {
    EichbosonGeltung.GESPERRT: 0.0,
    EichbosonGeltung.EICHBOSONAL: 0.04,
    EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL: 0.08,
}

_TIER_DELTA: dict[EichbosonGeltung, int] = {
    EichbosonGeltung.GESPERRT: 0,
    EichbosonGeltung.EICHBOSONAL: 1,
    EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL: 2,
}


@dataclass(frozen=True)
class EichbosonNorm:
    eichboson_pakt_id: str
    eichboson_typ: EichbosonTyp
    prozedur: EichbosonProzedur
    geltung: EichbosonGeltung
    eichboson_weight: float
    eichboson_tier: int
    canonical: bool
    eichboson_ids: tuple[str, ...]
    eichboson_tags: tuple[str, ...]


@dataclass(frozen=True)
class EichbosonPakt:
    pakt_id: str
    gluon_kodex: GluonKodex
    normen: tuple[EichbosonNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.eichboson_pakt_id for n in self.normen if n.geltung is EichbosonGeltung.GESPERRT)

    @property
    def eichbosonal_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.eichboson_pakt_id for n in self.normen if n.geltung is EichbosonGeltung.EICHBOSONAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.eichboson_pakt_id for n in self.normen if n.geltung is EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL)

    @property
    def pakt_signal(self):
        if any(n.geltung is EichbosonGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is EichbosonGeltung.EICHBOSONAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-eichbosonal")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-eichbosonal")


def build_eichboson_pakt(
    gluon_kodex: GluonKodex | None = None,
    *,
    pakt_id: str = "eichboson-pakt",
) -> EichbosonPakt:
    if gluon_kodex is None:
        gluon_kodex = build_gluon_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[EichbosonNorm] = []
    for parent_norm in gluon_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.gluon_kodex_id.removeprefix(f'{gluon_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.gluon_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gluon_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL)
        normen.append(
            EichbosonNorm(
                eichboson_pakt_id=new_id,
                eichboson_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                eichboson_weight=new_weight,
                eichboson_tier=new_tier,
                canonical=is_canonical,
                eichboson_ids=parent_norm.gluon_ids + (new_id,),
                eichboson_tags=parent_norm.gluon_tags + (f"eichboson-pakt:{new_geltung.value}",),
            )
        )
    return EichbosonPakt(
        pakt_id=pakt_id,
        gluon_kodex=gluon_kodex,
        normen=tuple(normen),
    )
