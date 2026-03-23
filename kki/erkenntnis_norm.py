"""
#478 ErkenntnisNorm — Lakatos Forschungsprogramm & Quine Holismus (*_norm-Muster).
Imre Lakatos (1978): Wissenschaftliche Forschungsprogramme — harter Kern, Schutzgürtel
  aus Hilfshypothesen; progressive vs. degenerative Forschungsprogramme.
W.V.O. Quine (1951): Two Dogmas of Empiricism — Holismus der Überzeugungen; kein Satz
  ist immun gegen Revision; Unterbestimmtheit der Theorie durch die Daten.
Leitsterns Erkenntnisnom: Jeder Agent pflegt einen harten Kern unverrückbarer Axiome
(GESPERRT), einen anpassungsfähigen Schutzgürtel (ERKENNTNISNORMATIV) und grundlegende
Holismusprotokolle für Gesamtrevision (GRUNDLEGEND_ERKENNTNISNORMATIV).
Geltungsstufen: GESPERRT / ERKENNTNISNORMATIV / GRUNDLEGEND_ERKENNTNISNORMATIV
Parent: LogikSenat (#477) — *_norm-Muster
Block #471–#480: Philosophie & Erkenntnistheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .logik_senat import (
    LogikSenat,
    LogikSenatGeltung,
    build_logik_senat,
)

_GELTUNG_MAP: dict[LogikSenatGeltung, "ErkenntnisNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LogikSenatGeltung.GESPERRT] = ErkenntnisNormGeltung.GESPERRT
    _GELTUNG_MAP[LogikSenatGeltung.LOGISCH] = ErkenntnisNormGeltung.ERKENNTNISNORMATIV
    _GELTUNG_MAP[LogikSenatGeltung.GRUNDLEGEND_LOGISCH] = ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV


class ErkenntnisNormTyp(Enum):
    SCHUTZ_ERKENNTNISNORM = "schutz-erkenntnisnorm"
    ORDNUNGS_ERKENNTNISNORM = "ordnungs-erkenntnisnorm"
    SOUVERAENITAETS_ERKENNTNISNORM = "souveraenitaets-erkenntnisnorm"


class ErkenntnisNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ErkenntnisNormGeltung(Enum):
    GESPERRT = "gesperrt"
    ERKENNTNISNORMATIV = "erkenntnisnormativ"
    GRUNDLEGEND_ERKENNTNISNORMATIV = "grundlegend-erkenntnisnormativ"


_init_map()

_TYP_MAP: dict[ErkenntnisNormGeltung, ErkenntnisNormTyp] = {
    ErkenntnisNormGeltung.GESPERRT: ErkenntnisNormTyp.SCHUTZ_ERKENNTNISNORM,
    ErkenntnisNormGeltung.ERKENNTNISNORMATIV: ErkenntnisNormTyp.ORDNUNGS_ERKENNTNISNORM,
    ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV: ErkenntnisNormTyp.SOUVERAENITAETS_ERKENNTNISNORM,
}

_PROZEDUR_MAP: dict[ErkenntnisNormGeltung, ErkenntnisNormProzedur] = {
    ErkenntnisNormGeltung.GESPERRT: ErkenntnisNormProzedur.NOTPROZEDUR,
    ErkenntnisNormGeltung.ERKENNTNISNORMATIV: ErkenntnisNormProzedur.REGELPROTOKOLL,
    ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV: ErkenntnisNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ErkenntnisNormGeltung, float] = {
    ErkenntnisNormGeltung.GESPERRT: 0.0,
    ErkenntnisNormGeltung.ERKENNTNISNORMATIV: 0.04,
    ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV: 0.08,
}

_TIER_DELTA: dict[ErkenntnisNormGeltung, int] = {
    ErkenntnisNormGeltung.GESPERRT: 0,
    ErkenntnisNormGeltung.ERKENNTNISNORMATIV: 1,
    ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV: 2,
}


@dataclass(frozen=True)
class ErkenntnisNormEintrag:
    norm_id: str
    erkenntnis_norm_typ: ErkenntnisNormTyp
    prozedur: ErkenntnisNormProzedur
    geltung: ErkenntnisNormGeltung
    erkenntnis_norm_weight: float
    erkenntnis_norm_tier: int
    canonical: bool
    erkenntnis_norm_ids: tuple[str, ...]
    erkenntnis_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class ErkenntnisNormSatz:
    norm_id: str
    logik_senat: LogikSenat
    normen: tuple[ErkenntnisNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ErkenntnisNormGeltung.GESPERRT)

    @property
    def erkenntnisnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ErkenntnisNormGeltung.ERKENNTNISNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is ErkenntnisNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is ErkenntnisNormGeltung.ERKENNTNISNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-erkenntnisnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-erkenntnisnormativ")


def build_erkenntnis_norm(
    logik_senat: LogikSenat | None = None,
    *,
    norm_id: str = "erkenntnis-norm",
) -> ErkenntnisNormSatz:
    if logik_senat is None:
        logik_senat = build_logik_senat(senat_id=f"{norm_id}-senat")

    normen: list[ErkenntnisNormEintrag] = []
    for parent_norm in logik_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.logik_senat_id.removeprefix(f'{logik_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.logik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.logik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ErkenntnisNormGeltung.GRUNDLEGEND_ERKENNTNISNORMATIV)
        normen.append(
            ErkenntnisNormEintrag(
                norm_id=new_id,
                erkenntnis_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                erkenntnis_norm_weight=new_weight,
                erkenntnis_norm_tier=new_tier,
                canonical=is_canonical,
                erkenntnis_norm_ids=parent_norm.logik_ids + (new_id,),
                erkenntnis_norm_tags=parent_norm.logik_tags + (f"erkenntnis-norm:{new_geltung.value}",),
            )
        )
    return ErkenntnisNormSatz(
        norm_id=norm_id,
        logik_senat=logik_senat,
        normen=tuple(normen),
    )
