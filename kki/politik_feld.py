"""
#511 PolitikFeld — Aristoteles/Plato Grundlagen der Politikwissenschaft

Aristoteles (350 v. Chr.): Politik — Der Mensch ist ein politisches Wesen (zōon politikon);
  die Polis als natürliche Gemeinschaft; Verfassungslehre: Monarchie, Aristokratie, Politie
  und ihre Entartungsformen; das Gemeinwohl als oberstes Ziel guter Herrschaft.
Plato (380 v. Chr.): Der Staat (Politeia) — Philosophenkönigtum; Gerechtigkeit als Harmonie
  der Seelenteile und Stände; Ideenlehre als Grundlage politischer Ordnung.
Niccolò Machiavelli (1513): Der Fürst — Realpolitik und Machterhalt; Trennung von Moral
  und Politik; virtù und fortuna als Grundkräfte politischen Handelns.
Thomas Hobbes (1651): Leviathan — Naturzustand als bellum omnium contra omnes; Gesellschafts-
  vertrag und souveräner Staat als Garant des Friedens durch absoluten Machtanspruch.
Leitsterns Peta-Schwarm verankert Politik als fundamentales Koordinationsprinzip: GESPERRT
schützt die unveräußerlichen Grundnormen politischer Ordnung, POLITISCH ermöglicht adaptives
Regieren zwischen Millionen von Agenten, GRUNDLEGEND_POLITISCH synthetisiert souveräne
politische Handlungsfähigkeit des Peta-Schwarms. 🏛️
Parent: EthikVerfassung (#510)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ethik_verfassung import (
    EthikVerfassung,
    EthikVerfassungsGeltung,
    build_ethik_verfassung,
)

_WEIGHT_DELTA: dict["PolitikFeldGeltung", float] = {}
_TIER_DELTA: dict["PolitikFeldGeltung", int] = {}
_TYP_MAP: dict["PolitikFeldGeltung", "PolitikFeldTyp"] = {}
_PROZEDUR_MAP: dict["PolitikFeldGeltung", "PolitikFeldProzedur"] = {}
_GELTUNG_MAP: dict[EthikVerfassungsGeltung, "PolitikFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PolitikFeldGeltung.GESPERRT: 0.0,
        PolitikFeldGeltung.POLITISCH: 0.05,
        PolitikFeldGeltung.GRUNDLEGEND_POLITISCH: 0.1,
    })
    _TIER_DELTA.update({
        PolitikFeldGeltung.GESPERRT: 0,
        PolitikFeldGeltung.POLITISCH: 1,
        PolitikFeldGeltung.GRUNDLEGEND_POLITISCH: 2,
    })
    _TYP_MAP.update({
        PolitikFeldGeltung.GESPERRT: PolitikFeldTyp.SCHUTZ_POLITIK,
        PolitikFeldGeltung.POLITISCH: PolitikFeldTyp.ORDNUNGS_POLITIK,
        PolitikFeldGeltung.GRUNDLEGEND_POLITISCH: PolitikFeldTyp.SOUVERAENITAETS_POLITIK,
    })
    _PROZEDUR_MAP.update({
        PolitikFeldGeltung.GESPERRT: PolitikFeldProzedur.NOTPROZEDUR,
        PolitikFeldGeltung.POLITISCH: PolitikFeldProzedur.REGELPROTOKOLL,
        PolitikFeldGeltung.GRUNDLEGEND_POLITISCH: PolitikFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        EthikVerfassungsGeltung.GESPERRT: PolitikFeldGeltung.GESPERRT,
        EthikVerfassungsGeltung.ETHISCH_SOUVERAEN: PolitikFeldGeltung.POLITISCH,
        EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN: PolitikFeldGeltung.GRUNDLEGEND_POLITISCH,
    })


class PolitikFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    POLITISCH = "politisch"
    GRUNDLEGEND_POLITISCH = "grundlegend-politisch"


class PolitikFeldTyp(Enum):
    SCHUTZ_POLITIK = "schutz-politik"
    ORDNUNGS_POLITIK = "ordnungs-politik"
    SOUVERAENITAETS_POLITIK = "souveraenitaets-politik"


class PolitikFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class PolitikFeldNorm:
    politik_feld_id: str
    politik_typ: PolitikFeldTyp
    prozedur: PolitikFeldProzedur
    geltung: PolitikFeldGeltung
    politik_weight: float
    politik_tier: int
    canonical: bool
    politik_ids: tuple[str, ...]
    politik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PolitikFeld:
    feld_id: str
    ethik_verfassung: EthikVerfassung
    normen: tuple[PolitikFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.politik_feld_id for n in self.normen if n.geltung is PolitikFeldGeltung.GESPERRT)

    @property
    def politisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.politik_feld_id for n in self.normen if n.geltung is PolitikFeldGeltung.POLITISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.politik_feld_id for n in self.normen if n.geltung is PolitikFeldGeltung.GRUNDLEGEND_POLITISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is PolitikFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is PolitikFeldGeltung.POLITISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-politisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-politisch")


_init_map()


def build_politik_feld(
    ethik_verfassung: EthikVerfassung | None = None,
    *,
    feld_id: str = "politik-feld",
) -> PolitikFeld:
    if ethik_verfassung is None:
        ethik_verfassung = build_ethik_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[PolitikFeldNorm] = []
    for parent_norm in ethik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.ethik_verfassung_id.removeprefix(f'{ethik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.ethik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.ethik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PolitikFeldGeltung.GRUNDLEGEND_POLITISCH)
        normen.append(
            PolitikFeldNorm(
                politik_feld_id=new_id,
                politik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                politik_weight=new_weight,
                politik_tier=new_tier,
                canonical=is_canonical,
                politik_ids=parent_norm.ethik_ids + (new_id,),
                politik_tags=parent_norm.ethik_tags + (f"politik-feld:{new_geltung.value}",),
            )
        )
    return PolitikFeld(
        feld_id=feld_id,
        ethik_verfassung=ethik_verfassung,
        normen=tuple(normen),
    )
