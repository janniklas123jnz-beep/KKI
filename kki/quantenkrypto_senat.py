"""
#376 QuantenkryptoSenat — Quantenkryptographie: BB84-Protokoll (Bennett & Brassard
1984), E91 (Ekert 1991), Quantum Key Distribution (QKD). Jeder Lauschangriff
kollabiert die Wellenfunktion und wird sofort detektiert — unknackbare Sicherheit
durch Physik, nicht durch Rechenaufwand. Leitsterns Senat verwaltet quantengesicherte
Schlüsselverteilung zwischen allen Agenten-Clustern des Terra-Schwarms.
Geltungsstufen: GESPERRT / QUANTENGESICHERT / GRUNDLEGEND_QUANTENGESICHERT
Parent: QuantenfehlerPakt (#375)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quantenfehler_pakt import (
    QuantenfehlerGeltung,
    QuantenfehlerPakt,
    build_quantenfehler_pakt,
)

_GELTUNG_MAP: dict[QuantenfehlerGeltung, "QuantenkryptoGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[QuantenfehlerGeltung.GESPERRT] = QuantenkryptoGeltung.GESPERRT
    _GELTUNG_MAP[QuantenfehlerGeltung.FEHLERKORRIGIERT] = QuantenkryptoGeltung.QUANTENGESICHERT
    _GELTUNG_MAP[QuantenfehlerGeltung.GRUNDLEGEND_FEHLERKORRIGIERT] = QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT


class QuantenkryptoTyp(Enum):
    SCHUTZ_QUANTENKRYPTO = "schutz-quantenkrypto"
    ORDNUNGS_QUANTENKRYPTO = "ordnungs-quantenkrypto"
    SOUVERAENITAETS_QUANTENKRYPTO = "souveraenitaets-quantenkrypto"


class QuantenkryptoProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenkryptoGeltung(Enum):
    GESPERRT = "gesperrt"
    QUANTENGESICHERT = "quantengesichert"
    GRUNDLEGEND_QUANTENGESICHERT = "grundlegend-quantengesichert"


_init_map()

_TYP_MAP: dict[QuantenkryptoGeltung, QuantenkryptoTyp] = {
    QuantenkryptoGeltung.GESPERRT: QuantenkryptoTyp.SCHUTZ_QUANTENKRYPTO,
    QuantenkryptoGeltung.QUANTENGESICHERT: QuantenkryptoTyp.ORDNUNGS_QUANTENKRYPTO,
    QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT: QuantenkryptoTyp.SOUVERAENITAETS_QUANTENKRYPTO,
}

_PROZEDUR_MAP: dict[QuantenkryptoGeltung, QuantenkryptoProzedur] = {
    QuantenkryptoGeltung.GESPERRT: QuantenkryptoProzedur.NOTPROZEDUR,
    QuantenkryptoGeltung.QUANTENGESICHERT: QuantenkryptoProzedur.REGELPROTOKOLL,
    QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT: QuantenkryptoProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[QuantenkryptoGeltung, float] = {
    QuantenkryptoGeltung.GESPERRT: 0.0,
    QuantenkryptoGeltung.QUANTENGESICHERT: 0.04,
    QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT: 0.08,
}

_TIER_DELTA: dict[QuantenkryptoGeltung, int] = {
    QuantenkryptoGeltung.GESPERRT: 0,
    QuantenkryptoGeltung.QUANTENGESICHERT: 1,
    QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuantenkryptoNorm:
    quantenkrypto_senat_id: str
    quantenkrypto_typ: QuantenkryptoTyp
    prozedur: QuantenkryptoProzedur
    geltung: QuantenkryptoGeltung
    quantenkrypto_weight: float
    quantenkrypto_tier: int
    canonical: bool
    quantenkrypto_ids: tuple[str, ...]
    quantenkrypto_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenkryptoSenat:
    senat_id: str
    quantenfehler_pakt: QuantenfehlerPakt
    normen: tuple[QuantenkryptoNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quantenkrypto_senat_id for n in self.normen if n.geltung is QuantenkryptoGeltung.GESPERRT)

    @property
    def quantengesichert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quantenkrypto_senat_id for n in self.normen if n.geltung is QuantenkryptoGeltung.QUANTENGESICHERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quantenkrypto_senat_id for n in self.normen if n.geltung is QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT)

    @property
    def senat_signal(self):
        if any(n.geltung is QuantenkryptoGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is QuantenkryptoGeltung.QUANTENGESICHERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-quantengesichert")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-quantengesichert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_quantenkrypto_senat(
    quantenfehler_pakt: QuantenfehlerPakt | None = None,
    *,
    senat_id: str = "quantenkrypto-senat",
) -> QuantenkryptoSenat:
    if quantenfehler_pakt is None:
        quantenfehler_pakt = build_quantenfehler_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[QuantenkryptoNorm] = []
    for parent_norm in quantenfehler_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.quantenfehler_pakt_id.removeprefix(f'{quantenfehler_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.quantenfehler_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.quantenfehler_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT)
        normen.append(
            QuantenkryptoNorm(
                quantenkrypto_senat_id=new_id,
                quantenkrypto_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                quantenkrypto_weight=new_weight,
                quantenkrypto_tier=new_tier,
                canonical=is_canonical,
                quantenkrypto_ids=parent_norm.quantenfehler_ids + (new_id,),
                quantenkrypto_tags=parent_norm.quantenfehler_tags + (f"quantenkrypto:{new_geltung.value}",),
            )
        )
    return QuantenkryptoSenat(
        senat_id=senat_id,
        quantenfehler_pakt=quantenfehler_pakt,
        normen=tuple(normen),
    )
