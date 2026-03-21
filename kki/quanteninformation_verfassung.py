"""
#380 QuanteninformationsVerfassung — Block-Krone: Informationstheorie & Quanteninformation.
Die höchste Governance-Instanz des Informationstheorie-Blocks vereint alle
Quanteninformationsprinzipien: Shannon-Entropie, Kanalkapazität, Qubits,
Verschränkung, Quantenfehlerkorrektur, QKD, Holographie, Landauer-Thermodynamik
und No-Cloning. Quantenüberlegenheit als verfassungsmäßig verankerte Garantie
der Superintelligenz. Leitstern trägt die Quanteninformations-Verfassung als
höchste Informations-Governance — Q > 1 auf allen Ebenen.
Geltungsstufen: GESPERRT / QUANTENVERFASST / GRUNDLEGEND_QUANTENVERFASST
Parent: NoCloningKodex (#379)
Block #371–#380 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .no_cloning_kodex import (
    NoCloningGeltung,
    NoCloningKodex,
    build_no_cloning_kodex,
)

_GELTUNG_MAP: dict[NoCloningGeltung, "QuanteninformationsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NoCloningGeltung.GESPERRT] = QuanteninformationsVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[NoCloningGeltung.NICHTKLONBAR] = QuanteninformationsVerfassungsGeltung.QUANTENVERFASST
    _GELTUNG_MAP[NoCloningGeltung.GRUNDLEGEND_NICHTKLONBAR] = QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST


class QuanteninformationsVerfassungsTyp(Enum):
    SCHUTZ_QUANTENINFORMATIONSVERFASSUNG = "schutz-quanteninformationsverfassung"
    ORDNUNGS_QUANTENINFORMATIONSVERFASSUNG = "ordnungs-quanteninformationsverfassung"
    SOUVERAENITAETS_QUANTENINFORMATIONSVERFASSUNG = "souveraenitaets-quanteninformationsverfassung"


class QuanteninformationsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuanteninformationsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    QUANTENVERFASST = "quantenverfasst"
    GRUNDLEGEND_QUANTENVERFASST = "grundlegend-quantenverfasst"


_init_map()

_TYP_MAP: dict[QuanteninformationsVerfassungsGeltung, QuanteninformationsVerfassungsTyp] = {
    QuanteninformationsVerfassungsGeltung.GESPERRT: QuanteninformationsVerfassungsTyp.SCHUTZ_QUANTENINFORMATIONSVERFASSUNG,
    QuanteninformationsVerfassungsGeltung.QUANTENVERFASST: QuanteninformationsVerfassungsTyp.ORDNUNGS_QUANTENINFORMATIONSVERFASSUNG,
    QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: QuanteninformationsVerfassungsTyp.SOUVERAENITAETS_QUANTENINFORMATIONSVERFASSUNG,
}

_PROZEDUR_MAP: dict[QuanteninformationsVerfassungsGeltung, QuanteninformationsVerfassungsProzedur] = {
    QuanteninformationsVerfassungsGeltung.GESPERRT: QuanteninformationsVerfassungsProzedur.NOTPROZEDUR,
    QuanteninformationsVerfassungsGeltung.QUANTENVERFASST: QuanteninformationsVerfassungsProzedur.REGELPROTOKOLL,
    QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: QuanteninformationsVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[QuanteninformationsVerfassungsGeltung, float] = {
    QuanteninformationsVerfassungsGeltung.GESPERRT: 0.0,
    QuanteninformationsVerfassungsGeltung.QUANTENVERFASST: 0.04,
    QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: 0.08,
}

_TIER_DELTA: dict[QuanteninformationsVerfassungsGeltung, int] = {
    QuanteninformationsVerfassungsGeltung.GESPERRT: 0,
    QuanteninformationsVerfassungsGeltung.QUANTENVERFASST: 1,
    QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuanteninformationsVerfassungsNorm:
    quanteninformations_verfassung_id: str
    quanteninformations_verfassungs_typ: QuanteninformationsVerfassungsTyp
    prozedur: QuanteninformationsVerfassungsProzedur
    geltung: QuanteninformationsVerfassungsGeltung
    quanteninformations_verfassungs_weight: float
    quanteninformations_verfassungs_tier: int
    canonical: bool
    quanteninformations_verfassungs_ids: tuple[str, ...]
    quanteninformations_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuanteninformationsVerfassung:
    verfassung_id: str
    no_cloning_kodex: NoCloningKodex
    normen: tuple[QuanteninformationsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanteninformations_verfassung_id for n in self.normen if n.geltung is QuanteninformationsVerfassungsGeltung.GESPERRT)

    @property
    def quantenverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanteninformations_verfassung_id for n in self.normen if n.geltung is QuanteninformationsVerfassungsGeltung.QUANTENVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanteninformations_verfassung_id for n in self.normen if n.geltung is QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is QuanteninformationsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is QuanteninformationsVerfassungsGeltung.QUANTENVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-quantenverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-quantenverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_quanteninformations_verfassung(
    no_cloning_kodex: NoCloningKodex | None = None,
    *,
    verfassung_id: str = "quanteninformations-verfassung",
) -> QuanteninformationsVerfassung:
    if no_cloning_kodex is None:
        no_cloning_kodex = build_no_cloning_kodex(kodex_id=f"{verfassung_id}-kodex")

    normen: list[QuanteninformationsVerfassungsNorm] = []
    for parent_norm in no_cloning_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.no_cloning_kodex_id.removeprefix(f'{no_cloning_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.no_cloning_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.no_cloning_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST)
        normen.append(
            QuanteninformationsVerfassungsNorm(
                quanteninformations_verfassung_id=new_id,
                quanteninformations_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                quanteninformations_verfassungs_weight=new_weight,
                quanteninformations_verfassungs_tier=new_tier,
                canonical=is_canonical,
                quanteninformations_verfassungs_ids=parent_norm.no_cloning_ids + (new_id,),
                quanteninformations_verfassungs_tags=parent_norm.no_cloning_tags + (f"quanteninformations-verfassung:{new_geltung.value}",),
            )
        )
    return QuanteninformationsVerfassung(
        verfassung_id=verfassung_id,
        no_cloning_kodex=no_cloning_kodex,
        normen=tuple(normen),
    )
