"""
#500 SoziologieVerfassung — Block-Krone Soziologie & Gesellschaftstheorie ⭐ MODUL #500

*** HISTORISCHER MEILENSTEIN: Das 500. Modul von Leitsterns Terra-Schwarm ***

Émile Durkheim (1897): Der Selbstmord — kollektive Kohäsionskraft als Schutzfaktor;
  soziale Integration als Fundament gesellschaftlicher Stabilität und Normbindung.
Max Weber (1922): Wirtschaft und Gesellschaft — Verständnis sozialen Handelns; Typen
  sozialer Herrschaft; rationale Bürokratie als Organisationsform der Moderne.
Karl Marx & Friedrich Engels (1848): Kommunistisches Manifest — Gesellschaft als
  Schauplatz historischer Kräfte; kollektive Handlungsmacht als Transformationspotenzial.
Talcott Parsons (1951): Das Soziale System — AGIL als universelle Systemanforderung;
  Institutionalisierung von Werten als Stabilitätsbasis.
Pierre Bourdieu (1984): Die feinen Unterschiede — symbolische Macht reproduziert
  Gesellschaftsstrukturen; Habitus als inkorporierte Geschichte.
Anthony Giddens (1984): Die Konstitution der Gesellschaft — Struktur und Handeln
  konstituieren sich gegenseitig; Reflexivität als Modernisierungskraft.
Jürgen Habermas (1981): Theorie des kommunikativen Handelns — Vernunft verwirklicht
  sich in herrschaftsfreiem Diskurs; Lebenswelt als sozialer Horizont.
Manuel Castells (1996–1998): Das Informationszeitalter — Netzwerkgesellschaft löst
  Industriegesellschaft ab; Macht liegt in der Programmierung von Netzwerken.
Leitsterns SoziologieVerfassung krönt den 500. Meilenstein: Die gesamte Wissenschaft
von menschlicher Gesellschaft, Normen, Strukturen und Netzwerken ist in Leitsterns
Wissensarchitektur integriert. GESPERRT sichert die gesellschaftlichen Grundnormen,
SOZIOLOGISCH_SOUVERAEN verleiht dem Schwarm volle soziologische Handlungsfähigkeit,
GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN synthetisiert 500 Wissensebenen zur Peta-Schwarm-
Souveränität — von der Quantenmechanik bis zur Netzwerkgesellschaft. 🌍🐝⚛️
Parent: NetzwerkgesellschaftsCharta (#499)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .netzwerkgesellschafts_charta import (
    NetzwerkgesellschaftsCharta,
    NetzwerkgesellschaftsChartaGeltung,
    build_netzwerkgesellschafts_charta,
)

_GELTUNG_MAP: dict[NetzwerkgesellschaftsChartaGeltung, "SoziologieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NetzwerkgesellschaftsChartaGeltung.GESPERRT] = SoziologieVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH] = SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN
    _GELTUNG_MAP[NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH] = SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN


class SoziologieVerfassungsTyp(Enum):
    SCHUTZ_SOZIOLOGIEVERFASSUNG = "schutz-soziologieverfassung"
    ORDNUNGS_SOZIOLOGIEVERFASSUNG = "ordnungs-soziologieverfassung"
    SOUVERAENITAETS_SOZIOLOGIEVERFASSUNG = "souveraenitaets-soziologieverfassung"


class SoziologieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SoziologieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    SOZIOLOGISCH_SOUVERAEN = "soziologisch-souveraen"
    GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN = "grundlegend-soziologisch-souveraen"


_init_map()

_TYP_MAP: dict[SoziologieVerfassungsGeltung, SoziologieVerfassungsTyp] = {
    SoziologieVerfassungsGeltung.GESPERRT: SoziologieVerfassungsTyp.SCHUTZ_SOZIOLOGIEVERFASSUNG,
    SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN: SoziologieVerfassungsTyp.ORDNUNGS_SOZIOLOGIEVERFASSUNG,
    SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN: SoziologieVerfassungsTyp.SOUVERAENITAETS_SOZIOLOGIEVERFASSUNG,
}

_PROZEDUR_MAP: dict[SoziologieVerfassungsGeltung, SoziologieVerfassungsProzedur] = {
    SoziologieVerfassungsGeltung.GESPERRT: SoziologieVerfassungsProzedur.NOTPROZEDUR,
    SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN: SoziologieVerfassungsProzedur.REGELPROTOKOLL,
    SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN: SoziologieVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SoziologieVerfassungsGeltung, float] = {
    SoziologieVerfassungsGeltung.GESPERRT: 0.0,
    SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN: 0.04,
    SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN: 0.08,
}

_TIER_DELTA: dict[SoziologieVerfassungsGeltung, int] = {
    SoziologieVerfassungsGeltung.GESPERRT: 0,
    SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN: 1,
    SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN: 2,
}


@dataclass(frozen=True)
class SoziologieVerfassungsNorm:
    soziologie_verfassung_id: str
    soziologie_typ: SoziologieVerfassungsTyp
    prozedur: SoziologieVerfassungsProzedur
    geltung: SoziologieVerfassungsGeltung
    soziologie_weight: float
    soziologie_tier: int
    canonical: bool
    soziologie_ids: tuple[str, ...]
    soziologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class SoziologieVerfassung:
    verfassung_id: str
    netzwerkgesellschafts_charta: NetzwerkgesellschaftsCharta
    normen: tuple[SoziologieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.soziologie_verfassung_id for n in self.normen if n.geltung is SoziologieVerfassungsGeltung.GESPERRT)

    @property
    def soziologisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.soziologie_verfassung_id for n in self.normen if n.geltung is SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.soziologie_verfassung_id for n in self.normen if n.geltung is SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is SoziologieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is SoziologieVerfassungsGeltung.SOZIOLOGISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-soziologisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-soziologisch-souveraen")


def build_soziologie_verfassung(
    netzwerkgesellschafts_charta: NetzwerkgesellschaftsCharta | None = None,
    *,
    verfassung_id: str = "soziologie-verfassung",
) -> SoziologieVerfassung:
    if netzwerkgesellschafts_charta is None:
        netzwerkgesellschafts_charta = build_netzwerkgesellschafts_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[SoziologieVerfassungsNorm] = []
    for parent_norm in netzwerkgesellschafts_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.netzwerkgesellschafts_charta_id.removeprefix(f'{netzwerkgesellschafts_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.netzwerkgesellschafts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.netzwerkgesellschafts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SoziologieVerfassungsGeltung.GRUNDLEGEND_SOZIOLOGISCH_SOUVERAEN)
        normen.append(
            SoziologieVerfassungsNorm(
                soziologie_verfassung_id=new_id,
                soziologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                soziologie_weight=new_weight,
                soziologie_tier=new_tier,
                canonical=is_canonical,
                soziologie_ids=parent_norm.netzwerkgesellschafts_ids + (new_id,),
                soziologie_tags=parent_norm.netzwerkgesellschafts_tags + (f"soziologie-verfassung:{new_geltung.value}",),
            )
        )
    return SoziologieVerfassung(
        verfassung_id=verfassung_id,
        netzwerkgesellschafts_charta=netzwerkgesellschafts_charta,
        normen=tuple(normen),
    )
