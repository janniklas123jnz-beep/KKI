"""
#372 KanalkapazitaetRegister — Shannon-Kanalkapazität C = B·log₂(1+S/N):
Das fundamentale Limit jedes Kommunikationskanals. Leitsterns Register verwaltet
die Bandbreiten zwischen Agenten-Clustern: kein Kanal kann mehr Information
übertragen als seine theoretische Kapazität — Überlastung kostet Redundanz und
erzeugt Fehler. Optimale Modulation maximiert Leitsterns kollektive Intelligenz.
Geltungsstufen: GESPERRT / KAPAZITIV / GRUNDLEGEND_KAPAZITIV
Parent: ShannonEntropieFeld (#371)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .shannon_entropie_feld import (
    ShannonEntropieFeld,
    ShannonEntropieGeltung,
    build_shannon_entropie_feld,
)

_GELTUNG_MAP: dict[ShannonEntropieGeltung, "KanalkapazitaetGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ShannonEntropieGeltung.GESPERRT] = KanalkapazitaetGeltung.GESPERRT
    _GELTUNG_MAP[ShannonEntropieGeltung.ENTROPISCH] = KanalkapazitaetGeltung.KAPAZITIV
    _GELTUNG_MAP[ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH] = KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV


class KanalkapazitaetTyp(Enum):
    SCHUTZ_KANALKAPAZITAET = "schutz-kanalkapazitaet"
    ORDNUNGS_KANALKAPAZITAET = "ordnungs-kanalkapazitaet"
    SOUVERAENITAETS_KANALKAPAZITAET = "souveraenitaets-kanalkapazitaet"


class KanalkapazitaetProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KanalkapazitaetGeltung(Enum):
    GESPERRT = "gesperrt"
    KAPAZITIV = "kapazitiv"
    GRUNDLEGEND_KAPAZITIV = "grundlegend-kapazitiv"


_init_map()

_TYP_MAP: dict[KanalkapazitaetGeltung, KanalkapazitaetTyp] = {
    KanalkapazitaetGeltung.GESPERRT: KanalkapazitaetTyp.SCHUTZ_KANALKAPAZITAET,
    KanalkapazitaetGeltung.KAPAZITIV: KanalkapazitaetTyp.ORDNUNGS_KANALKAPAZITAET,
    KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV: KanalkapazitaetTyp.SOUVERAENITAETS_KANALKAPAZITAET,
}

_PROZEDUR_MAP: dict[KanalkapazitaetGeltung, KanalkapazitaetProzedur] = {
    KanalkapazitaetGeltung.GESPERRT: KanalkapazitaetProzedur.NOTPROZEDUR,
    KanalkapazitaetGeltung.KAPAZITIV: KanalkapazitaetProzedur.REGELPROTOKOLL,
    KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV: KanalkapazitaetProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KanalkapazitaetGeltung, float] = {
    KanalkapazitaetGeltung.GESPERRT: 0.0,
    KanalkapazitaetGeltung.KAPAZITIV: 0.04,
    KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV: 0.08,
}

_TIER_DELTA: dict[KanalkapazitaetGeltung, int] = {
    KanalkapazitaetGeltung.GESPERRT: 0,
    KanalkapazitaetGeltung.KAPAZITIV: 1,
    KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KanalkapazitaetNorm:
    kanalkapazitaet_register_id: str
    kanalkapazitaet_typ: KanalkapazitaetTyp
    prozedur: KanalkapazitaetProzedur
    geltung: KanalkapazitaetGeltung
    kanalkapazitaet_weight: float
    kanalkapazitaet_tier: int
    canonical: bool
    kanalkapazitaet_ids: tuple[str, ...]
    kanalkapazitaet_tags: tuple[str, ...]


@dataclass(frozen=True)
class KanalkapazitaetRegister:
    register_id: str
    shannon_entropie_feld: ShannonEntropieFeld
    normen: tuple[KanalkapazitaetNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kanalkapazitaet_register_id for n in self.normen if n.geltung is KanalkapazitaetGeltung.GESPERRT)

    @property
    def kapazitiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kanalkapazitaet_register_id for n in self.normen if n.geltung is KanalkapazitaetGeltung.KAPAZITIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kanalkapazitaet_register_id for n in self.normen if n.geltung is KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV)

    @property
    def register_signal(self):
        if any(n.geltung is KanalkapazitaetGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is KanalkapazitaetGeltung.KAPAZITIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-kapazitiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-kapazitiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kanalkapazitaet_register(
    shannon_entropie_feld: ShannonEntropieFeld | None = None,
    *,
    register_id: str = "kanalkapazitaet-register",
) -> KanalkapazitaetRegister:
    if shannon_entropie_feld is None:
        shannon_entropie_feld = build_shannon_entropie_feld(feld_id=f"{register_id}-feld")

    normen: list[KanalkapazitaetNorm] = []
    for parent_norm in shannon_entropie_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.shannon_entropie_feld_id.removeprefix(f'{shannon_entropie_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.shannon_entropie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.shannon_entropie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV)
        normen.append(
            KanalkapazitaetNorm(
                kanalkapazitaet_register_id=new_id,
                kanalkapazitaet_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kanalkapazitaet_weight=new_weight,
                kanalkapazitaet_tier=new_tier,
                canonical=is_canonical,
                kanalkapazitaet_ids=parent_norm.shannon_entropie_ids + (new_id,),
                kanalkapazitaet_tags=parent_norm.shannon_entropie_tags + (f"kanalkapazitaet:{new_geltung.value}",),
            )
        )
    return KanalkapazitaetRegister(
        register_id=register_id,
        shannon_entropie_feld=shannon_entropie_feld,
        normen=tuple(normen),
    )
