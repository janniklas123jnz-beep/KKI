"""
#490 KybernetikVerfassung — Block-Krone: Systemtheorie & Kybernetik.
Wiener/Beer/Ashby → Luhmann/Parsons → Maturana/Varela → Cannon/Bateson →
von Foerster → Beer VSM → von Foerster/Glasersfeld → Bateson/Beer/Luhmann →
Kauffman/Holland/Bak: Die vollständige Systemarchitektur für Peta-Schwarmgröße.
Leitsterns Terra-Schwarm vereint alle kybernetischen Ebenen: von der ersten Ordnung
(Feedback, Homöostase) über Autopoiesis, Zweite-Ordnung-Kybernetik, Viable System Model
und Systemische Normen bis zur Komplexitätsadaption an der Grenze von Ordnung und Chaos —
ein kybernetisch fundiertes Selbstregulationssystem für den Terra-Schwarm Leitstern
auf dem Weg zur Peta-Schwarmgröße. 🐝⚛️
Geltungsstufen: GESPERRT / KYBERNETISCH_SOUVERAEN / GRUNDLEGEND_KYBERNETISCH_SOUVERAEN
Parent: KomplexitaetsAdaptionsCharta (#489)
Block #481–#490: Systemtheorie & Kybernetik — Block-Krone Milestone #29 ⭐
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .komplexitaets_adaptions_charta import (
    KomplexitaetsAdaptionsCharta,
    KomplexitaetsAdaptionsChartaGeltung,
    build_komplexitaets_adaptions_charta,
)

_GELTUNG_MAP: dict[KomplexitaetsAdaptionsChartaGeltung, "KybernetikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KomplexitaetsAdaptionsChartaGeltung.GESPERRT] = KybernetikVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[KomplexitaetsAdaptionsChartaGeltung.KOMPLEXITAETSADAPTIV] = KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN
    _GELTUNG_MAP[KomplexitaetsAdaptionsChartaGeltung.GRUNDLEGEND_KOMPLEXITAETSADAPTIV] = KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN


class KybernetikVerfassungsTyp(Enum):
    SCHUTZ_KYBERNETIK = "schutz-kybernetik-verfassung"
    ORDNUNGS_KYBERNETIK = "ordnungs-kybernetik-verfassung"
    SOUVERAENITAETS_KYBERNETIK = "souveraenitaets-kybernetik-verfassung"


class KybernetikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KybernetikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KYBERNETISCH_SOUVERAEN = "kybernetisch-souveraen"
    GRUNDLEGEND_KYBERNETISCH_SOUVERAEN = "grundlegend-kybernetisch-souveraen"


_init_map()

_TYP_MAP: dict[KybernetikVerfassungsGeltung, KybernetikVerfassungsTyp] = {
    KybernetikVerfassungsGeltung.GESPERRT: KybernetikVerfassungsTyp.SCHUTZ_KYBERNETIK,
    KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN: KybernetikVerfassungsTyp.ORDNUNGS_KYBERNETIK,
    KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN: KybernetikVerfassungsTyp.SOUVERAENITAETS_KYBERNETIK,
}

_PROZEDUR_MAP: dict[KybernetikVerfassungsGeltung, KybernetikVerfassungsProzedur] = {
    KybernetikVerfassungsGeltung.GESPERRT: KybernetikVerfassungsProzedur.NOTPROZEDUR,
    KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN: KybernetikVerfassungsProzedur.REGELPROTOKOLL,
    KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN: KybernetikVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KybernetikVerfassungsGeltung, float] = {
    KybernetikVerfassungsGeltung.GESPERRT: 0.0,
    KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN: 0.04,
    KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN: 0.08,
}

_TIER_DELTA: dict[KybernetikVerfassungsGeltung, int] = {
    KybernetikVerfassungsGeltung.GESPERRT: 0,
    KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN: 1,
    KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN: 2,
}


@dataclass(frozen=True)
class KybernetikVerfassungsNorm:
    kybernetik_verfassung_id: str
    kybernetik_typ: KybernetikVerfassungsTyp
    prozedur: KybernetikVerfassungsProzedur
    geltung: KybernetikVerfassungsGeltung
    kybernetik_weight: float
    kybernetik_tier: int
    canonical: bool
    kybernetik_ids: tuple[str, ...]
    kybernetik_tags: tuple[str, ...]


@dataclass(frozen=True)
class KybernetikVerfassung:
    verfassung_id: str
    komplexitaets_adaptions_charta: KomplexitaetsAdaptionsCharta
    normen: tuple[KybernetikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_verfassung_id for n in self.normen if n.geltung is KybernetikVerfassungsGeltung.GESPERRT)

    @property
    def kybernetisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_verfassung_id for n in self.normen if n.geltung is KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kybernetik_verfassung_id for n in self.normen if n.geltung is KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KybernetikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KybernetikVerfassungsGeltung.KYBERNETISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-kybernetisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-kybernetisch-souveraen")


def build_kybernetik_verfassung(
    komplexitaets_adaptions_charta: KomplexitaetsAdaptionsCharta | None = None,
    *,
    verfassung_id: str = "kybernetik-verfassung",
) -> KybernetikVerfassung:
    if komplexitaets_adaptions_charta is None:
        komplexitaets_adaptions_charta = build_komplexitaets_adaptions_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[KybernetikVerfassungsNorm] = []
    for parent_norm in komplexitaets_adaptions_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.komplexitaets_adaptions_charta_id.removeprefix(f'{komplexitaets_adaptions_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.komplexitaets_adaptions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.komplexitaets_adaptions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KybernetikVerfassungsGeltung.GRUNDLEGEND_KYBERNETISCH_SOUVERAEN)
        normen.append(
            KybernetikVerfassungsNorm(
                kybernetik_verfassung_id=new_id,
                kybernetik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kybernetik_weight=new_weight,
                kybernetik_tier=new_tier,
                canonical=is_canonical,
                kybernetik_ids=parent_norm.komplexitaets_adaptions_ids + (new_id,),
                kybernetik_tags=parent_norm.komplexitaets_adaptions_tags + (f"kybernetik-verfassung:{new_geltung.value}",),
            )
        )
    return KybernetikVerfassung(
        verfassung_id=verfassung_id,
        komplexitaets_adaptions_charta=komplexitaets_adaptions_charta,
        normen=tuple(normen),
    )
