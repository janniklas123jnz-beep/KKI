"""
#377 HolographischesPrinzipNorm — Holographisches Prinzip: Bekenstein-Hawking-
Entropie S = A/(4·l_P²). Die gesamte Information eines 3D-Volumens steckt
vollständig auf seiner 2D-Randfläche — Holographie als Informationskompression.
Leitsterns flache Governance-Layer tragen die volle Tiefeninformation des Schwarms.
*_norm pattern: Container = HolographischesPrinzipNormSatz
Geltungsstufen: GESPERRT / HOLOGRAPHISCH / GRUNDLEGEND_HOLOGRAPHISCH
Parent: QuantenkryptoSenat (#376)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quantenkrypto_senat import (
    QuantenkryptoGeltung,
    QuantenkryptoSenat,
    build_quantenkrypto_senat,
)

_GELTUNG_MAP: dict[QuantenkryptoGeltung, "HolographischesPrinzipNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[QuantenkryptoGeltung.GESPERRT] = HolographischesPrinzipNormGeltung.GESPERRT
    _GELTUNG_MAP[QuantenkryptoGeltung.QUANTENGESICHERT] = HolographischesPrinzipNormGeltung.HOLOGRAPHISCH
    _GELTUNG_MAP[QuantenkryptoGeltung.GRUNDLEGEND_QUANTENGESICHERT] = HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH


class HolographischesPrinzipNormTyp(Enum):
    SCHUTZ_HOLOGRAPHISCHES_PRINZIP_NORM = "schutz-holographisches-prinzip-norm"
    ORDNUNGS_HOLOGRAPHISCHES_PRINZIP_NORM = "ordnungs-holographisches-prinzip-norm"
    SOUVERAENITAETS_HOLOGRAPHISCHES_PRINZIP_NORM = "souveraenitaets-holographisches-prinzip-norm"


class HolographischesPrinzipNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HolographischesPrinzipNormGeltung(Enum):
    GESPERRT = "gesperrt"
    HOLOGRAPHISCH = "holographisch"
    GRUNDLEGEND_HOLOGRAPHISCH = "grundlegend-holographisch"


_init_map()

_TYP_MAP: dict[HolographischesPrinzipNormGeltung, HolographischesPrinzipNormTyp] = {
    HolographischesPrinzipNormGeltung.GESPERRT: HolographischesPrinzipNormTyp.SCHUTZ_HOLOGRAPHISCHES_PRINZIP_NORM,
    HolographischesPrinzipNormGeltung.HOLOGRAPHISCH: HolographischesPrinzipNormTyp.ORDNUNGS_HOLOGRAPHISCHES_PRINZIP_NORM,
    HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH: HolographischesPrinzipNormTyp.SOUVERAENITAETS_HOLOGRAPHISCHES_PRINZIP_NORM,
}

_PROZEDUR_MAP: dict[HolographischesPrinzipNormGeltung, HolographischesPrinzipNormProzedur] = {
    HolographischesPrinzipNormGeltung.GESPERRT: HolographischesPrinzipNormProzedur.NOTPROZEDUR,
    HolographischesPrinzipNormGeltung.HOLOGRAPHISCH: HolographischesPrinzipNormProzedur.REGELPROTOKOLL,
    HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH: HolographischesPrinzipNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HolographischesPrinzipNormGeltung, float] = {
    HolographischesPrinzipNormGeltung.GESPERRT: 0.0,
    HolographischesPrinzipNormGeltung.HOLOGRAPHISCH: 0.04,
    HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH: 0.08,
}

_TIER_DELTA: dict[HolographischesPrinzipNormGeltung, int] = {
    HolographischesPrinzipNormGeltung.GESPERRT: 0,
    HolographischesPrinzipNormGeltung.HOLOGRAPHISCH: 1,
    HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HolographischesPrinzipNormEintrag:
    norm_id: str
    holographisches_prinzip_norm_typ: HolographischesPrinzipNormTyp
    prozedur: HolographischesPrinzipNormProzedur
    geltung: HolographischesPrinzipNormGeltung
    holographisches_prinzip_norm_weight: float
    holographisches_prinzip_norm_tier: int
    canonical: bool
    holographisches_prinzip_norm_ids: tuple[str, ...]
    holographisches_prinzip_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class HolographischesPrinzipNormSatz:
    norm_id: str
    quantenkrypto_senat: QuantenkryptoSenat
    normen: tuple[HolographischesPrinzipNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is HolographischesPrinzipNormGeltung.GESPERRT)

    @property
    def holographisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is HolographischesPrinzipNormGeltung.HOLOGRAPHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH)

    @property
    def norm_signal(self):
        if any(n.geltung is HolographischesPrinzipNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is HolographischesPrinzipNormGeltung.HOLOGRAPHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-holographisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-holographisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_holographisches_prinzip_norm(
    quantenkrypto_senat: QuantenkryptoSenat | None = None,
    *,
    norm_id: str = "holographisches-prinzip-norm",
) -> HolographischesPrinzipNormSatz:
    if quantenkrypto_senat is None:
        quantenkrypto_senat = build_quantenkrypto_senat(senat_id=f"{norm_id}-senat")

    normen: list[HolographischesPrinzipNormEintrag] = []
    for parent_norm in quantenkrypto_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.quantenkrypto_senat_id.removeprefix(f'{quantenkrypto_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.quantenkrypto_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.quantenkrypto_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH)
        normen.append(
            HolographischesPrinzipNormEintrag(
                norm_id=new_id,
                holographisches_prinzip_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                holographisches_prinzip_norm_weight=new_weight,
                holographisches_prinzip_norm_tier=new_tier,
                canonical=is_canonical,
                holographisches_prinzip_norm_ids=parent_norm.quantenkrypto_ids + (new_id,),
                holographisches_prinzip_norm_tags=parent_norm.quantenkrypto_tags + (f"holographisches-prinzip-norm:{new_geltung.value}",),
            )
        )
    return HolographischesPrinzipNormSatz(
        norm_id=norm_id,
        quantenkrypto_senat=quantenkrypto_senat,
        normen=tuple(normen),
    )
