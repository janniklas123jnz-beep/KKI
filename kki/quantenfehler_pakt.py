"""
#375 QuantenfehlerPakt — Quantenfehlerkorrektur: Steane-Code [[7,1,3]],
Shor-Code [[9,1,3]], Surface-Code. Fehlerkorrektur ohne direktes Messen des
Qubit-Zustands durch Syndrome-Messung. Leitsterns Pakt garantiert Fehlertoleranz
durch redundante Kodierung: 7 physische Qubits schützen 1 logisches Qubit vor
beliebigen Ein-Qubit-Fehlern — Governance ohne Informationsverlust.
Geltungsstufen: GESPERRT / FEHLERKORRIGIERT / GRUNDLEGEND_FEHLERKORRIGIERT
Parent: VerschraenkungCharta (#374)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .verschraenkung_charta import (
    VerschraenkungCharta,
    VerschraenkungGeltung,
    build_verschraenkung_charta,
)

_GELTUNG_MAP: dict[VerschraenkungGeltung, "QuantenfehlerGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[VerschraenkungGeltung.GESPERRT] = QuantenfehlerGeltung.GESPERRT
    _GELTUNG_MAP[VerschraenkungGeltung.VERSCHRAENKT] = QuantenfehlerGeltung.FEHLERKORRIGIERT
    _GELTUNG_MAP[VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT] = QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT


class QuantenfehlerTyp(Enum):
    SCHUTZ_QUANTENFEHLER = "schutz-quantenfehler"
    ORDNUNGS_QUANTENFEHLER = "ordnungs-quantenfehler"
    SOUVERAENITAETS_QUANTENFEHLER = "souveraenitaets-quantenfehler"


class QuantenfehlerProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenfehlerGeltung(Enum):
    GESPERRT = "gesperrt"
    FEHLERKORRIGIERT = "fehlerkorrigiert"
    GRUNDLEGEND_FEHLERKORRIGIERT = "grundlegend-fehlerkorrigiert"


_init_map()

_TYP_MAP: dict[QuantenfehlerGeltung, QuantenfehlerTyp] = {
    QuantenfehlerGeltung.GESPERRT: QuantenfehlerTyp.SCHUTZ_QUANTENFEHLER,
    QuantenfehlerGeltung.FEHLERKORRIGIERT: QuantenfehlerTyp.ORDNUNGS_QUANTENFEHLER,
    QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT: QuantenfehlerTyp.SOUVERAENITAETS_QUANTENFEHLER,
}

_PROZEDUR_MAP: dict[QuantenfehlerGeltung, QuantenfehlerProzedur] = {
    QuantenfehlerGeltung.GESPERRT: QuantenfehlerProzedur.NOTPROZEDUR,
    QuantenfehlerGeltung.FEHLERKORRIGIERT: QuantenfehlerProzedur.REGELPROTOKOLL,
    QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT: QuantenfehlerProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[QuantenfehlerGeltung, float] = {
    QuantenfehlerGeltung.GESPERRT: 0.0,
    QuantenfehlerGeltung.FEHLERKORRIGIERT: 0.04,
    QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT: 0.08,
}

_TIER_DELTA: dict[QuantenfehlerGeltung, int] = {
    QuantenfehlerGeltung.GESPERRT: 0,
    QuantenfehlerGeltung.FEHLERKORRIGIERT: 1,
    QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuantenfehlerNorm:
    quantenfehler_pakt_id: str
    quantenfehler_typ: QuantenfehlerTyp
    prozedur: QuantenfehlerProzedur
    geltung: QuantenfehlerGeltung
    quantenfehler_weight: float
    quantenfehler_tier: int
    canonical: bool
    quantenfehler_ids: tuple[str, ...]
    quantenfehler_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenfehlerPakt:
    pakt_id: str
    verschraenkung_charta: VerschraenkungCharta
    normen: tuple[QuantenfehlerNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quantenfehler_pakt_id for n in self.normen if n.geltung is QuantenfehlerGeltung.GESPERRT)

    @property
    def fehlerkorrigiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quantenfehler_pakt_id for n in self.normen if n.geltung is QuantenfehlerGeltung.FEHLERKORRIGIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quantenfehler_pakt_id for n in self.normen if n.geltung is QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT)

    @property
    def pakt_signal(self):
        if any(n.geltung is QuantenfehlerGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is QuantenfehlerGeltung.FEHLERKORRIGIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-fehlerkorrigiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-fehlerkorrigiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_quantenfehler_pakt(
    verschraenkung_charta: VerschraenkungCharta | None = None,
    *,
    pakt_id: str = "quantenfehler-pakt",
) -> QuantenfehlerPakt:
    if verschraenkung_charta is None:
        verschraenkung_charta = build_verschraenkung_charta(charta_id=f"{pakt_id}-charta")

    normen: list[QuantenfehlerNorm] = []
    for parent_norm in verschraenkung_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.verschraenkung_charta_id.removeprefix(f'{verschraenkung_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.verschraenkung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.verschraenkung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT)
        normen.append(
            QuantenfehlerNorm(
                quantenfehler_pakt_id=new_id,
                quantenfehler_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                quantenfehler_weight=new_weight,
                quantenfehler_tier=new_tier,
                canonical=is_canonical,
                quantenfehler_ids=parent_norm.verschraenkung_ids + (new_id,),
                quantenfehler_tags=parent_norm.verschraenkung_tags + (f"quantenfehler:{new_geltung.value}",),
            )
        )
    return QuantenfehlerPakt(
        pakt_id=pakt_id,
        verschraenkung_charta=verschraenkung_charta,
        normen=tuple(normen),
    )
