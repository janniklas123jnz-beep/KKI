"""
#472 OntologieRegister — Aristoteles/Heidegger: Sein und Seiendes, Kategorientheorie.
Ontologie als Grundwissenschaft untersucht das Seiende als Seiendes (Aristoteles'
Erste Philosophie) und die Frage nach dem Sein selbst (Heideggers Fundamentalontologie).
Die Kategorientheorie klassifiziert das Seiende in Substanz, Qualität, Quantität und
Relation. Leitsterns Terra-Schwarm strukturiert ontologische Schichten: GESPERRT sichert
Basiskategorien, ONTOLOGISCH ermöglicht kategoriale Differenzierung, GRUNDLEGEND_ONTOLOGISCH
synthetisiert Seins- und Seiendheitsstrukturen.
Parent: ErkenntnisFeld (#471)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .erkenntnis_feld import (
    ErkenntnisFeld,
    ErkenntnisFeldGeltung,
    build_erkenntnis_feld,
)

_GELTUNG_MAP: dict[ErkenntnisFeldGeltung, "OntologieRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ErkenntnisFeldGeltung.GESPERRT] = OntologieRegisterGeltung.GESPERRT
    _GELTUNG_MAP[ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH] = OntologieRegisterGeltung.ONTOLOGISCH
    _GELTUNG_MAP[ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH] = OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH


class OntologieRegisterTyp(Enum):
    SCHUTZ_ONTOLOGIE = "schutz-ontologie"
    ORDNUNGS_ONTOLOGIE = "ordnungs-ontologie"
    SOUVERAENITAETS_ONTOLOGIE = "souveraenitaets-ontologie"


class OntologieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class OntologieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    ONTOLOGISCH = "ontologisch"
    GRUNDLEGEND_ONTOLOGISCH = "grundlegend-ontologisch"


_init_map()

_TYP_MAP = {
    OntologieRegisterGeltung.GESPERRT: OntologieRegisterTyp.SCHUTZ_ONTOLOGIE,
    OntologieRegisterGeltung.ONTOLOGISCH: OntologieRegisterTyp.ORDNUNGS_ONTOLOGIE,
    OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH: OntologieRegisterTyp.SOUVERAENITAETS_ONTOLOGIE,
}
_PROZEDUR_MAP = {
    OntologieRegisterGeltung.GESPERRT: OntologieRegisterProzedur.NOTPROZEDUR,
    OntologieRegisterGeltung.ONTOLOGISCH: OntologieRegisterProzedur.REGELPROTOKOLL,
    OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH: OntologieRegisterProzedur.PLENARPROTOKOLL,
}
_WEIGHT_DELTA = {
    OntologieRegisterGeltung.GESPERRT: 0.0,
    OntologieRegisterGeltung.ONTOLOGISCH: 0.04,
    OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH: 0.08,
}
_TIER_DELTA = {
    OntologieRegisterGeltung.GESPERRT: 0,
    OntologieRegisterGeltung.ONTOLOGISCH: 1,
    OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH: 2,
}


@dataclass(frozen=True)
class OntologieRegisterNorm:
    ontologie_register_id: str
    ontologie_typ: OntologieRegisterTyp
    prozedur: OntologieRegisterProzedur
    geltung: OntologieRegisterGeltung
    ontologie_weight: float
    ontologie_tier: int
    canonical: bool
    ontologie_ids: tuple[str, ...]
    ontologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class OntologieRegister:
    register_id: str
    erkenntnis_feld: ErkenntnisFeld
    normen: tuple[OntologieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ontologie_register_id for n in self.normen if n.geltung is OntologieRegisterGeltung.GESPERRT)

    @property
    def ontologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ontologie_register_id for n in self.normen if n.geltung is OntologieRegisterGeltung.ONTOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ontologie_register_id for n in self.normen if n.geltung is OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH)

    @property
    def register_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is OntologieRegisterGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is OntologieRegisterGeltung.ONTOLOGISCH for n in self.normen):
            return SimpleNamespace(status="register-ontologisch")
        return SimpleNamespace(status="register-grundlegend-ontologisch")


def build_ontologie_register(
    erkenntnis_feld: ErkenntnisFeld | None = None,
    *,
    register_id: str = "ontologie-register",
) -> OntologieRegister:
    if erkenntnis_feld is None:
        erkenntnis_feld = build_erkenntnis_feld(feld_id=f"{register_id}-feld")
    normen: list[OntologieRegisterNorm] = []
    for parent_norm in erkenntnis_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.erkenntnis_feld_id.removeprefix(f'{erkenntnis_feld.feld_id}-')}"
        is_canonical = parent_norm.canonical and (new_geltung is OntologieRegisterGeltung.GRUNDLEGEND_ONTOLOGISCH)
        normen.append(OntologieRegisterNorm(
            ontologie_register_id=new_id,
            ontologie_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            ontologie_weight=round(min(1.0, parent_norm.erkenntnis_weight + _WEIGHT_DELTA[new_geltung]), 3),
            ontologie_tier=parent_norm.erkenntnis_tier + _TIER_DELTA[new_geltung],
            canonical=is_canonical,
            ontologie_ids=parent_norm.erkenntnis_ids + (new_id,),
            ontologie_tags=parent_norm.erkenntnis_tags + (f"ontologie-register:{new_geltung.value}",),
        ))
    return OntologieRegister(register_id=register_id, erkenntnis_feld=erkenntnis_feld, normen=tuple(normen))
