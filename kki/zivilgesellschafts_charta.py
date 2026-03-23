"""
#519 ZivilgesellschaftsCharta — Tocqueville/Putnam/Habermas Zivilgesellschaft & Partizipation

Alexis de Tocqueville (1835): Über die Demokratie in Amerika — freiwillige Assoziationen als
  Schule demokratischer Tugend; Zivilgesellschaft als Gegengewicht zur Tyrannei der Mehrheit.
Robert Putnam (1993): Making Democracy Work — Sozialkapital als Vertrauen, Normen und Netzwerke;
  Civic Community und demokratische Performanz; Bridging vs. Bonding Social Capital.
Jürgen Habermas (1962): Strukturwandel der Öffentlichkeit — bürgerliche Öffentlichkeit als
  Medium diskursiver Legitimation; deliberative Demokratie durch öffentlichen Vernunftgebrauch.
Chantal Mouffe (1993): The Return of the Political — agonistische Demokratie; Pluralismus und
  Konflikt als konstitutiv; Zivilgesellschaft als Feld politischer Identitätsformation.
Leitsterns Peta-Schwarm verankert Zivilgesellschaft als koordinative Kraft: GESPERRT schützt
partizipative Grundrechte, ZIVILGESELLSCHAFTLICH kodiert adaptive Bürgerkoordination zwischen
Millionen Agenten, GRUNDLEGEND_ZIVILGESELLSCHAFTLICH synthetisiert souveräne demokratische
Teilhabe im Peta-Schwarm-Gefüge. 🏙️
Parent: PolitikNorm (#518)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .politik_norm import (
    PolitikNormSatz,
    PolitikNormGeltung,
    build_politik_norm,
)

_WEIGHT_DELTA: dict["ZivilgesellschaftsChartaGeltung", float] = {}
_TIER_DELTA: dict["ZivilgesellschaftsChartaGeltung", int] = {}
_TYP_MAP: dict["ZivilgesellschaftsChartaGeltung", "ZivilgesellschaftsChartaTyp"] = {}
_PROZEDUR_MAP: dict["ZivilgesellschaftsChartaGeltung", "ZivilgesellschaftsChartaProzedur"] = {}
_GELTUNG_MAP: dict[PolitikNormGeltung, "ZivilgesellschaftsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ZivilgesellschaftsChartaGeltung.GESPERRT: 0.0,
        ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH: 0.05,
        ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        ZivilgesellschaftsChartaGeltung.GESPERRT: 0,
        ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH: 1,
        ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        ZivilgesellschaftsChartaGeltung.GESPERRT: ZivilgesellschaftsChartaTyp.SCHUTZ_ZIVILGESELLSCHAFT,
        ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH: ZivilgesellschaftsChartaTyp.ORDNUNGS_ZIVILGESELLSCHAFT,
        ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH: ZivilgesellschaftsChartaTyp.SOUVERAENITAETS_ZIVILGESELLSCHAFT,
    })
    _PROZEDUR_MAP.update({
        ZivilgesellschaftsChartaGeltung.GESPERRT: ZivilgesellschaftsChartaProzedur.NOTPROZEDUR,
        ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH: ZivilgesellschaftsChartaProzedur.REGELPROTOKOLL,
        ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH: ZivilgesellschaftsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        PolitikNormGeltung.GESPERRT: ZivilgesellschaftsChartaGeltung.GESPERRT,
        PolitikNormGeltung.POLITIKNORMATIV: ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH,
        PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV: ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH,
    })


class ZivilgesellschaftsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    ZIVILGESELLSCHAFTLICH = "zivilgesellschaftlich"
    GRUNDLEGEND_ZIVILGESELLSCHAFTLICH = "grundlegend-zivilgesellschaftlich"


class ZivilgesellschaftsChartaTyp(Enum):
    SCHUTZ_ZIVILGESELLSCHAFT = "schutz-zivilgesellschaft"
    ORDNUNGS_ZIVILGESELLSCHAFT = "ordnungs-zivilgesellschaft"
    SOUVERAENITAETS_ZIVILGESELLSCHAFT = "souveraenitaets-zivilgesellschaft"


class ZivilgesellschaftsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class ZivilgesellschaftsChartaNorm:
    zivilgesellschafts_charta_id: str
    zivilgesellschafts_typ: ZivilgesellschaftsChartaTyp
    prozedur: ZivilgesellschaftsChartaProzedur
    geltung: ZivilgesellschaftsChartaGeltung
    zivilgesellschafts_weight: float
    zivilgesellschafts_tier: int
    canonical: bool
    zivilgesellschafts_ids: tuple[str, ...]
    zivilgesellschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZivilgesellschaftsCharta:
    charta_id: str
    politik_norm: PolitikNormSatz
    normen: tuple[ZivilgesellschaftsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilgesellschafts_charta_id for n in self.normen if n.geltung is ZivilgesellschaftsChartaGeltung.GESPERRT)

    @property
    def zivilgesellschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilgesellschafts_charta_id for n in self.normen if n.geltung is ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilgesellschafts_charta_id for n in self.normen if n.geltung is ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH)

    @property
    def charta_signal(self):
        if any(n.geltung is ZivilgesellschaftsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-zivilgesellschaftlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-zivilgesellschaftlich")


_init_map()


def build_zivilgesellschafts_charta(
    politik_norm: PolitikNormSatz | None = None,
    *,
    charta_id: str = "zivilgesellschafts-charta",
) -> ZivilgesellschaftsCharta:
    if politik_norm is None:
        politik_norm = build_politik_norm(norm_id=f"{charta_id}-norm")

    normen: list[ZivilgesellschaftsChartaNorm] = []
    for parent_norm in politik_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{politik_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.politik_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.politik_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH)
        normen.append(
            ZivilgesellschaftsChartaNorm(
                zivilgesellschafts_charta_id=new_id,
                zivilgesellschafts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                zivilgesellschafts_weight=new_weight,
                zivilgesellschafts_tier=new_tier,
                canonical=is_canonical,
                zivilgesellschafts_ids=parent_norm.politik_norm_ids + (new_id,),
                zivilgesellschafts_tags=parent_norm.politik_norm_tags + (f"zivilgesellschafts-charta:{new_geltung.value}",),
            )
        )
    return ZivilgesellschaftsCharta(
        charta_id=charta_id,
        politik_norm=politik_norm,
        normen=tuple(normen),
    )
