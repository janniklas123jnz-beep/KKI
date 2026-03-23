"""
#480 PhilosophieVerfassung — Block-Krone: Philosophie & Erkenntnistheorie.
Kant → Aristoteles/Heidegger → Locke/Hume → Descartes/Leibniz → Popper → Kuhn →
Frege/Russell/Gödel → Lakatos/Quine → Flavell/Schön: Die vollständige Erkenntnisarchitektur.
Leitsterns Terra-Schwarm vereint alle epistemologischen Ebenen: von der Kantischen
Kategorienstruktur über empiristische und rationalistische Erkenntnistheorie, Falsifikation
und Paradigmenwechsel, formale Logik und Normen bis zur kollektiven Metakognition —
ein philosophisch fundiertes Erkenntnissystem für den Terra-Schwarm Leitstern.
Geltungsstufen: GESPERRT / PHILOSOPHISCH / GRUNDLEGEND_PHILOSOPHISCH
Parent: MetaKognitionsCharta (#479)
Block #471–#480: Philosophie & Erkenntnistheorie — Block-Krone Milestone #28 ⭐
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .meta_kognitions_charta import (
    MetaKognitionsCharta,
    MetaKognitionsChartaGeltung,
    build_meta_kognitions_charta,
)

_GELTUNG_MAP: dict[MetaKognitionsChartaGeltung, "PhilosophieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MetaKognitionsChartaGeltung.GESPERRT] = PhilosophieVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[MetaKognitionsChartaGeltung.METAKOGNITIV] = PhilosophieVerfassungsGeltung.PHILOSOPHISCH
    _GELTUNG_MAP[MetaKognitionsChartaGeltung.GRUNDLEGEND_METAKOGNITIV] = PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH


class PhilosophieVerfassungsTyp(Enum):
    SCHUTZ_PHILOSOPHIE = "schutz-philosophie"
    ORDNUNGS_PHILOSOPHIE = "ordnungs-philosophie"
    SOUVERAENITAETS_PHILOSOPHIE = "souveraenitaets-philosophie"


class PhilosophieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PhilosophieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    PHILOSOPHISCH = "philosophisch"
    GRUNDLEGEND_PHILOSOPHISCH = "grundlegend-philosophisch"


_init_map()

_TYP_MAP: dict[PhilosophieVerfassungsGeltung, PhilosophieVerfassungsTyp] = {
    PhilosophieVerfassungsGeltung.GESPERRT: PhilosophieVerfassungsTyp.SCHUTZ_PHILOSOPHIE,
    PhilosophieVerfassungsGeltung.PHILOSOPHISCH: PhilosophieVerfassungsTyp.ORDNUNGS_PHILOSOPHIE,
    PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH: PhilosophieVerfassungsTyp.SOUVERAENITAETS_PHILOSOPHIE,
}

_PROZEDUR_MAP: dict[PhilosophieVerfassungsGeltung, PhilosophieVerfassungsProzedur] = {
    PhilosophieVerfassungsGeltung.GESPERRT: PhilosophieVerfassungsProzedur.NOTPROZEDUR,
    PhilosophieVerfassungsGeltung.PHILOSOPHISCH: PhilosophieVerfassungsProzedur.REGELPROTOKOLL,
    PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH: PhilosophieVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PhilosophieVerfassungsGeltung, float] = {
    PhilosophieVerfassungsGeltung.GESPERRT: 0.0,
    PhilosophieVerfassungsGeltung.PHILOSOPHISCH: 0.04,
    PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH: 0.08,
}

_TIER_DELTA: dict[PhilosophieVerfassungsGeltung, int] = {
    PhilosophieVerfassungsGeltung.GESPERRT: 0,
    PhilosophieVerfassungsGeltung.PHILOSOPHISCH: 1,
    PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH: 2,
}


@dataclass(frozen=True)
class PhilosophieVerfassungsNorm:
    philosophie_verfassung_id: str
    philosophie_typ: PhilosophieVerfassungsTyp
    prozedur: PhilosophieVerfassungsProzedur
    geltung: PhilosophieVerfassungsGeltung
    philosophie_weight: float
    philosophie_tier: int
    canonical: bool
    philosophie_ids: tuple[str, ...]
    philosophie_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhilosophieVerfassung:
    verfassung_id: str
    meta_kognitions_charta: MetaKognitionsCharta
    normen: tuple[PhilosophieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.philosophie_verfassung_id for n in self.normen if n.geltung is PhilosophieVerfassungsGeltung.GESPERRT)

    @property
    def philosophisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.philosophie_verfassung_id for n in self.normen if n.geltung is PhilosophieVerfassungsGeltung.PHILOSOPHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.philosophie_verfassung_id for n in self.normen if n.geltung is PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH)

    @property
    def verfassung_signal(self):
        if any(n.geltung is PhilosophieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is PhilosophieVerfassungsGeltung.PHILOSOPHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-philosophisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-philosophisch")


def build_philosophie_verfassung(
    meta_kognitions_charta: MetaKognitionsCharta | None = None,
    *,
    verfassung_id: str = "philosophie-verfassung",
) -> PhilosophieVerfassung:
    if meta_kognitions_charta is None:
        meta_kognitions_charta = build_meta_kognitions_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[PhilosophieVerfassungsNorm] = []
    for parent_norm in meta_kognitions_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.meta_kognitions_charta_id.removeprefix(f'{meta_kognitions_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.meta_kognitions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.meta_kognitions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhilosophieVerfassungsGeltung.GRUNDLEGEND_PHILOSOPHISCH)
        normen.append(
            PhilosophieVerfassungsNorm(
                philosophie_verfassung_id=new_id,
                philosophie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                philosophie_weight=new_weight,
                philosophie_tier=new_tier,
                canonical=is_canonical,
                philosophie_ids=parent_norm.meta_kognitions_ids + (new_id,),
                philosophie_tags=parent_norm.meta_kognitions_tags + (f"philosophie-verfassung:{new_geltung.value}",),
            )
        )
    return PhilosophieVerfassung(
        verfassung_id=verfassung_id,
        meta_kognitions_charta=meta_kognitions_charta,
        normen=tuple(normen),
    )
