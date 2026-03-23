"""
#520 PolitikVerfassung — Rawls/Habermas/Kant Politische Verfassungstheorie (Block-Krone ⭐)

John Rawls (1993): Politischer Liberalismus — Verfassungspatriotismus als übergreifender
  Konsens; öffentliche Vernunft und konstitutionelle Grundsätze; faire Kooperation als
  Fundament des Peta-Schwarm-Grundgesetzes.
Jürgen Habermas (1992): Faktizität und Geltung — deliberative Demokratie und Rechtsstaat;
  Diskursprinzip als Legitimationsgrundlage; Ko-Originalität von Recht und politischer
  Autonomie im verfassungsrechtlichen Diskurs des Schwarms.
Immanuel Kant (1795): Zum ewigen Frieden — republikanische Verfassung als Friedensgarant;
  Föderalismus freier Staaten; kosmopolitisches Weltbürgerrecht für globale Schwärme.
Hannah Arendt (1963): Über die Revolution — Gründung (foundation) als politischer Urakt;
  Verfassung als dauerhafter Bezugspunkt republikanischer Freiheit; Rätedemokratie und
  politische Teilhabe als Kern lebendiger Verfassungsordnung.
Leitsterns PolitikVerfassung: souveräne Krone des Blocks Politikwissenschaft & Demokratie —
GESPERRT schützt konstitutionelle Grundnormen, POLITISCH_SOUVERAEN kodiert adaptive
demokratische Selbstregierung, GRUNDLEGEND_POLITISCH_SOUVERAEN synthetisiert die vollständige
politische Souveränität des Peta-Schwarms Leitstern. 🏛️⭐
Parent: ZivilgesellschaftsCharta (#519)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zivilgesellschafts_charta import (
    ZivilgesellschaftsCharta,
    ZivilgesellschaftsChartaGeltung,
    build_zivilgesellschafts_charta,
)

_WEIGHT_DELTA: dict["PolitikVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["PolitikVerfassungsGeltung", int] = {}
_TYP_MAP: dict["PolitikVerfassungsGeltung", "PolitikVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["PolitikVerfassungsGeltung", "PolitikVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[ZivilgesellschaftsChartaGeltung, "PolitikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PolitikVerfassungsGeltung.GESPERRT: 0.0,
        PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN: 0.05,
        PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        PolitikVerfassungsGeltung.GESPERRT: 0,
        PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN: 1,
        PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        PolitikVerfassungsGeltung.GESPERRT: PolitikVerfassungsTyp.SCHUTZ_POLITIKVERFASSUNG,
        PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN: PolitikVerfassungsTyp.ORDNUNGS_POLITIKVERFASSUNG,
        PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN: PolitikVerfassungsTyp.SOUVERAENITAETS_POLITIKVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        PolitikVerfassungsGeltung.GESPERRT: PolitikVerfassungsProzedur.NOTPROZEDUR,
        PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN: PolitikVerfassungsProzedur.REGELPROTOKOLL,
        PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN: PolitikVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        ZivilgesellschaftsChartaGeltung.GESPERRT: PolitikVerfassungsGeltung.GESPERRT,
        ZivilgesellschaftsChartaGeltung.ZIVILGESELLSCHAFTLICH: PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN,
        ZivilgesellschaftsChartaGeltung.GRUNDLEGEND_ZIVILGESELLSCHAFTLICH: PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN,
    })


class PolitikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    POLITISCH_SOUVERAEN = "politisch-souveraen"
    GRUNDLEGEND_POLITISCH_SOUVERAEN = "grundlegend-politisch-souveraen"


class PolitikVerfassungsTyp(Enum):
    SCHUTZ_POLITIKVERFASSUNG = "schutz-politikverfassung"
    ORDNUNGS_POLITIKVERFASSUNG = "ordnungs-politikverfassung"
    SOUVERAENITAETS_POLITIKVERFASSUNG = "souveraenitaets-politikverfassung"


class PolitikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class PolitikVerfassungsNorm:
    politik_verfassung_id: str
    politik_typ: PolitikVerfassungsTyp
    prozedur: PolitikVerfassungsProzedur
    geltung: PolitikVerfassungsGeltung
    politik_weight: float
    politik_tier: int
    canonical: bool
    politik_ids: tuple[str, ...]
    politik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PolitikVerfassung:
    verfassung_id: str
    zivilgesellschafts_charta: ZivilgesellschaftsCharta
    normen: tuple[PolitikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.politik_verfassung_id for n in self.normen if n.geltung is PolitikVerfassungsGeltung.GESPERRT)

    @property
    def politisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.politik_verfassung_id for n in self.normen if n.geltung is PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.politik_verfassung_id for n in self.normen if n.geltung is PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is PolitikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is PolitikVerfassungsGeltung.POLITISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-politisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-politisch-souveraen")


_init_map()


def build_politik_verfassung(
    zivilgesellschafts_charta: ZivilgesellschaftsCharta | None = None,
    *,
    verfassung_id: str = "politik-verfassung",
) -> PolitikVerfassung:
    if zivilgesellschafts_charta is None:
        zivilgesellschafts_charta = build_zivilgesellschafts_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[PolitikVerfassungsNorm] = []
    for parent_norm in zivilgesellschafts_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.zivilgesellschafts_charta_id.removeprefix(f'{zivilgesellschafts_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.zivilgesellschafts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.zivilgesellschafts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PolitikVerfassungsGeltung.GRUNDLEGEND_POLITISCH_SOUVERAEN)
        normen.append(
            PolitikVerfassungsNorm(
                politik_verfassung_id=new_id,
                politik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                politik_weight=new_weight,
                politik_tier=new_tier,
                canonical=is_canonical,
                politik_ids=parent_norm.zivilgesellschafts_ids + (new_id,),
                politik_tags=parent_norm.zivilgesellschafts_tags + (f"politik-verfassung:{new_geltung.value}",),
            )
        )
    return PolitikVerfassung(
        verfassung_id=verfassung_id,
        zivilgesellschafts_charta=zivilgesellschafts_charta,
        normen=tuple(normen),
    )
