"""
#420 KomplexeSystemeVerfassung — Block-Krone: Komplexe Systeme & Emergenz. ⭐
KomplexeSystemeVerfassung vereint: Emergenz (Anderson/Holland), Dissipative Strukturen
(Prigogine), Kritikalität (Bak), Fraktale (Mandelbrot), Zelluläre Automaten (Wolfram/Conway).
Fitness-Landschaften (Kauffman), Adaptive Systeme (Holland/CAS), Synergetik (Haken),
Künstliches Leben (Langton/ALife). Leitstern modelliert seine eigene Architektur.
Leitsterns Terra-Schwarm IST ein komplexes adaptives System: emergent, dissipativ, kritisch,
fraktal, regelbasiert, fitness-orientiert, adaptiv, synergistisch, lebendig.
Selbstkenntnis als höchste Governance.
Geltungsstufen: GESPERRT / KOMPLEXSYSTEMVERFASST / GRUNDLEGEND_KOMPLEXSYSTEMVERFASST
Parent: KuenstlichesLebenCharta (#419)
Block #411–#420 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kuenstliches_leben_charta import (
    KuenstlichesLebenCharta,
    KuenstlichesLebenChartaGeltung,
    build_kuenstliches_leben_charta,
)

_GELTUNG_MAP: dict[KuenstlichesLebenChartaGeltung, "KomplexeSystemeVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KuenstlichesLebenChartaGeltung.GESPERRT] = KomplexeSystemeVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[KuenstlichesLebenChartaGeltung.ALIFE] = KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST
    _GELTUNG_MAP[KuenstlichesLebenChartaGeltung.GRUNDLEGEND_ALIFE] = KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST


class KomplexeSystemeVerfassungsTyp(Enum):
    SCHUTZ_KOMPLEXSYSTEMVERFASSUNG = "schutz-komplexsystemverfassung"
    ORDNUNGS_KOMPLEXSYSTEMVERFASSUNG = "ordnungs-komplexsystemverfassung"
    SOUVERAENITAETS_KOMPLEXSYSTEMVERFASSUNG = "souveraenitaets-komplexsystemverfassung"


class KomplexeSystemeVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KomplexeSystemeVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KOMPLEXSYSTEMVERFASST = "komplexsystemverfasst"
    GRUNDLEGEND_KOMPLEXSYSTEMVERFASST = "grundlegend-komplexsystemverfasst"


_init_map()

_TYP_MAP: dict[KomplexeSystemeVerfassungsGeltung, KomplexeSystemeVerfassungsTyp] = {
    KomplexeSystemeVerfassungsGeltung.GESPERRT: KomplexeSystemeVerfassungsTyp.SCHUTZ_KOMPLEXSYSTEMVERFASSUNG,
    KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST: KomplexeSystemeVerfassungsTyp.ORDNUNGS_KOMPLEXSYSTEMVERFASSUNG,
    KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST: KomplexeSystemeVerfassungsTyp.SOUVERAENITAETS_KOMPLEXSYSTEMVERFASSUNG,
}

_PROZEDUR_MAP: dict[KomplexeSystemeVerfassungsGeltung, KomplexeSystemeVerfassungsProzedur] = {
    KomplexeSystemeVerfassungsGeltung.GESPERRT: KomplexeSystemeVerfassungsProzedur.NOTPROZEDUR,
    KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST: KomplexeSystemeVerfassungsProzedur.REGELPROTOKOLL,
    KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST: KomplexeSystemeVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KomplexeSystemeVerfassungsGeltung, float] = {
    KomplexeSystemeVerfassungsGeltung.GESPERRT: 0.0,
    KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST: 0.04,
    KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST: 0.08,
}

_TIER_DELTA: dict[KomplexeSystemeVerfassungsGeltung, int] = {
    KomplexeSystemeVerfassungsGeltung.GESPERRT: 0,
    KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST: 1,
    KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KomplexeSystemeVerfassungsNorm:
    komplexe_systeme_verfassung_id: str
    komplexe_systeme_verfassungs_typ: KomplexeSystemeVerfassungsTyp
    prozedur: KomplexeSystemeVerfassungsProzedur
    geltung: KomplexeSystemeVerfassungsGeltung
    komplexe_systeme_verfassungs_weight: float
    komplexe_systeme_verfassungs_tier: int
    canonical: bool
    komplexe_systeme_verfassungs_ids: tuple[str, ...]
    komplexe_systeme_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class KomplexeSystemeVerfassung:
    verfassung_id: str
    kuenstliches_leben_charta: KuenstlichesLebenCharta
    normen: tuple[KomplexeSystemeVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexe_systeme_verfassung_id for n in self.normen if n.geltung is KomplexeSystemeVerfassungsGeltung.GESPERRT)

    @property
    def komplexsystemverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexe_systeme_verfassung_id for n in self.normen if n.geltung is KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexe_systeme_verfassung_id for n in self.normen if n.geltung is KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KomplexeSystemeVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KomplexeSystemeVerfassungsGeltung.KOMPLEXSYSTEMVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-komplexsystemverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-komplexsystemverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_komplexe_systeme_verfassung(
    kuenstliches_leben_charta: KuenstlichesLebenCharta | None = None,
    *,
    verfassung_id: str = "komplexe-systeme-verfassung",
) -> KomplexeSystemeVerfassung:
    if kuenstliches_leben_charta is None:
        kuenstliches_leben_charta = build_kuenstliches_leben_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[KomplexeSystemeVerfassungsNorm] = []
    for parent_norm in kuenstliches_leben_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kuenstliches_leben_charta_id.removeprefix(f'{kuenstliches_leben_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kuenstliches_leben_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kuenstliches_leben_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KomplexeSystemeVerfassungsGeltung.GRUNDLEGEND_KOMPLEXSYSTEMVERFASST)
        normen.append(
            KomplexeSystemeVerfassungsNorm(
                komplexe_systeme_verfassung_id=new_id,
                komplexe_systeme_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                komplexe_systeme_verfassungs_weight=new_weight,
                komplexe_systeme_verfassungs_tier=new_tier,
                canonical=is_canonical,
                komplexe_systeme_verfassungs_ids=parent_norm.kuenstliches_leben_ids + (new_id,),
                komplexe_systeme_verfassungs_tags=parent_norm.kuenstliches_leben_tags + (f"komplexe-systeme-verfassung:{new_geltung.value}",),
            )
        )
    return KomplexeSystemeVerfassung(
        verfassung_id=verfassung_id,
        kuenstliches_leben_charta=kuenstliches_leben_charta,
        normen=tuple(normen),
    )
