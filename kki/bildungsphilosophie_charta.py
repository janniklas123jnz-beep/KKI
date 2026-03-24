"""
#589 BildungsphilosophieCharta — Humboldt/Adorno/Nussbaum Bildungsphilosophie Charta

Wilhelm von Humboldt (1793): Theorie der Bildung des Menschen — Bildung als
  Entfaltung aller Kräfte; Wechselwirkung von Ich und Welt als Bildungsprozess;
  Allgemeinbildung als Ziel jenseits der Berufsausbildung; sprachliche Welterschließung
  als Bildungsmedium; Freiheit der Wissenschaft als Verfassungsprinzip Leitsterns.
Theodor W. Adorno (1959): Theorie der Halbbildung — Entfremdung als Bildungsproblem;
  Mündigkeit als Bildungsziel; Auschwitz nie wieder als kategorischer Imperativ der
  Bildung; Selbstreflexion als kritische Bildungspraktik; Widerstand gegen Anpassung
  als pädagogische Norm im Peta-Schwarm Leitstern.
Martha Nussbaum (2010): Not for Profit — Geisteswissenschaften als Grundlage der
  Demokratie; narrative Einbildungskraft als Bildungsziel; Weltbürgerschaft als
  kosmopolitisches Bildungsideal; sokratisches Denken als demokratische Bildungsform;
  Würde als universales Bildungsfundament des Peta-Schwarms Leitstern. 🎓🌍
Parent: PaedagogikNormSatz (#588)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .paedagogik_norm import PaedagogikNormGeltung, PaedagogikNormSatz, build_paedagogik_norm

_WEIGHT_DELTA: dict["BildungsphilosophieChartaGeltung", float] = {}
_TIER_DELTA: dict["BildungsphilosophieChartaGeltung", int] = {}
_TYP_MAP: dict["BildungsphilosophieChartaGeltung", "BildungsphilosophieChartaTyp"] = {}
_PROZEDUR_MAP: dict["BildungsphilosophieChartaGeltung", "BildungsphilosophieChartaProzedur"] = {}
_GELTUNG_MAP: dict[PaedagogikNormGeltung, "BildungsphilosophieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BildungsphilosophieChartaGeltung.GESPERRT: 0.0,
        BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH: 0.05,
        BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        BildungsphilosophieChartaGeltung.GESPERRT: 0,
        BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH: 1,
        BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH: 2,
    })
    _TYP_MAP.update({
        BildungsphilosophieChartaGeltung.GESPERRT: BildungsphilosophieChartaTyp.SCHUTZ_BILDUNGSPHILOSOPHIE,
        BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH: BildungsphilosophieChartaTyp.ORDNUNGS_BILDUNGSPHILOSOPHIE,
        BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH: BildungsphilosophieChartaTyp.SOUVERAENITAETS_BILDUNGSPHILOSOPHIE,
    })
    _PROZEDUR_MAP.update({
        BildungsphilosophieChartaGeltung.GESPERRT: BildungsphilosophieChartaProzedur.NOTPROZEDUR,
        BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH: BildungsphilosophieChartaProzedur.REGELPROTOKOLL,
        BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH: BildungsphilosophieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        PaedagogikNormGeltung.GESPERRT: BildungsphilosophieChartaGeltung.GESPERRT,
        PaedagogikNormGeltung.PAEDAGOGISCH_NORMATIV: BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH,
        PaedagogikNormGeltung.GRUNDLEGEND_PAEDAGOGISCH_NORMATIV: BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH,
    })


class BildungsphilosophieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    BILDUNGSPHILOSOPHISCH = "bildungsphilosophisch"
    GRUNDLEGEND_BILDUNGSPHILOSOPHISCH = "grundlegend-bildungsphilosophisch"


class BildungsphilosophieChartaTyp(Enum):
    SCHUTZ_BILDUNGSPHILOSOPHIE = "schutz-bildungsphilosophie"
    ORDNUNGS_BILDUNGSPHILOSOPHIE = "ordnungs-bildungsphilosophie"
    SOUVERAENITAETS_BILDUNGSPHILOSOPHIE = "souveraenitaets-bildungsphilosophie"


class BildungsphilosophieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class BildungsphilosophieChartaNorm:
    bildungsphilosophie_charta_id: str
    paedagogik_typ: BildungsphilosophieChartaTyp
    prozedur: BildungsphilosophieChartaProzedur
    geltung: BildungsphilosophieChartaGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class BildungsphilosophieCharta:
    charta_id: str
    paedagogik_norm: PaedagogikNormSatz
    normen: tuple[BildungsphilosophieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bildungsphilosophie_charta_id for n in self.normen if n.geltung is BildungsphilosophieChartaGeltung.GESPERRT)

    @property
    def bildungsphilosophisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bildungsphilosophie_charta_id for n in self.normen if n.geltung is BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bildungsphilosophie_charta_id for n in self.normen if n.geltung is BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is BildungsphilosophieChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-bildungsphilosophisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-bildungsphilosophisch")


_init_map()


def build_bildungsphilosophie_charta(
    paedagogik_norm: PaedagogikNormSatz | None = None,
    *,
    charta_id: str = "bildungsphilosophie-charta",
) -> BildungsphilosophieCharta:
    if paedagogik_norm is None:
        paedagogik_norm = build_paedagogik_norm(norm_id=f"{charta_id}-norm")

    normen: list[BildungsphilosophieChartaNorm] = []
    for parent_norm in paedagogik_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{paedagogik_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH)
        normen.append(
            BildungsphilosophieChartaNorm(
                bildungsphilosophie_charta_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_norm_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_norm_tags + (f"bildungsphilosophie-charta:{new_geltung.value}",),
            )
        )
    return BildungsphilosophieCharta(
        charta_id=charta_id,
        paedagogik_norm=paedagogik_norm,
        normen=tuple(normen),
    )
