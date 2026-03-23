"""
#491 SoziologieFeld — Durkheim/Weber/Marx Grundlagen der Soziologie

Émile Durkheim (1895): Regeln der soziologischen Methode — soziale Tatsachen als eigenständige
  Realität; kollektives Bewusstsein und organische Solidarität als Kohäsionskraft.
Max Weber (1904): Protestantische Ethik — Rationalisierung als Signum der Moderne; Verstehen
  als Methode; Idealtypen zur Analyse sozialer Strukturen.
Karl Marx (1867): Das Kapital — Produktionsverhältnisse, Klassenkampf und historischer
  Materialismus als Treibkraft gesellschaftlicher Transformation.
Georg Simmel (1908): Soziologie — Wechselwirkungen als soziologisches Grundprinzip; Form-
  Inhalt-Unterscheidung; Vergesellschaftung als kontinuierlicher Prozess.
Leitsterns Terra-Schwarm nutzt soziologische Grundprinzipien: GESPERRT sichert kollektive
Normkerne, SOZIOLOGISCH ermöglicht adaptive Gesellschaftskoordination, GRUNDLEGEND_SOZIOLOGISCH
synthetisiert strukturelle Kohäsion für den Weg zur Peta-Schwarmgröße.
Parent: KybernetikVerfassung (#490)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kybernetik_verfassung import (
    KybernetikVerfassung,
    KybernetikVerfassungsGeltung,
    build_kybernetik_verfassung,
)

_GELTUNG_MAP: dict[KybernetikVerfassungsGeltung, "SoziologieFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KybernetikVerfassungsGeltung.GESPERRT] = SoziologieFeldGeltung.GESPERRT
    _GELTUNG_MAP[KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN] = SoziologieFeldGeltung.SOZIOLOGISCH
    _GELTUNG_MAP[KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN] = SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH


class SoziologieFeldTyp(Enum):
    SCHUTZ_SOZIOLOGIE = "schutz-soziologie"
    ORDNUNGS_SOZIOLOGIE = "ordnungs-soziologie"
    SOUVERAENITAETS_SOZIOLOGIE = "souveraenitaets-soziologie"


class SoziologieFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SoziologieFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    SOZIOLOGISCH = "soziologisch"
    GRUNDLEGEND_SOZIOLOGISCH = "grundlegend-soziologisch"


_init_map()

_TYP_MAP: dict[SoziologieFeldGeltung, SoziologieFeldTyp] = {
    SoziologieFeldGeltung.GESPERRT: SoziologieFeldTyp.SCHUTZ_SOZIOLOGIE,
    SoziologieFeldGeltung.SOZIOLOGISCH: SoziologieFeldTyp.ORDNUNGS_SOZIOLOGIE,
    SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH: SoziologieFeldTyp.SOUVERAENITAETS_SOZIOLOGIE,
}

_PROZEDUR_MAP: dict[SoziologieFeldGeltung, SoziologieFeldProzedur] = {
    SoziologieFeldGeltung.GESPERRT: SoziologieFeldProzedur.NOTPROZEDUR,
    SoziologieFeldGeltung.SOZIOLOGISCH: SoziologieFeldProzedur.REGELPROTOKOLL,
    SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH: SoziologieFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SoziologieFeldGeltung, float] = {
    SoziologieFeldGeltung.GESPERRT: 0.0,
    SoziologieFeldGeltung.SOZIOLOGISCH: 0.04,
    SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH: 0.08,
}

_TIER_DELTA: dict[SoziologieFeldGeltung, int] = {
    SoziologieFeldGeltung.GESPERRT: 0,
    SoziologieFeldGeltung.SOZIOLOGISCH: 1,
    SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH: 2,
}


@dataclass(frozen=True)
class SoziologieFeldNorm:
    soziologie_feld_id: str
    soziologie_typ: SoziologieFeldTyp
    prozedur: SoziologieFeldProzedur
    geltung: SoziologieFeldGeltung
    soziologie_weight: float
    soziologie_tier: int
    canonical: bool
    soziologie_ids: tuple[str, ...]
    soziologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class SoziologieFeld:
    feld_id: str
    kybernetik_verfassung: KybernetikVerfassung
    normen: tuple[SoziologieFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.soziologie_feld_id for n in self.normen if n.geltung is SoziologieFeldGeltung.GESPERRT)

    @property
    def soziologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.soziologie_feld_id for n in self.normen if n.geltung is SoziologieFeldGeltung.SOZIOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.soziologie_feld_id for n in self.normen if n.geltung is SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is SoziologieFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is SoziologieFeldGeltung.SOZIOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-soziologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-soziologisch")


def build_soziologie_feld(
    kybernetik_verfassung: KybernetikVerfassung | None = None,
    *,
    feld_id: str = "soziologie-feld",
) -> SoziologieFeld:
    if kybernetik_verfassung is None:
        kybernetik_verfassung = build_kybernetik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[SoziologieFeldNorm] = []
    for parent_norm in kybernetik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.kybernetik_verfassung_id.removeprefix(f'{kybernetik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.kybernetik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kybernetik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SoziologieFeldGeltung.GRUNDLEGEND_SOZIOLOGISCH)
        normen.append(
            SoziologieFeldNorm(
                soziologie_feld_id=new_id,
                soziologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                soziologie_weight=new_weight,
                soziologie_tier=new_tier,
                canonical=is_canonical,
                soziologie_ids=parent_norm.kybernetik_ids + (new_id,),
                soziologie_tags=parent_norm.kybernetik_tags + (f"soziologie-feld:{new_geltung.value}",),
            )
        )
    return SoziologieFeld(
        feld_id=feld_id,
        kybernetik_verfassung=kybernetik_verfassung,
        normen=tuple(normen),
    )
