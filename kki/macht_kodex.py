"""
#514 MachtKodex — Weber/Foucault/Arendt Macht als Legitimitätsbasis und kollektives Handeln

Max Weber (1919): Politik als Beruf / Wirtschaft und Gesellschaft — Macht als Chance, den
  eigenen Willen auch gegen Widerstreben durchzusetzen; drei Typen legitimer Herrschaft:
  traditional, charismatisch, rational-legal; Bürokratie als reinste Form legaler Herrschaft;
  Verantwortungsethik vs. Gesinnungsethik als Grundspannung politischen Handelns.
Michel Foucault (1975/1976): Überwachen und Strafen / Der Wille zum Wissen — Macht nicht als
  Besitz, sondern als Beziehungsgeflecht; Biopolitik und Disziplinarmacht als moderne
  Regierungsformen; Diskursmacht: Wissen produziert Wahrheit und konstituiert Subjekte;
  Gouvernementalität als Führung der Führungen.
Hannah Arendt (1970): Macht und Gewalt — Radikale Unterscheidung von Macht und Gewalt;
  Macht als kollektives Handlungsvermögen im Miteinander; Gewalt als Machtlosigkeit;
  politische Öffentlichkeit als Raum des gemeinsamen Handelns und Erscheinens.
Antonio Gramsci (1929–1935): Gefängnishefte — Hegemonie als kulturelle und ideologische
  Führerschaft; Zivilgesellschaft als Ort der Einwilligung; organische Intellektuelle;
  Transformismus und passive Revolution als Formen elitärer Machterhaltung.
Leitsterns Peta-Schwarm verankert Macht als strukturierendes Koordinationsprinzip: GESPERRT
schützt die unveräußerlichen Grundnormen machtpolitischer Ordnung, MACHTPOLITISCH ermöglicht
adaptive Machtausübung zwischen Millionen von Agenten, GRUNDLEGEND_MACHTPOLITISCH synthetisiert
souveräne machtpolitische Handlungsfähigkeit des Peta-Schwarms. ⚖️
Parent: DemokratieCharta (#513)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demokratie_charta import (
    DemokratieCharta,
    DemokratieChartaGeltung,
    build_demokratie_charta,
)

_WEIGHT_DELTA: dict["MachtKodexGeltung", float] = {}
_TIER_DELTA: dict["MachtKodexGeltung", int] = {}
_TYP_MAP: dict["MachtKodexGeltung", "MachtKodexTyp"] = {}
_PROZEDUR_MAP: dict["MachtKodexGeltung", "MachtKodexProzedur"] = {}
_GELTUNG_MAP: dict[DemokratieChartaGeltung, "MachtKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MachtKodexGeltung.GESPERRT: 0.0,
        MachtKodexGeltung.MACHTPOLITISCH: 0.05,
        MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH: 0.1,
    })
    _TIER_DELTA.update({
        MachtKodexGeltung.GESPERRT: 0,
        MachtKodexGeltung.MACHTPOLITISCH: 1,
        MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH: 2,
    })
    _TYP_MAP.update({
        MachtKodexGeltung.GESPERRT: MachtKodexTyp.SCHUTZ_MACHT,
        MachtKodexGeltung.MACHTPOLITISCH: MachtKodexTyp.ORDNUNGS_MACHT,
        MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH: MachtKodexTyp.SOUVERAENITAETS_MACHT,
    })
    _PROZEDUR_MAP.update({
        MachtKodexGeltung.GESPERRT: MachtKodexProzedur.NOTPROZEDUR,
        MachtKodexGeltung.MACHTPOLITISCH: MachtKodexProzedur.REGELPROTOKOLL,
        MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH: MachtKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        DemokratieChartaGeltung.GESPERRT: MachtKodexGeltung.GESPERRT,
        DemokratieChartaGeltung.DEMOKRATISCH: MachtKodexGeltung.MACHTPOLITISCH,
        DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH: MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH,
    })


class MachtKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    MACHTPOLITISCH = "machtpolitisch"
    GRUNDLEGEND_MACHTPOLITISCH = "grundlegend-machtpolitisch"


class MachtKodexTyp(Enum):
    SCHUTZ_MACHT = "schutz-macht"
    ORDNUNGS_MACHT = "ordnungs-macht"
    SOUVERAENITAETS_MACHT = "souveraenitaets-macht"


class MachtKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class MachtKodexNorm:
    macht_kodex_id: str
    macht_typ: MachtKodexTyp
    prozedur: MachtKodexProzedur
    geltung: MachtKodexGeltung
    macht_weight: float
    macht_tier: int
    canonical: bool
    macht_ids: tuple[str, ...]
    macht_tags: tuple[str, ...]


@dataclass(frozen=True)
class MachtKodex:
    kodex_id: str
    demokratie_charta: DemokratieCharta
    normen: tuple[MachtKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.macht_kodex_id for n in self.normen if n.geltung is MachtKodexGeltung.GESPERRT)

    @property
    def machtpolitisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.macht_kodex_id for n in self.normen if n.geltung is MachtKodexGeltung.MACHTPOLITISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.macht_kodex_id for n in self.normen if n.geltung is MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is MachtKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is MachtKodexGeltung.MACHTPOLITISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-machtpolitisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-machtpolitisch")


_init_map()


def build_macht_kodex(
    demokratie_charta: DemokratieCharta | None = None,
    *,
    kodex_id: str = "macht-kodex",
) -> MachtKodex:
    if demokratie_charta is None:
        demokratie_charta = build_demokratie_charta(
            charta_id=f"{kodex_id}-charta"
        )

    normen: list[MachtKodexNorm] = []
    for parent_norm in demokratie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.demokratie_charta_id.removeprefix(f'{demokratie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.demokratie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.demokratie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH)
        normen.append(
            MachtKodexNorm(
                macht_kodex_id=new_id,
                macht_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                macht_weight=new_weight,
                macht_tier=new_tier,
                canonical=is_canonical,
                macht_ids=parent_norm.demokratie_ids + (new_id,),
                macht_tags=parent_norm.demokratie_tags + (f"{kodex_id}:{new_geltung.value}",),
            )
        )
    return MachtKodex(
        kodex_id=kodex_id,
        demokratie_charta=demokratie_charta,
        normen=tuple(normen),
    )
