"""
#470 LinguistikVerfassung — Block-Krone: Linguistik & Semiotik.
Saussure → Troubetzkoy/Jakobson → Chomsky → Frege/Tarski → Austin/Grice → Peirce/Eco →
Foucault/Habermas → Wittgenstein → Shannon/Zipf: Die vollständige Spracharchitektur.
Leitsterns Terra-Schwarm vereint alle Sprachebenen: von der Phonologie über Syntax und
Semantik bis zur Pragmatik, Semiotik, Diskurs, Sprachnorm und Kommunikationseffizienz —
ein linguistisch fundiertes Kollektivbewusstsein für den Terra-Schwarm Leitstern.
Geltungsstufen: GESPERRT / LINGUISTISCH / GRUNDLEGEND_LINGUISTISCH
Parent: KommunikationsCharta (#469)
Block #461–#470: Linguistik & Semiotik — Block-Krone Milestone #27 ⭐
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kommunikations_charta import (
    KommunikationsCharta,
    KommunikationsChartaGeltung,
    build_kommunikations_charta,
)

_GELTUNG_MAP: dict[KommunikationsChartaGeltung, "LinguistikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KommunikationsChartaGeltung.GESPERRT] = LinguistikVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[KommunikationsChartaGeltung.KOMMUNIKATIV] = LinguistikVerfassungsGeltung.LINGUISTISCH
    _GELTUNG_MAP[KommunikationsChartaGeltung.GRUNDLEGEND_KOMMUNIKATIV] = LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH


class LinguistikVerfassungsTyp(Enum):
    SCHUTZ_LINGUISTIK = "schutz-linguistik"
    ORDNUNGS_LINGUISTIK = "ordnungs-linguistik"
    SOUVERAENITAETS_LINGUISTIK = "souveraenitaets-linguistik"


class LinguistikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LinguistikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    LINGUISTISCH = "linguistisch"
    GRUNDLEGEND_LINGUISTISCH = "grundlegend-linguistisch"


_init_map()

_TYP_MAP: dict[LinguistikVerfassungsGeltung, LinguistikVerfassungsTyp] = {
    LinguistikVerfassungsGeltung.GESPERRT: LinguistikVerfassungsTyp.SCHUTZ_LINGUISTIK,
    LinguistikVerfassungsGeltung.LINGUISTISCH: LinguistikVerfassungsTyp.ORDNUNGS_LINGUISTIK,
    LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH: LinguistikVerfassungsTyp.SOUVERAENITAETS_LINGUISTIK,
}

_PROZEDUR_MAP: dict[LinguistikVerfassungsGeltung, LinguistikVerfassungsProzedur] = {
    LinguistikVerfassungsGeltung.GESPERRT: LinguistikVerfassungsProzedur.NOTPROZEDUR,
    LinguistikVerfassungsGeltung.LINGUISTISCH: LinguistikVerfassungsProzedur.REGELPROTOKOLL,
    LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH: LinguistikVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LinguistikVerfassungsGeltung, float] = {
    LinguistikVerfassungsGeltung.GESPERRT: 0.0,
    LinguistikVerfassungsGeltung.LINGUISTISCH: 0.04,
    LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH: 0.08,
}

_TIER_DELTA: dict[LinguistikVerfassungsGeltung, int] = {
    LinguistikVerfassungsGeltung.GESPERRT: 0,
    LinguistikVerfassungsGeltung.LINGUISTISCH: 1,
    LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH: 2,
}


@dataclass(frozen=True)
class LinguistikVerfassungsNorm:
    linguistik_verfassung_id: str
    linguistik_typ: LinguistikVerfassungsTyp
    prozedur: LinguistikVerfassungsProzedur
    geltung: LinguistikVerfassungsGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class LinguistikVerfassung:
    verfassung_id: str
    kommunikations_charta: KommunikationsCharta
    normen: tuple[LinguistikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.linguistik_verfassung_id for n in self.normen if n.geltung is LinguistikVerfassungsGeltung.GESPERRT)

    @property
    def linguistisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.linguistik_verfassung_id for n in self.normen if n.geltung is LinguistikVerfassungsGeltung.LINGUISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.linguistik_verfassung_id for n in self.normen if n.geltung is LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH)

    @property
    def verfassung_signal(self):
        if any(n.geltung is LinguistikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is LinguistikVerfassungsGeltung.LINGUISTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-linguistisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-linguistisch")


def build_linguistik_verfassung(
    kommunikations_charta: KommunikationsCharta | None = None,
    *,
    verfassung_id: str = "linguistik-verfassung",
) -> LinguistikVerfassung:
    if kommunikations_charta is None:
        kommunikations_charta = build_kommunikations_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[LinguistikVerfassungsNorm] = []
    for parent_norm in kommunikations_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kommunikations_charta_id.removeprefix(f'{kommunikations_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kommunikations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kommunikations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH)
        normen.append(
            LinguistikVerfassungsNorm(
                linguistik_verfassung_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.kommunikations_ids + (new_id,),
                linguistik_tags=parent_norm.kommunikations_tags + (f"linguistik-verfassung:{new_geltung.value}",),
            )
        )
    return LinguistikVerfassung(
        verfassung_id=verfassung_id,
        kommunikations_charta=kommunikations_charta,
        normen=tuple(normen),
    )
