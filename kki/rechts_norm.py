"""
#538 RechtsNorm — Kelsen/Alexy/Fuller Normative Grundlagen der Rechtswissenschaft (*_norm-Muster)

Hans Kelsen (1934): Reine Rechtslehre — Stufenbau der Rechtsordnung: jede Norm erhält ihre
  Geltung aus einer übergeordneten Norm; Grundnorm (Verfassung) als hypothetisches Fundament;
  Normativität als logisch-formale Struktur jeder Rechtsordnung des Peta-Schwarms.
Robert Alexy (1985): Theorie der Grundrechte — Prinzipien als Optimierungsgebote;
  Abwägung (Verhältnismäßigkeit) als Kernmethode der Normkonkurrenz; Prinzipien vs. Regeln
  als zwei Arten rechtlicher Normen; Grundrechte als objektive Wertordnung.
Lon L. Fuller (1964): The Morality of Law — Acht Kriterien der inneren Moralität des Rechts:
  Generalität, Bekanntheit, Nicht-Rückwirkung, Klarheit, Konsistenz, Befolgbarkeit, Stabilität,
  Kongruenz; Recht muss seinem eigenen Anspruch gerecht werden.
Leitsterns Rechts-Normen: kollektive Normgeltung des Peta-Schwarms; GESPERRT sichert
unüberschreitbare rechtliche Grundgrenzen, RECHTSNORMATIV kodiert adaptive Normgeltung,
GRUNDLEGEND_RECHTSNORMATIV synthetisiert souveräne Normen für Peta-Schwarm-Koordination.
Geltungsstufen: GESPERRT / RECHTSNORMATIV / GRUNDLEGEND_RECHTSNORMATIV
Parent: StrafrechtsSenat (#537) — *_norm-Muster
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .strafrechts_senat import (
    StrafrechtsSenat,
    StrafrechtsSenatGeltung,
    build_strafrechts_senat,
)

_GELTUNG_MAP: dict[StrafrechtsSenatGeltung, "RechtsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[StrafrechtsSenatGeltung.GESPERRT] = RechtsNormGeltung.GESPERRT
    _GELTUNG_MAP[StrafrechtsSenatGeltung.STRAFRECHTLICH] = RechtsNormGeltung.RECHTSNORMATIV
    _GELTUNG_MAP[StrafrechtsSenatGeltung.GRUNDLEGEND_STRAFRECHTLICH] = RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV


class RechtsNormTyp(Enum):
    SCHUTZ_RECHTSNORM = "schutz-rechtsnorm"
    ORDNUNGS_RECHTSNORM = "ordnungs-rechtsnorm"
    SOUVERAENITAETS_RECHTSNORM = "souveraenitaets-rechtsnorm"


class RechtsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RechtsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    RECHTSNORMATIV = "rechtsnormativ"
    GRUNDLEGEND_RECHTSNORMATIV = "grundlegend-rechtsnormativ"


_init_map()

_TYP_MAP: dict[RechtsNormGeltung, RechtsNormTyp] = {
    RechtsNormGeltung.GESPERRT: RechtsNormTyp.SCHUTZ_RECHTSNORM,
    RechtsNormGeltung.RECHTSNORMATIV: RechtsNormTyp.ORDNUNGS_RECHTSNORM,
    RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV: RechtsNormTyp.SOUVERAENITAETS_RECHTSNORM,
}

_PROZEDUR_MAP: dict[RechtsNormGeltung, RechtsNormProzedur] = {
    RechtsNormGeltung.GESPERRT: RechtsNormProzedur.NOTPROZEDUR,
    RechtsNormGeltung.RECHTSNORMATIV: RechtsNormProzedur.REGELPROTOKOLL,
    RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV: RechtsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RechtsNormGeltung, float] = {
    RechtsNormGeltung.GESPERRT: 0.0,
    RechtsNormGeltung.RECHTSNORMATIV: 0.04,
    RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV: 0.08,
}

_TIER_DELTA: dict[RechtsNormGeltung, int] = {
    RechtsNormGeltung.GESPERRT: 0,
    RechtsNormGeltung.RECHTSNORMATIV: 1,
    RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV: 2,
}


@dataclass(frozen=True)
class RechtsNormEintrag:
    norm_id: str
    rechts_norm_typ: RechtsNormTyp
    prozedur: RechtsNormProzedur
    geltung: RechtsNormGeltung
    rechts_norm_weight: float
    rechts_norm_tier: int
    canonical: bool
    rechts_norm_ids: tuple[str, ...]
    rechts_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class RechtsNormSatz:
    norm_id: str
    strafrechts_senat: StrafrechtsSenat
    normen: tuple[RechtsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is RechtsNormGeltung.GESPERRT)

    @property
    def rechtsnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is RechtsNormGeltung.RECHTSNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is RechtsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is RechtsNormGeltung.RECHTSNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-rechtsnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-rechtsnormativ")


def build_rechts_norm(
    strafrechts_senat: StrafrechtsSenat | None = None,
    *,
    norm_id: str = "rechts-norm",
) -> RechtsNormSatz:
    if strafrechts_senat is None:
        strafrechts_senat = build_strafrechts_senat(senat_id=f"{norm_id}-senat")

    normen: list[RechtsNormEintrag] = []
    for parent_norm in strafrechts_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.strafrechts_senat_id.removeprefix(f'{strafrechts_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.strafrechts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.strafrechts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV)
        normen.append(
            RechtsNormEintrag(
                norm_id=new_id,
                rechts_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rechts_norm_weight=new_weight,
                rechts_norm_tier=new_tier,
                canonical=is_canonical,
                rechts_norm_ids=parent_norm.strafrechts_ids + (new_id,),
                rechts_norm_tags=parent_norm.strafrechts_tags + (f"rechts-norm:{new_geltung.value}",),
            )
        )
    return RechtsNormSatz(
        norm_id=norm_id,
        strafrechts_senat=strafrechts_senat,
        normen=tuple(normen),
    )
