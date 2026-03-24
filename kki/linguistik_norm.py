from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .linguistik_senat import LinguistikSenat, build_linguistik_senat

_GELTUNG_MAP: dict[str, "LinguistikNormGeltung"] = {}

_WEIGHT_DELTA = {
    "GESPERRT": 0.0,
    "LINGUISTISCH_NORMATIV": 0.05,
    "GRUNDLEGEND_LINGUISTISCH_NORMATIV": 0.1,
}
_TIER_DELTA = {
    "GESPERRT": 0,
    "LINGUISTISCH_NORMATIV": 1,
    "GRUNDLEGEND_LINGUISTISCH_NORMATIV": 2,
}
_TYP_MAP = {
    "GESPERRT": None,
    "LINGUISTISCH_NORMATIV": None,
    "GRUNDLEGEND_LINGUISTISCH_NORMATIV": None,
}
_PROZEDUR_MAP = {
    "GESPERRT": None,
    "LINGUISTISCH_NORMATIV": None,
    "GRUNDLEGEND_LINGUISTISCH_NORMATIV": None,
}


def _init_map() -> None:
    _GELTUNG_MAP["gesperrt"] = LinguistikNormGeltung.GESPERRT
    _GELTUNG_MAP["linguistisch-senatorisch"] = LinguistikNormGeltung.LINGUISTISCH_NORMATIV
    _GELTUNG_MAP["grundlegend-linguistisch-senatorisch"] = LinguistikNormGeltung.GRUNDLEGEND_LINGUISTISCH_NORMATIV
    _TYP_MAP["GESPERRT"] = LinguistikNormTyp.SCHUTZ_LINGUISTIKNORM
    _TYP_MAP["LINGUISTISCH_NORMATIV"] = LinguistikNormTyp.ORDNUNGS_LINGUISTIKNORM
    _TYP_MAP["GRUNDLEGEND_LINGUISTISCH_NORMATIV"] = LinguistikNormTyp.SOUVERAENITAETS_LINGUISTIKNORM
    _PROZEDUR_MAP["GESPERRT"] = LinguistikNormProzedur.NOTPROZEDUR
    _PROZEDUR_MAP["LINGUISTISCH_NORMATIV"] = LinguistikNormProzedur.REGELPROTOKOLL
    _PROZEDUR_MAP["GRUNDLEGEND_LINGUISTISCH_NORMATIV"] = LinguistikNormProzedur.PLENARPROTOKOLL


class LinguistikNormTyp(Enum):
    SCHUTZ_LINGUISTIKNORM = "schutz-linguistiknorm"
    ORDNUNGS_LINGUISTIKNORM = "ordnungs-linguistiknorm"
    SOUVERAENITAETS_LINGUISTIKNORM = "souveraenitaets-linguistiknorm"


class LinguistikNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LinguistikNormGeltung(Enum):
    GESPERRT = "gesperrt"
    LINGUISTISCH_NORMATIV = "linguistisch-normativ"
    GRUNDLEGEND_LINGUISTISCH_NORMATIV = "grundlegend-linguistisch-normativ"


@dataclass(frozen=True)
class LinguistikNormEintrag:
    norm_id: str
    linguistik_norm_typ: LinguistikNormTyp
    prozedur: LinguistikNormProzedur
    geltung: LinguistikNormGeltung
    linguistik_norm_weight: float
    linguistik_norm_tier: int
    canonical: bool
    linguistik_norm_ids: tuple[str, ...]
    linguistik_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class LinguistikNormSatz:
    norm_id: str
    linguistik_senat: LinguistikSenat
    normen: tuple[LinguistikNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is LinguistikNormGeltung.GESPERRT)

    @property
    def linguistisch_normativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is LinguistikNormGeltung.LINGUISTISCH_NORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is LinguistikNormGeltung.GRUNDLEGEND_LINGUISTISCH_NORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is LinguistikNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is LinguistikNormGeltung.LINGUISTISCH_NORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-linguistisch-normativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-linguistisch-normativ")


_init_map()

_GELTUNG_KEY_MAP = {
    LinguistikNormGeltung.GESPERRT: "GESPERRT",
    LinguistikNormGeltung.LINGUISTISCH_NORMATIV: "LINGUISTISCH_NORMATIV",
    LinguistikNormGeltung.GRUNDLEGEND_LINGUISTISCH_NORMATIV: "GRUNDLEGEND_LINGUISTISCH_NORMATIV",
}


def build_linguistik_norm(
    linguistik_senat: LinguistikSenat | None = None,
    *,
    norm_id: str = "linguistik-norm",
) -> LinguistikNormSatz:
    if linguistik_senat is None:
        linguistik_senat = build_linguistik_senat(senat_id=f"{norm_id}-senat")

    normen: list[LinguistikNormEintrag] = []
    for parent_norm in linguistik_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung.value]
        key = _GELTUNG_KEY_MAP[new_geltung]
        new_id = f"{norm_id}-{parent_norm.linguistik_senat_id.removeprefix(f'{linguistik_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[key])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[key]
        is_canonical = parent_norm.canonical and (new_geltung is LinguistikNormGeltung.GRUNDLEGEND_LINGUISTISCH_NORMATIV)
        normen.append(
            LinguistikNormEintrag(
                norm_id=new_id,
                linguistik_norm_typ=_TYP_MAP[key],
                prozedur=_PROZEDUR_MAP[key],
                geltung=new_geltung,
                linguistik_norm_weight=new_weight,
                linguistik_norm_tier=new_tier,
                canonical=is_canonical,
                linguistik_norm_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_norm_tags=parent_norm.linguistik_tags + (f"linguistik-norm:{new_geltung.value}",),
            )
        )
    return LinguistikNormSatz(
        norm_id=norm_id,
        linguistik_senat=linguistik_senat,
        normen=tuple(normen),
    )
