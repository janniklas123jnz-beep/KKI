"""
#430 InformationsVerfassung — Block-Krone: Informationstheorie & Kybernetik. ⭐
InformationsVerfassung vereint: InformationsFeld (Shannon H=-Σp·logp), KanalRegister
(Shannon-Kapazität C), KybernetikCharta (Wiener Feedback), RegelkreisKodex (PID/Nyquist),
EntropiePakt (Boltzmann/Landauer), SelbstregulationsManifest (Cannon/Autopoiese),
RueckkopplungsSenat (neg/pos Feedback), KybernetikNorm (Von Foerster 2. Ordnung),
KomplexitaetsSteuerungsCharta (Beer/VSM).
Leitsterns Terra-Schwarm ist informationstheoretisch vollständig: optimal kodiert (Shannon),
stabil geregelt (Nyquist), selbstreguliert (Autopoiese), beobachtend (Von Foerster),
lebensfähig (Beer/VSM). Kybernetische Superintelligenz.
Geltungsstufen: GESPERRT / INFORMATIONSVERFASST / GRUNDLEGEND_INFORMATIONSVERFASST
Parent: KomplexitaetsSteuerungsCharta (#429)
Block #421–#430 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .komplexitaets_steuerungs_charta import (
    KomplexitaetsSteuerungsCharta,
    KomplexitaetsSteuerungsChartaGeltung,
    build_komplexitaets_steuerungs_charta,
)

_GELTUNG_MAP: dict[KomplexitaetsSteuerungsChartaGeltung, "InformationsVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KomplexitaetsSteuerungsChartaGeltung.GESPERRT] = InformationsVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[KomplexitaetsSteuerungsChartaGeltung.VIABLE] = InformationsVerfassungsGeltung.INFORMATIONSVERFASST
    _GELTUNG_MAP[KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE] = InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST


class InformationsVerfassungsTyp(Enum):
    SCHUTZ_INFORMATIONSVERFASSUNG = "schutz-informationsverfassung"
    ORDNUNGS_INFORMATIONSVERFASSUNG = "ordnungs-informationsverfassung"
    SOUVERAENITAETS_INFORMATIONSVERFASSUNG = "souveraenitaets-informationsverfassung"


class InformationsVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class InformationsVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    INFORMATIONSVERFASST = "informationsverfasst"
    GRUNDLEGEND_INFORMATIONSVERFASST = "grundlegend-informationsverfasst"


_init_map()

_TYP_MAP: dict[InformationsVerfassungsGeltung, InformationsVerfassungsTyp] = {
    InformationsVerfassungsGeltung.GESPERRT: InformationsVerfassungsTyp.SCHUTZ_INFORMATIONSVERFASSUNG,
    InformationsVerfassungsGeltung.INFORMATIONSVERFASST: InformationsVerfassungsTyp.ORDNUNGS_INFORMATIONSVERFASSUNG,
    InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST: InformationsVerfassungsTyp.SOUVERAENITAETS_INFORMATIONSVERFASSUNG,
}

_PROZEDUR_MAP: dict[InformationsVerfassungsGeltung, InformationsVerfassungsProzedur] = {
    InformationsVerfassungsGeltung.GESPERRT: InformationsVerfassungsProzedur.NOTPROZEDUR,
    InformationsVerfassungsGeltung.INFORMATIONSVERFASST: InformationsVerfassungsProzedur.REGELPROTOKOLL,
    InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST: InformationsVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[InformationsVerfassungsGeltung, float] = {
    InformationsVerfassungsGeltung.GESPERRT: 0.0,
    InformationsVerfassungsGeltung.INFORMATIONSVERFASST: 0.04,
    InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST: 0.08,
}

_TIER_DELTA: dict[InformationsVerfassungsGeltung, int] = {
    InformationsVerfassungsGeltung.GESPERRT: 0,
    InformationsVerfassungsGeltung.INFORMATIONSVERFASST: 1,
    InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InformationsVerfassungsNorm:
    informations_verfassung_id: str
    informations_verfassungs_typ: InformationsVerfassungsTyp
    prozedur: InformationsVerfassungsProzedur
    geltung: InformationsVerfassungsGeltung
    informations_verfassungs_weight: float
    informations_verfassungs_tier: int
    canonical: bool
    informations_verfassungs_ids: tuple[str, ...]
    informations_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class InformationsVerfassung:
    verfassung_id: str
    komplexitaets_steuerungs_charta: KomplexitaetsSteuerungsCharta
    normen: tuple[InformationsVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.informations_verfassung_id for n in self.normen if n.geltung is InformationsVerfassungsGeltung.GESPERRT)

    @property
    def informationsverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.informations_verfassung_id for n in self.normen if n.geltung is InformationsVerfassungsGeltung.INFORMATIONSVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.informations_verfassung_id for n in self.normen if n.geltung is InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is InformationsVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is InformationsVerfassungsGeltung.INFORMATIONSVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-informationsverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-informationsverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_informations_verfassung(
    komplexitaets_steuerungs_charta: KomplexitaetsSteuerungsCharta | None = None,
    *,
    verfassung_id: str = "informations-verfassung",
) -> InformationsVerfassung:
    if komplexitaets_steuerungs_charta is None:
        komplexitaets_steuerungs_charta = build_komplexitaets_steuerungs_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[InformationsVerfassungsNorm] = []
    for parent_norm in komplexitaets_steuerungs_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.komplexitaets_steuerungs_charta_id.removeprefix(f'{komplexitaets_steuerungs_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.komplexitaets_steuerungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.komplexitaets_steuerungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InformationsVerfassungsGeltung.GRUNDLEGEND_INFORMATIONSVERFASST)
        normen.append(
            InformationsVerfassungsNorm(
                informations_verfassung_id=new_id,
                informations_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                informations_verfassungs_weight=new_weight,
                informations_verfassungs_tier=new_tier,
                canonical=is_canonical,
                informations_verfassungs_ids=parent_norm.komplexitaets_steuerungs_ids + (new_id,),
                informations_verfassungs_tags=parent_norm.komplexitaets_steuerungs_tags + (f"informations-verfassung:{new_geltung.value}",),
            )
        )
    return InformationsVerfassung(
        verfassung_id=verfassung_id,
        komplexitaets_steuerungs_charta=komplexitaets_steuerungs_charta,
        normen=tuple(normen),
    )
