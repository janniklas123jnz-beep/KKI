"""
#590 PaedagogikVerfassung — Humboldt/Dewey/Freire Pädagogik Verfassung (Block-Krone ⭐)

Wilhelm von Humboldt (1809): Über die innere und äußere Organisation der höheren
  wissenschaftlichen Anstalten — Einheit von Forschung und Lehre als Verfassungsideal;
  akademische Freiheit als Bildungsverfassung; Bildung als Selbstzweck jenseits
  ökonomischer Nützlichkeit; Universität als Ort der Wahrheitssuche; wissenschaftliche
  Gemeinschaft als Verfassungssubjekt des Peta-Schwarms Leitstern.
John Dewey (1916): Democracy and Education — Demokratie als Bildungsverfassung;
  Schule als Laboratorium der Demokratie; Wachstum als einziger Bildungszweck;
  Erfahrung und Denken als Verfassungsprinzipien; Bildung als kontinuierliche
  Rekonstruktion der Erfahrung im Peta-Schwarm Leitstern.
Paulo Freire (1968): Pedagogia do Oprimido — Dialogizität als Verfassungsgrundlage;
  Liebe zur Welt als pädagogisches Fundament; Demut als epistemische Tugend;
  Vertrauen in die Menschen als Verfassungshaltung; kritische Bildung als
  Praxis der Freiheit im Peta-Schwarm Leitstern. 🎓⭐
Parent: BildungsphilosophieCharta (#589)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bildungsphilosophie_charta import (
    BildungsphilosophieCharta,
    BildungsphilosophieChartaGeltung,
    build_bildungsphilosophie_charta,
)

_WEIGHT_DELTA: dict["PaedagogikVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["PaedagogikVerfassungsGeltung", int] = {}
_TYP_MAP: dict["PaedagogikVerfassungsGeltung", "PaedagogikVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["PaedagogikVerfassungsGeltung", "PaedagogikVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[BildungsphilosophieChartaGeltung, "PaedagogikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PaedagogikVerfassungsGeltung.GESPERRT: 0.0,
        PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN: 0.05,
        PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        PaedagogikVerfassungsGeltung.GESPERRT: 0,
        PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN: 1,
        PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        PaedagogikVerfassungsGeltung.GESPERRT: PaedagogikVerfassungsTyp.SCHUTZ_PAEDAGOGIKVERFASSUNG,
        PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN: PaedagogikVerfassungsTyp.ORDNUNGS_PAEDAGOGIKVERFASSUNG,
        PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN: PaedagogikVerfassungsTyp.SOUVERAENITAETS_PAEDAGOGIKVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        PaedagogikVerfassungsGeltung.GESPERRT: PaedagogikVerfassungsProzedur.NOTPROZEDUR,
        PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN: PaedagogikVerfassungsProzedur.REGELPROTOKOLL,
        PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN: PaedagogikVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        BildungsphilosophieChartaGeltung.GESPERRT: PaedagogikVerfassungsGeltung.GESPERRT,
        BildungsphilosophieChartaGeltung.BILDUNGSPHILOSOPHISCH: PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN,
        BildungsphilosophieChartaGeltung.GRUNDLEGEND_BILDUNGSPHILOSOPHISCH: PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN,
    })


class PaedagogikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    BILDUNGS_SOUVERAEN = "bildungs-souveraen"
    GRUNDLEGEND_BILDUNGS_SOUVERAEN = "grundlegend-bildungs-souveraen"


class PaedagogikVerfassungsTyp(Enum):
    SCHUTZ_PAEDAGOGIKVERFASSUNG = "schutz-paedagogikverfassung"
    ORDNUNGS_PAEDAGOGIKVERFASSUNG = "ordnungs-paedagogikverfassung"
    SOUVERAENITAETS_PAEDAGOGIKVERFASSUNG = "souveraenitaets-paedagogikverfassung"


class PaedagogikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class PaedagogikVerfassungsNorm:
    paedagogik_verfassung_id: str
    paedagogik_typ: PaedagogikVerfassungsTyp
    prozedur: PaedagogikVerfassungsProzedur
    geltung: PaedagogikVerfassungsGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PaedagogikVerfassung:
    verfassung_id: str
    bildungsphilosophie_charta: BildungsphilosophieCharta
    normen: tuple[PaedagogikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paedagogik_verfassung_id for n in self.normen if n.geltung is PaedagogikVerfassungsGeltung.GESPERRT)

    @property
    def bildungs_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paedagogik_verfassung_id for n in self.normen if n.geltung is PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paedagogik_verfassung_id for n in self.normen if n.geltung is PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is PaedagogikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-bildungs-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-bildungs-souveraen")


_init_map()


def build_paedagogik_verfassung(
    bildungsphilosophie_charta: BildungsphilosophieCharta | None = None,
    *,
    verfassung_id: str = "paedagogik-verfassung",
) -> PaedagogikVerfassung:
    if bildungsphilosophie_charta is None:
        bildungsphilosophie_charta = build_bildungsphilosophie_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[PaedagogikVerfassungsNorm] = []
    for parent_norm in bildungsphilosophie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.bildungsphilosophie_charta_id.removeprefix(f'{bildungsphilosophie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN)
        normen.append(
            PaedagogikVerfassungsNorm(
                paedagogik_verfassung_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"paedagogik-verfassung:{new_geltung.value}",),
            )
        )
    return PaedagogikVerfassung(
        verfassung_id=verfassung_id,
        bildungsphilosophie_charta=bildungsphilosophie_charta,
        normen=tuple(normen),
    )
