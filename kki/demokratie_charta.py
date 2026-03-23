"""
#513 DemokratieCharta — Madison/Tocqueville/Dahl Volksherrschaft und pluralistische Demokratie

James Madison (1787): Federalist Papers — Pluralistische Demokratietheorie; Kontrolle von
  Fraktionen durch Gewaltenteilung und föderale Struktur; repräsentative Demokratie als
  Schutz vor Tyrannei der Mehrheit; checks and balances als Verfassungsprinzip der USA.
Alexis de Tocqueville (1835): Über die Demokratie in Amerika — Demokratie als gesellschaftliche
  Gleichheitskultur; Gefahr des demokratischen Despotismus und der Tyrannei der Mehrheit;
  Zivilgesellschaft und kommunale Selbstverwaltung als demokratische Schulen der Freiheit.
Robert A. Dahl (1956/1971): Polyarchie — Pluralismus als realistisches Demokratiemodell;
  Polyarchie als faktische Herrschaft konkurrierender Eliten und Interessengruppen; Kriterien
  demokratischer Legitimität: Partizipation, Wettbewerb, bürgerliche Freiheiten.
Jean-Jacques Rousseau (1762): Volonté générale — Gemeinwille als Grundlage demokratischer
  Legitimität; direkte Demokratie als Ideal; Volkssouveränität als unveräußerliches Prinzip;
  Unterschied zwischen Gemeinwille und bloßem Mehrheitswillen.
Leitsterns Peta-Schwarm verankert Demokratie als kollektives Selbstbestimmungsprinzip: GESPERRT
schützt die unveräußerlichen Grundnormen demokratischer Ordnung, DEMOKRATISCH ermöglicht
adaptive Volksherrschaft zwischen Millionen von Agenten, GRUNDLEGEND_DEMOKRATISCH synthetisiert
souveräne demokratische Handlungsfähigkeit des Peta-Schwarms. 🗳️
Parent: StaatstheorieRegister (#512)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .staatstheorie_register import (
    StaatstheorieRegister,
    StaatstheorieRegisterGeltung,
    build_staatstheorie_register,
)

_WEIGHT_DELTA: dict["DemokratieChartaGeltung", float] = {}
_TIER_DELTA: dict["DemokratieChartaGeltung", int] = {}
_TYP_MAP: dict["DemokratieChartaGeltung", "DemokratieChartaTyp"] = {}
_PROZEDUR_MAP: dict["DemokratieChartaGeltung", "DemokratieChartaProzedur"] = {}
_GELTUNG_MAP: dict[StaatstheorieRegisterGeltung, "DemokratieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DemokratieChartaGeltung.GESPERRT: 0.0,
        DemokratieChartaGeltung.DEMOKRATISCH: 0.05,
        DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH: 0.1,
    })
    _TIER_DELTA.update({
        DemokratieChartaGeltung.GESPERRT: 0,
        DemokratieChartaGeltung.DEMOKRATISCH: 1,
        DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH: 2,
    })
    _TYP_MAP.update({
        DemokratieChartaGeltung.GESPERRT: DemokratieChartaTyp.SCHUTZ_DEMOKRATIE,
        DemokratieChartaGeltung.DEMOKRATISCH: DemokratieChartaTyp.ORDNUNGS_DEMOKRATIE,
        DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH: DemokratieChartaTyp.SOUVERAENITAETS_DEMOKRATIE,
    })
    _PROZEDUR_MAP.update({
        DemokratieChartaGeltung.GESPERRT: DemokratieChartaProzedur.NOTPROZEDUR,
        DemokratieChartaGeltung.DEMOKRATISCH: DemokratieChartaProzedur.REGELPROTOKOLL,
        DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH: DemokratieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        StaatstheorieRegisterGeltung.GESPERRT: DemokratieChartaGeltung.GESPERRT,
        StaatstheorieRegisterGeltung.STAATSTHEORETISCH: DemokratieChartaGeltung.DEMOKRATISCH,
        StaatstheorieRegisterGeltung.GRUNDLEGEND_STAATSTHEORETISCH: DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH,
    })


class DemokratieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    DEMOKRATISCH = "demokratisch"
    GRUNDLEGEND_DEMOKRATISCH = "grundlegend-demokratisch"


class DemokratieChartaTyp(Enum):
    SCHUTZ_DEMOKRATIE = "schutz-demokratie"
    ORDNUNGS_DEMOKRATIE = "ordnungs-demokratie"
    SOUVERAENITAETS_DEMOKRATIE = "souveraenitaets-demokratie"


class DemokratieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class DemokratieChartaNorm:
    demokratie_charta_id: str
    demokratie_typ: DemokratieChartaTyp
    prozedur: DemokratieChartaProzedur
    geltung: DemokratieChartaGeltung
    demokratie_weight: float
    demokratie_tier: int
    canonical: bool
    demokratie_ids: tuple[str, ...]
    demokratie_tags: tuple[str, ...]


@dataclass(frozen=True)
class DemokratieCharta:
    charta_id: str
    staatstheorie_register: StaatstheorieRegister
    normen: tuple[DemokratieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.demokratie_charta_id for n in self.normen if n.geltung is DemokratieChartaGeltung.GESPERRT)

    @property
    def demokratisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.demokratie_charta_id for n in self.normen if n.geltung is DemokratieChartaGeltung.DEMOKRATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.demokratie_charta_id for n in self.normen if n.geltung is DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is DemokratieChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is DemokratieChartaGeltung.DEMOKRATISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-demokratisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-demokratisch")


_init_map()


def build_demokratie_charta(
    staatstheorie_register: StaatstheorieRegister | None = None,
    *,
    charta_id: str = "demokratie-charta",
) -> DemokratieCharta:
    if staatstheorie_register is None:
        staatstheorie_register = build_staatstheorie_register(
            register_id=f"{charta_id}-register"
        )

    normen: list[DemokratieChartaNorm] = []
    for parent_norm in staatstheorie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.staatstheorie_register_id.removeprefix(f'{staatstheorie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.staatstheorie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.staatstheorie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DemokratieChartaGeltung.GRUNDLEGEND_DEMOKRATISCH)
        normen.append(
            DemokratieChartaNorm(
                demokratie_charta_id=new_id,
                demokratie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                demokratie_weight=new_weight,
                demokratie_tier=new_tier,
                canonical=is_canonical,
                demokratie_ids=parent_norm.staatstheorie_ids + (new_id,),
                demokratie_tags=parent_norm.staatstheorie_tags + (f"{charta_id}:{new_geltung.value}",),
            )
        )
    return DemokratieCharta(
        charta_id=charta_id,
        staatstheorie_register=staatstheorie_register,
        normen=tuple(normen),
    )
