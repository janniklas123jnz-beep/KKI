"""
#422 KanalRegister — Kanalcodierung: Shannon-Kapazität und Fehlerkorrektur.
Shannon (1948): Kanalkapazität C = max I(X;Y). Kanalcodierungs-Theorem: zuverlässige
Übertragung möglich falls R < C. Hamming-Code (1950): erstes systematisches
Fehlerkorrekturverfahren. Turbo-Codes (Berrou 1993): nahe Shannon-Grenze.
Leitsterns Kommunikation: fehlerkorrigiert bis zur Kapazitätsgrenze.
Geltungsstufen: GESPERRT / KANALKODIERT / GRUNDLEGEND_KANALKODIERT
Parent: InformationsFeld (#421)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .informations_feld import (
    InformationsFeld,
    InformationsFeldGeltung,
    build_informations_feld,
)

_GELTUNG_MAP: dict[InformationsFeldGeltung, "KanalRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[InformationsFeldGeltung.GESPERRT] = KanalRegisterGeltung.GESPERRT
    _GELTUNG_MAP[InformationsFeldGeltung.INFORMATIONSREICH] = KanalRegisterGeltung.KANALKODIERT
    _GELTUNG_MAP[InformationsFeldGeltung.GRUNDLEGEND_INFORMATIONSREICH] = KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT


class KanalRegisterTyp(Enum):
    SCHUTZ_KANAL = "schutz-kanal"
    ORDNUNGS_KANAL = "ordnungs-kanal"
    SOUVERAENITAETS_KANAL = "souveraenitaets-kanal"


class KanalRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KanalRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    KANALKODIERT = "kanalkodiert"
    GRUNDLEGEND_KANALKODIERT = "grundlegend-kanalkodiert"


_init_map()

_TYP_MAP: dict[KanalRegisterGeltung, KanalRegisterTyp] = {
    KanalRegisterGeltung.GESPERRT: KanalRegisterTyp.SCHUTZ_KANAL,
    KanalRegisterGeltung.KANALKODIERT: KanalRegisterTyp.ORDNUNGS_KANAL,
    KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT: KanalRegisterTyp.SOUVERAENITAETS_KANAL,
}

_PROZEDUR_MAP: dict[KanalRegisterGeltung, KanalRegisterProzedur] = {
    KanalRegisterGeltung.GESPERRT: KanalRegisterProzedur.NOTPROZEDUR,
    KanalRegisterGeltung.KANALKODIERT: KanalRegisterProzedur.REGELPROTOKOLL,
    KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT: KanalRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KanalRegisterGeltung, float] = {
    KanalRegisterGeltung.GESPERRT: 0.0,
    KanalRegisterGeltung.KANALKODIERT: 0.04,
    KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT: 0.08,
}

_TIER_DELTA: dict[KanalRegisterGeltung, int] = {
    KanalRegisterGeltung.GESPERRT: 0,
    KanalRegisterGeltung.KANALKODIERT: 1,
    KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KanalRegisterNorm:
    kanal_register_id: str
    kanal_typ: KanalRegisterTyp
    prozedur: KanalRegisterProzedur
    geltung: KanalRegisterGeltung
    kanal_weight: float
    kanal_tier: int
    canonical: bool
    kanal_ids: tuple[str, ...]
    kanal_tags: tuple[str, ...]


@dataclass(frozen=True)
class KanalRegister:
    register_id: str
    informations_feld: InformationsFeld
    normen: tuple[KanalRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kanal_register_id for n in self.normen if n.geltung is KanalRegisterGeltung.GESPERRT)

    @property
    def kanalkodiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kanal_register_id for n in self.normen if n.geltung is KanalRegisterGeltung.KANALKODIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kanal_register_id for n in self.normen if n.geltung is KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT)

    @property
    def register_signal(self):
        if any(n.geltung is KanalRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is KanalRegisterGeltung.KANALKODIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-kanalkodiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-kanalkodiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kanal_register(
    informations_feld: InformationsFeld | None = None,
    *,
    register_id: str = "kanal-register",
) -> KanalRegister:
    if informations_feld is None:
        informations_feld = build_informations_feld(feld_id=f"{register_id}-feld")

    normen: list[KanalRegisterNorm] = []
    for parent_norm in informations_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.informations_feld_id.removeprefix(f'{informations_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.informations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.informations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT)
        normen.append(
            KanalRegisterNorm(
                kanal_register_id=new_id,
                kanal_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kanal_weight=new_weight,
                kanal_tier=new_tier,
                canonical=is_canonical,
                kanal_ids=parent_norm.informations_ids + (new_id,),
                kanal_tags=parent_norm.informations_tags + (f"kanal-register:{new_geltung.value}",),
            )
        )
    return KanalRegister(
        register_id=register_id,
        informations_feld=informations_feld,
        normen=tuple(normen),
    )
