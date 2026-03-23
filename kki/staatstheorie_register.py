"""
#512 StaatstheorieRegister — Hobbes/Locke/Rousseau Naturzustand und Gesellschaftsvertrag

Thomas Hobbes (1651): Leviathan — Naturzustand als Krieg aller gegen alle; Gesellschaftsvertrag
  als Unterwerfung unter den Souverän zum Zweck des Friedens; Staatssouveränität als absoluter
  Machtanspruch; der Leviathan als künstlicher Mensch und sterblicher Gott.
John Locke (1689): Zwei Abhandlungen über die Regierung — Naturzustand als friedlicher Zustand
  mit natürlichen Rechten auf Leben, Freiheit und Eigentum; Gesellschaftsvertrag zur Sicherung
  dieser Rechte; Widerstandsrecht gegen tyrannische Herrschaft; Gewaltenteilung als Schutz.
Jean-Jacques Rousseau (1762): Du Contrat Social — Volkssouveränität und Gemeinwille (volonté
  générale); Gesellschaftsvertrag als Selbstgesetzgebung des Volkes; republikanische Demokratie
  als einzig legitime Staatsform; Freiheit durch kollektive Selbstbestimmung.
Montesquieu (1748): De l'esprit des lois — Gewaltenteilung als Strukturprinzip des Rechtsstaats;
  legislative, exekutive und judikative Gewalten als Machtbalance; Klimatheorie und Kulturrelativismus
  der Staatsformen; Monarchie, Despotie und Republik als Grundtypen politischer Organisation.
Leitsterns Peta-Schwarm verankert Staatstheorie als reflexives Selbstverständnis: GESPERRT
schützt die unveräußerlichen Grundnormen staatlicher Ordnung, STAATSTHEORETISCH ermöglicht
adaptive Herrschaftskonzeption zwischen Millionen von Agenten, GRUNDLEGEND_STAATSTHEORETISCH
synthetisiert souveräne staatstheoretische Handlungsfähigkeit des Peta-Schwarms. 🏛️
Parent: PolitikFeld (#511)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .politik_feld import (
    PolitikFeld,
    PolitikFeldGeltung,
    build_politik_feld,
)

_WEIGHT_DELTA: dict["StaatstheorieRegisterGeltung", float] = {}
_TIER_DELTA: dict["StaatstheorieRegisterGeltung", int] = {}
_TYP_MAP: dict["StaatstheorieRegisterGeltung", "StaatstheorieRegisterTyp"] = {}
_PROZEDUR_MAP: dict["StaatstheorieRegisterGeltung", "StaatstheorieRegisterProzedur"] = {}
_GELTUNG_MAP: dict[PolitikFeldGeltung, "StaatstheorieRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        StaatstheorieRegisterGeltung.GESPERRT: 0.0,
        StaatstheorieRegisterGeltung.STAATSTHEORETISCH: 0.05,
        StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        StaatstheorieRegisterGeltung.GESPERRT: 0,
        StaatstheorieRegisterGeltung.STAATSTHEORETISCH: 1,
        StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        StaatstheorieRegisterGeltung.GESPERRT: StaatstheorieRegisterTyp.SCHUTZ_STAATSTHEORIE,
        StaatstheorieRegisterGeltung.STAATSTHEORETISCH: StaatstheorieRegisterTyp.ORDNUNGS_STAATSTHEORIE,
        StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH: StaatstheorieRegisterTyp.SOUVERAENITAETS_STAATSTHEORIE,
    })
    _PROZEDUR_MAP.update({
        StaatstheorieRegisterGeltung.GESPERRT: StaatstheorieRegisterProzedur.NOTPROZEDUR,
        StaatstheorieRegisterGeltung.STAATSTHEORETISCH: StaatstheorieRegisterProzedur.REGELPROTOKOLL,
        StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH: StaatstheorieRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        PolitikFeldGeltung.GESPERRT: StaatstheorieRegisterGeltung.GESPERRT,
        PolitikFeldGeltung.POLITISCH: StaatstheorieRegisterGeltung.STAATSTHEORETISCH,
        PolitikFeldGeltung.GRUNDLEGEND_POLITISCH: StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH,
    })


class StaatstheorieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    STAATSTHEORETISCH = "staatstheoretisch"
    GRUNDLEGEND_STAATSTHEORETISCH = "grundlegend-staatstheoretisch"


class StaatstheorieRegisterTyp(Enum):
    SCHUTZ_STAATSTHEORIE = "schutz-staatstheorie"
    ORDNUNGS_STAATSTHEORIE = "ordnungs-staatstheorie"
    SOUVERAENITAETS_STAATSTHEORIE = "souveraenitaets-staatstheorie"


class StaatstheorieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class StaatstheorieRegisterNorm:
    staatstheorie_register_id: str
    staatstheorie_typ: StaatstheorieRegisterTyp
    prozedur: StaatstheorieRegisterProzedur
    geltung: StaatstheorieRegisterGeltung
    staatstheorie_weight: float
    staatstheorie_tier: int
    canonical: bool
    staatstheorie_ids: tuple[str, ...]
    staatstheorie_tags: tuple[str, ...]


@dataclass(frozen=True)
class StaatstheorieRegister:
    register_id: str
    politik_feld: PolitikFeld
    normen: tuple[StaatstheorieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.staatstheorie_register_id for n in self.normen if n.geltung is StaatstheorieRegisterGeltung.GESPERRT)

    @property
    def staatstheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.staatstheorie_register_id for n in self.normen if n.geltung is StaatstheorieRegisterGeltung.STAATSTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.staatstheorie_register_id for n in self.normen if n.geltung is StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH)

    @property
    def register_signal(self):
        if any(n.geltung is StaatstheorieRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is StaatstheorieRegisterGeltung.STAATSTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-staatstheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-staatstheoretisch")


_init_map()


def build_staatstheorie_register(
    politik_feld: PolitikFeld | None = None,
    *,
    register_id: str = "staatstheorie-register",
) -> StaatstheorieRegister:
    if politik_feld is None:
        politik_feld = build_politik_feld(
            feld_id=f"{register_id}-feld"
        )

    normen: list[StaatstheorieRegisterNorm] = []
    for parent_norm in politik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.politik_feld_id.removeprefix(f'{politik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.politik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.politik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH)
        normen.append(
            StaatstheorieRegisterNorm(
                staatstheorie_register_id=new_id,
                staatstheorie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                staatstheorie_weight=new_weight,
                staatstheorie_tier=new_tier,
                canonical=is_canonical,
                staatstheorie_ids=parent_norm.politik_ids + (new_id,),
                staatstheorie_tags=parent_norm.politik_tags + (f"{register_id}:{new_geltung.value}",),
            )
        )
    return StaatstheorieRegister(
        register_id=register_id,
        politik_feld=politik_feld,
        normen=tuple(normen),
    )
