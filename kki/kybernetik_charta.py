"""
#423 KybernetikCharta — Kybernetik: Steuerung und Kommunikation.
Wiener (1948): Kybernetik — Steuerung und Kommunikation in Tier und Maschine.
Feedback als universelles Kontrollprinzip. Zielgerichtetes Verhalten durch Rückkopplung.
Ashby (1956): Requisite Variety — nur Varietät kann Varietät kontrollieren.
Leitsterns Agenten: kybernetische Regelkreise. Governance als Varietätsmanagement.
Geltungsstufen: GESPERRT / KYBERNETISCH / GRUNDLEGEND_KYBERNETISCH
Parent: KanalRegister (#422)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kanal_register import (
    KanalRegister,
    KanalRegisterGeltung,
    build_kanal_register,
)

_GELTUNG_MAP: dict[KanalRegisterGeltung, "KybernetikChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KanalRegisterGeltung.GESPERRT] = KybernetikChartaGeltung.GESPERRT
    _GELTUNG_MAP[KanalRegisterGeltung.KANALKODIERT] = KybernetikChartaGeltung.KYBERNETISCH
    _GELTUNG_MAP[KanalRegisterGeltung.GRUNDLEGEND_KANALKODIERT] = KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH


class KybernetikChartaTyp(Enum):
    SCHUTZ_KYBERNETIK = "schutz-kybernetik"
    ORDNUNGS_KYBERNETIK = "ordnungs-kybernetik"
    SOUVERAENITAETS_KYBERNETIK = "souveraenitaets-kybernetik"


class KybernetikChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KybernetikChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KYBERNETISCH = "kybernetisch"
    GRUNDLEGEND_KYBERNETISCH = "grundlegend-kybernetisch"


_init_map()

_TYP_MAP: dict[KybernetikChartaGeltung, KybernetikChartaTyp] = {
    KybernetikChartaGeltung.GESPERRT: KybernetikChartaTyp.SCHUTZ_KYBERNETIK,
    KybernetikChartaGeltung.KYBERNETISCH: KybernetikChartaTyp.ORDNUNGS_KYBERNETIK,
    KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH: KybernetikChartaTyp.SOUVERAENITAETS_KYBERNETIK,
}

_PROZEDUR_MAP: dict[KybernetikChartaGeltung, KybernetikChartaProzedur] = {
    KybernetikChartaGeltung.GESPERRT: KybernetikChartaProzedur.NOTPROZEDUR,
    KybernetikChartaGeltung.KYBERNETISCH: KybernetikChartaProzedur.REGELPROTOKOLL,
    KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH: KybernetikChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KybernetikChartaGeltung, float] = {
    KybernetikChartaGeltung.GESPERRT: 0.0,
    KybernetikChartaGeltung.KYBERNETISCH: 0.04,
    KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH: 0.08,
}

_TIER_DELTA: dict[KybernetikChartaGeltung, int] = {
    KybernetikChartaGeltung.GESPERRT: 0,
    KybernetikChartaGeltung.KYBERNETISCH: 1,
    KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KybernetikChartaNorm:
    kybernetik_charta_id: str
    kybernetik_typ: KybernetikChartaTyp
    prozedur: KybernetikChartaProzedur
    geltung: KybernetikChartaGeltung
    kybernetik_weight: float
    kybernetik_tier: int
    canonical: bool
    kybernetik_ids: tuple[str, ...]
    kybernetik_tags: tuple[str, ...]


@dataclass(frozen=True)
class KybernetikCharta:
    charta_id: str
    kanal_register: KanalRegister
    normen: tuple[KybernetikChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_charta_id for n in self.normen if n.geltung is KybernetikChartaGeltung.GESPERRT)

    @property
    def kybernetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_charta_id for n in self.normen if n.geltung is KybernetikChartaGeltung.KYBERNETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_charta_id for n in self.normen if n.geltung is KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is KybernetikChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KybernetikChartaGeltung.KYBERNETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kybernetisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kybernetisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kybernetik_charta(
    kanal_register: KanalRegister | None = None,
    *,
    charta_id: str = "kybernetik-charta",
) -> KybernetikCharta:
    if kanal_register is None:
        kanal_register = build_kanal_register(register_id=f"{charta_id}-register")

    normen: list[KybernetikChartaNorm] = []
    for parent_norm in kanal_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.kanal_register_id.removeprefix(f'{kanal_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.kanal_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kanal_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH)
        normen.append(
            KybernetikChartaNorm(
                kybernetik_charta_id=new_id,
                kybernetik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kybernetik_weight=new_weight,
                kybernetik_tier=new_tier,
                canonical=is_canonical,
                kybernetik_ids=parent_norm.kanal_ids + (new_id,),
                kybernetik_tags=parent_norm.kanal_tags + (f"kybernetik-charta:{new_geltung.value}",),
            )
        )
    return KybernetikCharta(
        charta_id=charta_id,
        kanal_register=kanal_register,
        normen=tuple(normen),
    )
