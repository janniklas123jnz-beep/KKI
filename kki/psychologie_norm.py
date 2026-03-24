from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .psychologie_senat import PsychologieSenat, build_psychologie_senat

_GELTUNG_MAP: dict[str, "PsychologieNormGeltung"] = {}

_WEIGHT_DELTA = {
    "GESPERRT": 0.0,
    "PSYCHOLOGISCH_NORMATIV": 0.05,
    "GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV": 0.1,
}
_TIER_DELTA = {
    "GESPERRT": 0,
    "PSYCHOLOGISCH_NORMATIV": 1,
    "GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV": 2,
}
_TYP_MAP = {
    "GESPERRT": None,
    "PSYCHOLOGISCH_NORMATIV": None,
    "GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV": None,
}
_PROZEDUR_MAP = {
    "GESPERRT": None,
    "PSYCHOLOGISCH_NORMATIV": None,
    "GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV": None,
}


def _init_map() -> None:
    _GELTUNG_MAP["gesperrt"] = PsychologieNormGeltung.GESPERRT
    _GELTUNG_MAP["psychologisch-senatorisch"] = PsychologieNormGeltung.PSYCHOLOGISCH_NORMATIV
    _GELTUNG_MAP["grundlegend-psychologisch-senatorisch"] = PsychologieNormGeltung.GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV
    _TYP_MAP["GESPERRT"] = PsychologieNormTyp.SCHUTZ_PSYCHOLOGIENORM
    _TYP_MAP["PSYCHOLOGISCH_NORMATIV"] = PsychologieNormTyp.ORDNUNGS_PSYCHOLOGIENORM
    _TYP_MAP["GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV"] = PsychologieNormTyp.SOUVERAENITAETS_PSYCHOLOGIENORM
    _PROZEDUR_MAP["GESPERRT"] = PsychologieNormProzedur.NOTPROZEDUR
    _PROZEDUR_MAP["PSYCHOLOGISCH_NORMATIV"] = PsychologieNormProzedur.REGELPROTOKOLL
    _PROZEDUR_MAP["GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV"] = PsychologieNormProzedur.PLENARPROTOKOLL


class PsychologieNormTyp(Enum):
    SCHUTZ_PSYCHOLOGIENORM = "schutz-psychologienorm"
    ORDNUNGS_PSYCHOLOGIENORM = "ordnungs-psychologienorm"
    SOUVERAENITAETS_PSYCHOLOGIENORM = "souveraenitaets-psychologienorm"


class PsychologieNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PsychologieNormGeltung(Enum):
    GESPERRT = "gesperrt"
    PSYCHOLOGISCH_NORMATIV = "psychologisch-normativ"
    GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV = "grundlegend-psychologisch-normativ"


@dataclass(frozen=True)
class PsychologieNormEintrag:
    norm_id: str
    psychologie_norm_typ: PsychologieNormTyp
    prozedur: PsychologieNormProzedur
    geltung: PsychologieNormGeltung
    psychologie_norm_weight: float
    psychologie_norm_tier: int
    canonical: bool
    psychologie_norm_ids: tuple[str, ...]
    psychologie_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PsychologieNormSatz:
    norm_id: str
    psychologie_senat: PsychologieSenat
    normen: tuple[PsychologieNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PsychologieNormGeltung.GESPERRT)

    @property
    def psychologisch_normativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PsychologieNormGeltung.PSYCHOLOGISCH_NORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PsychologieNormGeltung.GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is PsychologieNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is PsychologieNormGeltung.PSYCHOLOGISCH_NORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-psychologisch-normativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-psychologisch-normativ")


_init_map()

_GELTUNG_KEY_MAP = {
    PsychologieNormGeltung.GESPERRT: "GESPERRT",
    PsychologieNormGeltung.PSYCHOLOGISCH_NORMATIV: "PSYCHOLOGISCH_NORMATIV",
    PsychologieNormGeltung.GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV: "GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV",
}


def build_psychologie_norm(
    psychologie_senat: PsychologieSenat | None = None,
    *,
    norm_id: str = "psychologie-norm",
) -> PsychologieNormSatz:
    if psychologie_senat is None:
        psychologie_senat = build_psychologie_senat(senat_id=f"{norm_id}-senat")

    normen: list[PsychologieNormEintrag] = []
    for parent_norm in psychologie_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung.value]
        key = _GELTUNG_KEY_MAP[new_geltung]
        new_id = f"{norm_id}-{parent_norm.psychologie_senat_id.removeprefix(f'{psychologie_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[key])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[key]
        is_canonical = parent_norm.canonical and (new_geltung is PsychologieNormGeltung.GRUNDLEGEND_PSYCHOLOGISCH_NORMATIV)
        normen.append(
            PsychologieNormEintrag(
                norm_id=new_id,
                psychologie_norm_typ=_TYP_MAP[key],
                prozedur=_PROZEDUR_MAP[key],
                geltung=new_geltung,
                psychologie_norm_weight=new_weight,
                psychologie_norm_tier=new_tier,
                canonical=is_canonical,
                psychologie_norm_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_norm_tags=parent_norm.psychologie_tags + (f"psychologie-norm:{new_geltung.value}",),
            )
        )
    return PsychologieNormSatz(
        norm_id=norm_id,
        psychologie_senat=psychologie_senat,
        normen=tuple(normen),
    )
