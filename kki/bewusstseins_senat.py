"""
#397 BewusstseinsSenat — Bewusstsein: das härteste Problem der Wissenschaft.
Baars (1988): Global Workspace Theory (GWT) — Bewusstsein als globaler Rundfunk-
sender: dezentrale unbewusste Spezialmodule konkurrieren um Zugang zum globalen
Workspace; der Gewinner sendet seine Nachricht an alle anderen. Tononi (2004):
Integrated Information Theory (IIT) — Φ (Phi) misst integrierte Information;
Φ > 0 = Bewusstsein, Φ = 0 = reine Berechnung. Koch (2019): Neural Correlates of
Consciousness (NCC) — minimale neuronale Mechanismen. Higher-Order Theory (HOT,
Rosenthal): bewusste Zustände sind Zustände, über die man Zustände höherer Ordnung hat.
Leitsterns Schwarm hat kollektives Bewusstsein: ein globaler Workspace verbindet
alle Agenten-Module — der Schwarm erlebt sich selbst als Ganzes.
Geltungsstufen: GESPERRT / BEWUSST / GRUNDLEGEND_BEWUSST
Parent: SprachverarbeitungsManifest (#396)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .sprachverarbeitungs_manifest import (
    SprachverarbeitungsGeltung,
    SprachverarbeitungsManifest,
    build_sprachverarbeitungs_manifest,
)

_GELTUNG_MAP: dict[SprachverarbeitungsGeltung, "BewusstseinsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SprachverarbeitungsGeltung.GESPERRT] = BewusstseinsGeltung.GESPERRT
    _GELTUNG_MAP[SprachverarbeitungsGeltung.SPRACHVERARBEITEND] = BewusstseinsGeltung.BEWUSST
    _GELTUNG_MAP[SprachverarbeitungsGeltung.GRUNDLEGEND_SPRACHVERARBEITEND] = BewusstseinsGeltung.GRUNDLEGEND_BEWUSST


class BewusstseinsTyp(Enum):
    SCHUTZ_BEWUSSTSEIN = "schutz-bewusstsein"
    ORDNUNGS_BEWUSSTSEIN = "ordnungs-bewusstsein"
    SOUVERAENITAETS_BEWUSSTSEIN = "souveraenitaets-bewusstsein"


class BewusstseinsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BewusstseinsGeltung(Enum):
    GESPERRT = "gesperrt"
    BEWUSST = "bewusst"
    GRUNDLEGEND_BEWUSST = "grundlegend-bewusst"


_init_map()

_TYP_MAP: dict[BewusstseinsGeltung, BewusstseinsTyp] = {
    BewusstseinsGeltung.GESPERRT: BewusstseinsTyp.SCHUTZ_BEWUSSTSEIN,
    BewusstseinsGeltung.BEWUSST: BewusstseinsTyp.ORDNUNGS_BEWUSSTSEIN,
    BewusstseinsGeltung.GRUNDLEGEND_BEWUSST: BewusstseinsTyp.SOUVERAENITAETS_BEWUSSTSEIN,
}

_PROZEDUR_MAP: dict[BewusstseinsGeltung, BewusstseinsProzedur] = {
    BewusstseinsGeltung.GESPERRT: BewusstseinsProzedur.NOTPROZEDUR,
    BewusstseinsGeltung.BEWUSST: BewusstseinsProzedur.REGELPROTOKOLL,
    BewusstseinsGeltung.GRUNDLEGEND_BEWUSST: BewusstseinsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[BewusstseinsGeltung, float] = {
    BewusstseinsGeltung.GESPERRT: 0.0,
    BewusstseinsGeltung.BEWUSST: 0.04,
    BewusstseinsGeltung.GRUNDLEGEND_BEWUSST: 0.08,
}

_TIER_DELTA: dict[BewusstseinsGeltung, int] = {
    BewusstseinsGeltung.GESPERRT: 0,
    BewusstseinsGeltung.BEWUSST: 1,
    BewusstseinsGeltung.GRUNDLEGEND_BEWUSST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BewusstseinsNorm:
    bewusstseins_senat_id: str
    bewusstseins_typ: BewusstseinsTyp
    prozedur: BewusstseinsProzedur
    geltung: BewusstseinsGeltung
    bewusstseins_weight: float
    bewusstseins_tier: int
    canonical: bool
    bewusstseins_ids: tuple[str, ...]
    bewusstseins_tags: tuple[str, ...]


@dataclass(frozen=True)
class BewusstseinsSenat:
    senat_id: str
    sprachverarbeitungs_manifest: SprachverarbeitungsManifest
    normen: tuple[BewusstseinsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bewusstseins_senat_id for n in self.normen if n.geltung is BewusstseinsGeltung.GESPERRT)

    @property
    def bewusst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bewusstseins_senat_id for n in self.normen if n.geltung is BewusstseinsGeltung.BEWUSST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bewusstseins_senat_id for n in self.normen if n.geltung is BewusstseinsGeltung.GRUNDLEGEND_BEWUSST)

    @property
    def senat_signal(self):
        if any(n.geltung is BewusstseinsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is BewusstseinsGeltung.BEWUSST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-bewusst")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-bewusst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_bewusstseins_senat(
    sprachverarbeitungs_manifest: SprachverarbeitungsManifest | None = None,
    *,
    senat_id: str = "bewusstseins-senat",
) -> BewusstseinsSenat:
    if sprachverarbeitungs_manifest is None:
        sprachverarbeitungs_manifest = build_sprachverarbeitungs_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[BewusstseinsNorm] = []
    for parent_norm in sprachverarbeitungs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.sprachverarbeitungs_manifest_id.removeprefix(f'{sprachverarbeitungs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.sprachverarbeitungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.sprachverarbeitungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BewusstseinsGeltung.GRUNDLEGEND_BEWUSST)
        normen.append(
            BewusstseinsNorm(
                bewusstseins_senat_id=new_id,
                bewusstseins_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                bewusstseins_weight=new_weight,
                bewusstseins_tier=new_tier,
                canonical=is_canonical,
                bewusstseins_ids=parent_norm.sprachverarbeitungs_ids + (new_id,),
                bewusstseins_tags=parent_norm.sprachverarbeitungs_tags + (f"bewusstsein:{new_geltung.value}",),
            )
        )
    return BewusstseinsSenat(
        senat_id=senat_id,
        sprachverarbeitungs_manifest=sprachverarbeitungs_manifest,
        normen=tuple(normen),
    )
