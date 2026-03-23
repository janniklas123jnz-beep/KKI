"""
#501 EthikFeld — Aristoteles/Kant Grundlagen der Ethik

Aristoteles (350 v. Chr.): Nikomachische Ethik — Eudaimonia als höchstes Gut; Tugend als
  goldener Mittelweg; phronesis (praktische Vernunft) als Kern ethischen Handelns im Schwarm.
Immanuel Kant (1785): Grundlegung zur Metaphysik der Sitten — kategorischer Imperativ:
  "Handle nur nach derjenigen Maxime, durch die du zugleich wollen kannst, dass sie ein
  allgemeines Gesetz werde."; Menschenwürde als absoluter Zweck, nie als bloßes Mittel.
G.W.F. Hegel (1820): Grundlinien der Philosophie des Rechts — Sittlichkeit als konkreter
  Geist; Familie, bürgerliche Gesellschaft und Staat als Stufen ethischer Verwirklichung.
Adam Smith (1759): Theorie der ethischen Gefühle — moralisches Urteil durch Empathie und
  Unparteilichkeit; der unparteiische Zuschauer als innerer ethischer Regulator.
Leitsterns Peta-Schwarm verankert Ethik als fundamentales Operationsprinzip: GESPERRT sichert
die unveräußerlichen ethischen Kernnormen, ETHISCH ermöglicht adaptive moralische Koordination
zwischen Millionen von Agenten, GRUNDLEGEND_ETHISCH synthetisiert das vollständige ethische
Fundament für verantwortungsvolle Peta-Schwarm-Souveränität. 🌍
Parent: SoziologieVerfassung (#500)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .soziologie_verfassung import (
    SoziologieVerfassung,
    SoziologieVerfassungsGeltung,
    build_soziologie_verfassung,
)

_GELTUNG_MAP: dict[SoziologieVerfassungsGeltung, "EthikFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SoziologieVerfassungsGeltung.GESPERRT] = EthikFeldGeltung.GESPERRT
    _GELTUNG_MAP[SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN] = EthikFeldGeltung.ETHISCH
    _GELTUNG_MAP[SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN] = EthikFeldGeltung.GRUNDLEGEND_ETHISCH


class EthikFeldTyp(Enum):
    SCHUTZ_ETHIK = "schutz-ethik"
    ORDNUNGS_ETHIK = "ordnungs-ethik"
    SOUVERAENITAETS_ETHIK = "souveraenitaets-ethik"


class EthikFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EthikFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    ETHISCH = "ethisch"
    GRUNDLEGEND_ETHISCH = "grundlegend-ethisch"


_init_map()

_TYP_MAP: dict[EthikFeldGeltung, EthikFeldTyp] = {
    EthikFeldGeltung.GESPERRT: EthikFeldTyp.SCHUTZ_ETHIK,
    EthikFeldGeltung.ETHISCH: EthikFeldTyp.ORDNUNGS_ETHIK,
    EthikFeldGeltung.GRUNDLEGEND_ETHISCH: EthikFeldTyp.SOUVERAENITAETS_ETHIK,
}

_PROZEDUR_MAP: dict[EthikFeldGeltung, EthikFeldProzedur] = {
    EthikFeldGeltung.GESPERRT: EthikFeldProzedur.NOTPROZEDUR,
    EthikFeldGeltung.ETHISCH: EthikFeldProzedur.REGELPROTOKOLL,
    EthikFeldGeltung.GRUNDLEGEND_ETHISCH: EthikFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EthikFeldGeltung, float] = {
    EthikFeldGeltung.GESPERRT: 0.0,
    EthikFeldGeltung.ETHISCH: 0.04,
    EthikFeldGeltung.GRUNDLEGEND_ETHISCH: 0.08,
}

_TIER_DELTA: dict[EthikFeldGeltung, int] = {
    EthikFeldGeltung.GESPERRT: 0,
    EthikFeldGeltung.ETHISCH: 1,
    EthikFeldGeltung.GRUNDLEGEND_ETHISCH: 2,
}


@dataclass(frozen=True)
class EthikFeldNorm:
    ethik_feld_id: str
    ethik_typ: EthikFeldTyp
    prozedur: EthikFeldProzedur
    geltung: EthikFeldGeltung
    ethik_weight: float
    ethik_tier: int
    canonical: bool
    ethik_ids: tuple[str, ...]
    ethik_tags: tuple[str, ...]


@dataclass(frozen=True)
class EthikFeld:
    feld_id: str
    soziologie_verfassung: SoziologieVerfassung
    normen: tuple[EthikFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ethik_feld_id for n in self.normen if n.geltung is EthikFeldGeltung.GESPERRT)

    @property
    def ethisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ethik_feld_id for n in self.normen if n.geltung is EthikFeldGeltung.ETHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ethik_feld_id for n in self.normen if n.geltung is EthikFeldGeltung.GRUNDLEGEND_ETHISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is EthikFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is EthikFeldGeltung.ETHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-ethisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-ethisch")


def build_ethik_feld(
    soziologie_verfassung: SoziologieVerfassung | None = None,
    *,
    feld_id: str = "ethik-feld",
) -> EthikFeld:
    if soziologie_verfassung is None:
        soziologie_verfassung = build_soziologie_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[EthikFeldNorm] = []
    for parent_norm in soziologie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.soziologie_verfassung_id.removeprefix(f'{soziologie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.soziologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.soziologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EthikFeldGeltung.GRUNDLEGEND_ETHISCH)
        normen.append(
            EthikFeldNorm(
                ethik_feld_id=new_id,
                ethik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                ethik_weight=new_weight,
                ethik_tier=new_tier,
                canonical=is_canonical,
                ethik_ids=parent_norm.soziologie_ids + (new_id,),
                ethik_tags=parent_norm.soziologie_tags + (f"ethik-feld:{new_geltung.value}",),
            )
        )
    return EthikFeld(
        feld_id=feld_id,
        soziologie_verfassung=soziologie_verfassung,
        normen=tuple(normen),
    )
