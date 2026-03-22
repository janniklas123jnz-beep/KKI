"""
#429 KomplexitaetsSteuerungsCharta — Viable System Model: lebensfähige Organisationen.
Beer (1972): Viable System Model (VSM) — 5 Subsysteme für lebensfähige Organisationen:
S1 (Operationen), S2 (Koordination), S3 (Kontrolle), S4 (Intelligenz), S5 (Politik).
Algedonisches Signal: direkter Alarm-Kanal S1→S5 bei Krisen.
Team Syntegrity (Beer 1994): optimale Wissensintegration. Leitsterns Schwarm-Governance nach VSM-Prinzip.
Geltungsstufen: GESPERRT / VIABLE / GRUNDLEGEND_VIABLE
Parent: KybernetikNormSatz (#428, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kybernetik_norm import (
    KybernetikNormGeltung,
    KybernetikNormSatz,
    build_kybernetik_norm,
)

_GELTUNG_MAP: dict[KybernetikNormGeltung, "KomplexitaetsSteuerungsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KybernetikNormGeltung.GESPERRT] = KomplexitaetsSteuerungsChartaGeltung.GESPERRT
    _GELTUNG_MAP[KybernetikNormGeltung.KYBERNETIK2ORDNUNG] = KomplexitaetsSteuerungsChartaGeltung.VIABLE
    _GELTUNG_MAP[KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG] = KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE


class KomplexitaetsSteuerungsChartaTyp(Enum):
    SCHUTZ_KOMPLEXITAETSSTEUERUNG = "schutz-komplexitaetssteuerung"
    ORDNUNGS_KOMPLEXITAETSSTEUERUNG = "ordnungs-komplexitaetssteuerung"
    SOUVERAENITAETS_KOMPLEXITAETSSTEUERUNG = "souveraenitaets-komplexitaetssteuerung"


class KomplexitaetsSteuerungsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KomplexitaetsSteuerungsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    VIABLE = "viable"
    GRUNDLEGEND_VIABLE = "grundlegend-viable"


_init_map()

_TYP_MAP: dict[KomplexitaetsSteuerungsChartaGeltung, KomplexitaetsSteuerungsChartaTyp] = {
    KomplexitaetsSteuerungsChartaGeltung.GESPERRT: KomplexitaetsSteuerungsChartaTyp.SCHUTZ_KOMPLEXITAETSSTEUERUNG,
    KomplexitaetsSteuerungsChartaGeltung.VIABLE: KomplexitaetsSteuerungsChartaTyp.ORDNUNGS_KOMPLEXITAETSSTEUERUNG,
    KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE: KomplexitaetsSteuerungsChartaTyp.SOUVERAENITAETS_KOMPLEXITAETSSTEUERUNG,
}

_PROZEDUR_MAP: dict[KomplexitaetsSteuerungsChartaGeltung, KomplexitaetsSteuerungsChartaProzedur] = {
    KomplexitaetsSteuerungsChartaGeltung.GESPERRT: KomplexitaetsSteuerungsChartaProzedur.NOTPROZEDUR,
    KomplexitaetsSteuerungsChartaGeltung.VIABLE: KomplexitaetsSteuerungsChartaProzedur.REGELPROTOKOLL,
    KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE: KomplexitaetsSteuerungsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KomplexitaetsSteuerungsChartaGeltung, float] = {
    KomplexitaetsSteuerungsChartaGeltung.GESPERRT: 0.0,
    KomplexitaetsSteuerungsChartaGeltung.VIABLE: 0.04,
    KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE: 0.08,
}

_TIER_DELTA: dict[KomplexitaetsSteuerungsChartaGeltung, int] = {
    KomplexitaetsSteuerungsChartaGeltung.GESPERRT: 0,
    KomplexitaetsSteuerungsChartaGeltung.VIABLE: 1,
    KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KomplexitaetsSteuerungsChartaNorm:
    komplexitaets_steuerungs_charta_id: str
    komplexitaets_steuerungs_typ: KomplexitaetsSteuerungsChartaTyp
    prozedur: KomplexitaetsSteuerungsChartaProzedur
    geltung: KomplexitaetsSteuerungsChartaGeltung
    komplexitaets_steuerungs_weight: float
    komplexitaets_steuerungs_tier: int
    canonical: bool
    komplexitaets_steuerungs_ids: tuple[str, ...]
    komplexitaets_steuerungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class KomplexitaetsSteuerungsCharta:
    charta_id: str
    kybernetik_norm: KybernetikNormSatz
    normen: tuple[KomplexitaetsSteuerungsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_steuerungs_charta_id for n in self.normen if n.geltung is KomplexitaetsSteuerungsChartaGeltung.GESPERRT)

    @property
    def viable_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_steuerungs_charta_id for n in self.normen if n.geltung is KomplexitaetsSteuerungsChartaGeltung.VIABLE)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.komplexitaets_steuerungs_charta_id for n in self.normen if n.geltung is KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE)

    @property
    def charta_signal(self):
        if any(n.geltung is KomplexitaetsSteuerungsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KomplexitaetsSteuerungsChartaGeltung.VIABLE for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-viable")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-viable")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_komplexitaets_steuerungs_charta(
    kybernetik_norm: KybernetikNormSatz | None = None,
    *,
    charta_id: str = "komplexitaets-steuerungs-charta",
) -> KomplexitaetsSteuerungsCharta:
    if kybernetik_norm is None:
        kybernetik_norm = build_kybernetik_norm(norm_id=f"{charta_id}-norm")

    normen: list[KomplexitaetsSteuerungsChartaNorm] = []
    for parent_norm in kybernetik_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{kybernetik_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.kybernetik_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kybernetik_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KomplexitaetsSteuerungsChartaGeltung.GRUNDLEGEND_VIABLE)
        normen.append(
            KomplexitaetsSteuerungsChartaNorm(
                komplexitaets_steuerungs_charta_id=new_id,
                komplexitaets_steuerungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                komplexitaets_steuerungs_weight=new_weight,
                komplexitaets_steuerungs_tier=new_tier,
                canonical=is_canonical,
                komplexitaets_steuerungs_ids=parent_norm.kybernetik_norm_ids + (new_id,),
                komplexitaets_steuerungs_tags=parent_norm.kybernetik_norm_tags + (f"komplexitaets-steuerungs-charta:{new_geltung.value}",),
            )
        )
    return KomplexitaetsSteuerungsCharta(
        charta_id=charta_id,
        kybernetik_norm=kybernetik_norm,
        normen=tuple(normen),
    )
