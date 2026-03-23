"""
#578 KunstNorm — Bourdieu/Danto/Dickie Kunstwissenschaft Norm (*_norm pattern)

Pierre Bourdieu (1992): Les Règles de l'art — literarisches Feld als autonomes
  Produktionsfeld; ästhetische Disposition als klassenkulturelle Norm; Illusio
  als Einsatz im Kunstfeld; symbolisches Kapital als Anerkennung; Habitus als
  inkorporierte Norm des Peta-Schwarms Leitstern.
Arthur Danto (1964): The Artworld — Kunstwelt als institutioneller Kontext;
  Interpretationsrahmen als Konstituens von Kunst; Transfiguration des Gewöhnlichen
  als ästhetischer Akt; Ende der Kunstgeschichte als Pluralismus; historisches
  Bewusstsein als normative Voraussetzung Leitsterns.
George Dickie (1974): Art and the Aesthetic — Institutionentheorie der Kunst;
  Kunstwerk als Kandidat zur Wertschätzung; Artworld als normativer Rahmen;
  ästhetische Erfahrung als nicht-privilegierter Begriff; Definition von Kunst
  als soziale Norm im Peta-Schwarm Leitstern. 🎨🏛️
Parent: KunstsoziologieSenat (#577)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kunstsoziologie_senat import KunstsoziologieSenat, build_kunstsoziologie_senat

_GELTUNG_MAP: dict[str, "KunstNormGeltung"] = {}

_WEIGHT_DELTA = {
    "GESPERRT": 0.0,
    "KUNSTNORMATIV": 0.05,
    "GRUNDLEGEND_KUNSTNORMATIV": 0.1,
}
_TIER_DELTA = {
    "GESPERRT": 0,
    "KUNSTNORMATIV": 1,
    "GRUNDLEGEND_KUNSTNORMATIV": 2,
}
_TYP_MAP = {
    "GESPERRT": None,
    "KUNSTNORMATIV": None,
    "GRUNDLEGEND_KUNSTNORMATIV": None,
}
_PROZEDUR_MAP = {
    "GESPERRT": None,
    "KUNSTNORMATIV": None,
    "GRUNDLEGEND_KUNSTNORMATIV": None,
}


def _init_map() -> None:
    _GELTUNG_MAP["gesperrt"] = KunstNormGeltung.GESPERRT
    _GELTUNG_MAP["kunstsoziologisch"] = KunstNormGeltung.KUNSTNORMATIV
    _GELTUNG_MAP["grundlegend-kunstsoziologisch"] = KunstNormGeltung.GRUNDLEGEND_KUNSTNORMATIV
    _TYP_MAP["GESPERRT"] = KunstNormTyp.SCHUTZ_KUNSTNORM
    _TYP_MAP["KUNSTNORMATIV"] = KunstNormTyp.ORDNUNGS_KUNSTNORM
    _TYP_MAP["GRUNDLEGEND_KUNSTNORMATIV"] = KunstNormTyp.SOUVERAENITAETS_KUNSTNORM
    _PROZEDUR_MAP["GESPERRT"] = KunstNormProzedur.NOTPROZEDUR
    _PROZEDUR_MAP["KUNSTNORMATIV"] = KunstNormProzedur.REGELPROTOKOLL
    _PROZEDUR_MAP["GRUNDLEGEND_KUNSTNORMATIV"] = KunstNormProzedur.PLENARPROTOKOLL


class KunstNormTyp(Enum):
    SCHUTZ_KUNSTNORM = "schutz-kunstnorm"
    ORDNUNGS_KUNSTNORM = "ordnungs-kunstnorm"
    SOUVERAENITAETS_KUNSTNORM = "souveraenitaets-kunstnorm"


class KunstNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KunstNormGeltung(Enum):
    GESPERRT = "gesperrt"
    KUNSTNORMATIV = "kunstnormativ"
    GRUNDLEGEND_KUNSTNORMATIV = "grundlegend-kunstnormativ"


@dataclass(frozen=True)
class KunstNormEintrag:
    norm_id: str
    kunst_norm_typ: KunstNormTyp
    prozedur: KunstNormProzedur
    geltung: KunstNormGeltung
    kunst_norm_weight: float
    kunst_norm_tier: int
    canonical: bool
    kunst_norm_ids: tuple[str, ...]
    kunst_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class KunstNormSatz:
    norm_id: str
    kunstsoziologie_senat: KunstsoziologieSenat
    normen: tuple[KunstNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KunstNormGeltung.GESPERRT)

    @property
    def kunstnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KunstNormGeltung.KUNSTNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KunstNormGeltung.GRUNDLEGEND_KUNSTNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is KunstNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is KunstNormGeltung.KUNSTNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-kunstnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-kunstnormativ")


_init_map()

_GELTUNG_KEY_MAP = {
    KunstNormGeltung.GESPERRT: "GESPERRT",
    KunstNormGeltung.KUNSTNORMATIV: "KUNSTNORMATIV",
    KunstNormGeltung.GRUNDLEGEND_KUNSTNORMATIV: "GRUNDLEGEND_KUNSTNORMATIV",
}


def build_kunst_norm(
    kunstsoziologie_senat: KunstsoziologieSenat | None = None,
    *,
    norm_id: str = "kunst-norm",
) -> KunstNormSatz:
    if kunstsoziologie_senat is None:
        kunstsoziologie_senat = build_kunstsoziologie_senat(senat_id=f"{norm_id}-senat")

    normen: list[KunstNormEintrag] = []
    for parent_norm in kunstsoziologie_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung.value]
        key = _GELTUNG_KEY_MAP[new_geltung]
        new_id = f"{norm_id}-{parent_norm.kunstsoziologie_senat_id.removeprefix(f'{kunstsoziologie_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[key])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[key]
        is_canonical = parent_norm.canonical and (new_geltung is KunstNormGeltung.GRUNDLEGEND_KUNSTNORMATIV)
        normen.append(
            KunstNormEintrag(
                norm_id=new_id,
                kunst_norm_typ=_TYP_MAP[key],
                prozedur=_PROZEDUR_MAP[key],
                geltung=new_geltung,
                kunst_norm_weight=new_weight,
                kunst_norm_tier=new_tier,
                canonical=is_canonical,
                kunst_norm_ids=parent_norm.kunst_ids + (new_id,),
                kunst_norm_tags=parent_norm.kunst_tags + (f"kunst-norm:{new_geltung.value}",),
            )
        )
    return KunstNormSatz(
        norm_id=norm_id,
        kunstsoziologie_senat=kunstsoziologie_senat,
        normen=tuple(normen),
    )
