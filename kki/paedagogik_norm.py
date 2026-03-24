"""
#588 PaedagogikNorm — Montessori/Freire/Dewey Pädagogik Norm (*_norm pattern)

Maria Montessori (1909): Il Metodo della Pedagogia Scientifica — Freiarbeit als
  normatives Lernprinzip; vorbereitete Umgebung als pädagogische Norm; Selbst-
  korrigierende Materialien als Lernwerkzeuge; Sensible Phasen als Entwicklungs-
  norm; Achtung vor dem Kind als ethische Grundnorm des Peta-Schwarms Leitstern.
Paulo Freire (1970): Pedagogia do Oprimido — Dialog als normative Grundstruktur;
  Conscientização als Bildungsnorm; Namensgebung der Welt als Erkenntnisakt;
  kritische Bewusstseinsbildung als Norm des Lernens; Praxis als Einheit von
  Reflexion und Handlung im normativen Rahmen des Peta-Schwarms Leitstern.
John Dewey (1938): Experience and Education — Erfahrung als Bildungsnorm;
  Kontinuität und Interaktion als normative Kriterien; progressive Erziehung
  als demokratische Norm; Wachstum als Bildungszweck; reflektive Erfahrung
  als normative Grundstruktur des Peta-Schwarms Leitstern. 🎓📋
Parent: PaedagogikSenat (#587)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .paedagogik_senat import PaedagogikSenat, build_paedagogik_senat

_GELTUNG_MAP: dict[str, "PaedagogikNormGeltung"] = {}

_WEIGHT_DELTA = {
    "GESPERRT": 0.0,
    "PAEDAGOGISCH_NORMATIV": 0.05,
    "GRUNDLEGEND_PAEDAGOGISCH_NORMATIV": 0.1,
}
_TIER_DELTA = {
    "GESPERRT": 0,
    "PAEDAGOGISCH_NORMATIV": 1,
    "GRUNDLEGEND_PAEDAGOGISCH_NORMATIV": 2,
}
_TYP_MAP = {
    "GESPERRT": None,
    "PAEDAGOGISCH_NORMATIV": None,
    "GRUNDLEGEND_PAEDAGOGISCH_NORMATIV": None,
}
_PROZEDUR_MAP = {
    "GESPERRT": None,
    "PAEDAGOGISCH_NORMATIV": None,
    "GRUNDLEGEND_PAEDAGOGISCH_NORMATIV": None,
}


def _init_map() -> None:
    _GELTUNG_MAP["gesperrt"] = PaedagogikNormGeltung.GESPERRT
    _GELTUNG_MAP["paedagogisch-senatorisch"] = PaedagogikNormGeltung.PAEDAGOGISCH_NORMATIV
    _GELTUNG_MAP["grundlegend-paedagogisch-senatorisch"] = PaedagogikNormGeltung.GRUNDLEGEND_PAEDAGOGISCH_NORMATIV
    _TYP_MAP["GESPERRT"] = PaedagogikNormTyp.SCHUTZ_PAEDAGOGIKNORM
    _TYP_MAP["PAEDAGOGISCH_NORMATIV"] = PaedagogikNormTyp.ORDNUNGS_PAEDAGOGIKNORM
    _TYP_MAP["GRUNDLEGEND_PAEDAGOGISCH_NORMATIV"] = PaedagogikNormTyp.SOUVERAENITAETS_PAEDAGOGIKNORM
    _PROZEDUR_MAP["GESPERRT"] = PaedagogikNormProzedur.NOTPROZEDUR
    _PROZEDUR_MAP["PAEDAGOGISCH_NORMATIV"] = PaedagogikNormProzedur.REGELPROTOKOLL
    _PROZEDUR_MAP["GRUNDLEGEND_PAEDAGOGISCH_NORMATIV"] = PaedagogikNormProzedur.PLENARPROTOKOLL


class PaedagogikNormTyp(Enum):
    SCHUTZ_PAEDAGOGIKNORM = "schutz-paedagogiknorm"
    ORDNUNGS_PAEDAGOGIKNORM = "ordnungs-paedagogiknorm"
    SOUVERAENITAETS_PAEDAGOGIKNORM = "souveraenitaets-paedagogiknorm"


class PaedagogikNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PaedagogikNormGeltung(Enum):
    GESPERRT = "gesperrt"
    PAEDAGOGISCH_NORMATIV = "paedagogisch-normativ"
    GRUNDLEGEND_PAEDAGOGISCH_NORMATIV = "grundlegend-paedagogisch-normativ"


@dataclass(frozen=True)
class PaedagogikNormEintrag:
    norm_id: str
    paedagogik_norm_typ: PaedagogikNormTyp
    prozedur: PaedagogikNormProzedur
    geltung: PaedagogikNormGeltung
    paedagogik_norm_weight: float
    paedagogik_norm_tier: int
    canonical: bool
    paedagogik_norm_ids: tuple[str, ...]
    paedagogik_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PaedagogikNormSatz:
    norm_id: str
    paedagogik_senat: PaedagogikSenat
    normen: tuple[PaedagogikNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PaedagogikNormGeltung.GESPERRT)

    @property
    def paedagogisch_normativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PaedagogikNormGeltung.PAEDAGOGISCH_NORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PaedagogikNormGeltung.GRUNDLEGEND_PAEDAGOGISCH_NORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is PaedagogikNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is PaedagogikNormGeltung.PAEDAGOGISCH_NORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-paedagogisch-normativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-paedagogisch-normativ")


_init_map()

_GELTUNG_KEY_MAP = {
    PaedagogikNormGeltung.GESPERRT: "GESPERRT",
    PaedagogikNormGeltung.PAEDAGOGISCH_NORMATIV: "PAEDAGOGISCH_NORMATIV",
    PaedagogikNormGeltung.GRUNDLEGEND_PAEDAGOGISCH_NORMATIV: "GRUNDLEGEND_PAEDAGOGISCH_NORMATIV",
}


def build_paedagogik_norm(
    paedagogik_senat: PaedagogikSenat | None = None,
    *,
    norm_id: str = "paedagogik-norm",
) -> PaedagogikNormSatz:
    if paedagogik_senat is None:
        paedagogik_senat = build_paedagogik_senat(senat_id=f"{norm_id}-senat")

    normen: list[PaedagogikNormEintrag] = []
    for parent_norm in paedagogik_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung.value]
        key = _GELTUNG_KEY_MAP[new_geltung]
        new_id = f"{norm_id}-{parent_norm.paedagogik_senat_id.removeprefix(f'{paedagogik_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[key])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[key]
        is_canonical = parent_norm.canonical and (new_geltung is PaedagogikNormGeltung.GRUNDLEGEND_PAEDAGOGISCH_NORMATIV)
        normen.append(
            PaedagogikNormEintrag(
                norm_id=new_id,
                paedagogik_norm_typ=_TYP_MAP[key],
                prozedur=_PROZEDUR_MAP[key],
                geltung=new_geltung,
                paedagogik_norm_weight=new_weight,
                paedagogik_norm_tier=new_tier,
                canonical=is_canonical,
                paedagogik_norm_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_norm_tags=parent_norm.paedagogik_tags + (f"paedagogik-norm:{new_geltung.value}",),
            )
        )
    return PaedagogikNormSatz(
        norm_id=norm_id,
        paedagogik_senat=paedagogik_senat,
        normen=tuple(normen),
    )
