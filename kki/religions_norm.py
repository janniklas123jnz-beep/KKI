from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .religionsphilosophie_senat import ReligionsphilosophieSenat, build_religionsphilosophie_senat

_GELTUNG_MAP: dict[str, "ReligionsNormGeltung"] = {}

_WEIGHT_DELTA = {
    "GESPERRT": 0.0,
    "RELIGIOES_NORMATIV": 0.05,
    "GRUNDLEGEND_RELIGIOES_NORMATIV": 0.1,
}
_TIER_DELTA = {
    "GESPERRT": 0,
    "RELIGIOES_NORMATIV": 1,
    "GRUNDLEGEND_RELIGIOES_NORMATIV": 2,
}
_TYP_MAP = {
    "GESPERRT": None,
    "RELIGIOES_NORMATIV": None,
    "GRUNDLEGEND_RELIGIOES_NORMATIV": None,
}
_PROZEDUR_MAP = {
    "GESPERRT": None,
    "RELIGIOES_NORMATIV": None,
    "GRUNDLEGEND_RELIGIOES_NORMATIV": None,
}


def _init_map() -> None:
    _GELTUNG_MAP["gesperrt"] = ReligionsNormGeltung.GESPERRT
    _GELTUNG_MAP["religionsphilosophisch"] = ReligionsNormGeltung.RELIGIOES_NORMATIV
    _GELTUNG_MAP["grundlegend-religionsphilosophisch"] = ReligionsNormGeltung.GRUNDLEGEND_RELIGIOES_NORMATIV
    _TYP_MAP["GESPERRT"] = ReligionsNormTyp.SCHUTZ_RELIGIONSNORM
    _TYP_MAP["RELIGIOES_NORMATIV"] = ReligionsNormTyp.ORDNUNGS_RELIGIONSNORM
    _TYP_MAP["GRUNDLEGEND_RELIGIOES_NORMATIV"] = ReligionsNormTyp.SOUVERAENITAETS_RELIGIONSNORM
    _PROZEDUR_MAP["GESPERRT"] = ReligionsNormProzedur.NOTPROZEDUR
    _PROZEDUR_MAP["RELIGIOES_NORMATIV"] = ReligionsNormProzedur.REGELPROTOKOLL
    _PROZEDUR_MAP["GRUNDLEGEND_RELIGIOES_NORMATIV"] = ReligionsNormProzedur.PLENARPROTOKOLL


class ReligionsNormTyp(Enum):
    SCHUTZ_RELIGIONSNORM = "schutz-religionsnorm"
    ORDNUNGS_RELIGIONSNORM = "ordnungs-religionsnorm"
    SOUVERAENITAETS_RELIGIONSNORM = "souveraenitaets-religionsnorm"


class ReligionsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ReligionsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    RELIGIOES_NORMATIV = "religioes-normativ"
    GRUNDLEGEND_RELIGIOES_NORMATIV = "grundlegend-religioes-normativ"


@dataclass(frozen=True)
class ReligionsNormEintrag:
    norm_id: str
    religions_norm_typ: ReligionsNormTyp
    prozedur: ReligionsNormProzedur
    geltung: ReligionsNormGeltung
    religions_norm_weight: float
    religions_norm_tier: int
    canonical: bool
    religions_norm_ids: tuple[str, ...]
    religions_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class ReligionsNormSatz:
    norm_id: str
    religionsphilosophie_senat: ReligionsphilosophieSenat
    normen: tuple[ReligionsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ReligionsNormGeltung.GESPERRT)

    @property
    def religioes_normativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ReligionsNormGeltung.RELIGIOES_NORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is ReligionsNormGeltung.GRUNDLEGEND_RELIGIOES_NORMATIV)


_GELTUNG_KEY_MAP = {
    ReligionsNormGeltung.GESPERRT: "GESPERRT",
    ReligionsNormGeltung.RELIGIOES_NORMATIV: "RELIGIOES_NORMATIV",
    ReligionsNormGeltung.GRUNDLEGEND_RELIGIOES_NORMATIV: "GRUNDLEGEND_RELIGIOES_NORMATIV",
}

_init_map()


def build_religions_norm(
    religionsphilosophie_senat: ReligionsphilosophieSenat | None = None,
    *,
    norm_id: str = "religions-norm",
) -> ReligionsNormSatz:
    if religionsphilosophie_senat is None:
        religionsphilosophie_senat = build_religionsphilosophie_senat(
            senat_id=f"{norm_id}-senat"
        )

    eintraege: list[ReligionsNormEintrag] = []
    for parent_norm in religionsphilosophie_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung.value]
        key = _GELTUNG_KEY_MAP[new_geltung]
        new_id = f"{norm_id}-{parent_norm.religionsphilosophie_senat_id.removeprefix(f'{religionsphilosophie_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[key])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[key]
        is_canonical = parent_norm.canonical and (new_geltung is ReligionsNormGeltung.GRUNDLEGEND_RELIGIOES_NORMATIV)
        eintraege.append(
            ReligionsNormEintrag(
                norm_id=new_id,
                religions_norm_typ=_TYP_MAP[key],
                prozedur=_PROZEDUR_MAP[key],
                geltung=new_geltung,
                religions_norm_weight=new_weight,
                religions_norm_tier=new_tier,
                canonical=is_canonical,
                religions_norm_ids=parent_norm.religions_ids + (new_id,),
                religions_norm_tags=parent_norm.religions_tags + (f"religions-norm:{new_geltung.value}",),
            )
        )
    return ReligionsNormSatz(
        norm_id=norm_id,
        religionsphilosophie_senat=religionsphilosophie_senat,
        normen=tuple(eintraege),
    )
