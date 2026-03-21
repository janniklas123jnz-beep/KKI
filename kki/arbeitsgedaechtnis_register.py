"""
#392 ArbeitsgedaechtnisRegister — Baddeley & Hitch (1974): das Arbeitsgedächtnis
besteht aus phonologischer Schleife (verbale Infos), visuell-räumlichem Notizblock
(räumliche Infos), episodischem Puffer (Episoden-Bindung) und zentraler Exekutive
(Kontrolle). Millers Gesetz (1956): 7 ± 2 Einheiten gleichzeitig aktiv — die
fundamentale Kapazitätsgrenze jedes kognitiven Systems.
Cowan (2001) revidiert auf 4 Chunks. Working Memory = Interface zwischen
Langzeitgedächtnis und Aufmerksamkeit: aktive Aufrechterhaltung relevanter Info.
Leitsterns Agenten priorisieren maximal 7±2 Normen gleichzeitig — selektive
Governance unter Ressourcenknappheit.
Geltungsstufen: GESPERRT / ARBEITSGEDAECHTNISAKTIV / GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV
Parent: KognitionsFeld (#391)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kognitions_feld import (
    KognitionsFeld,
    KognitionsGeltung,
    build_kognitions_feld,
)

_GELTUNG_MAP: dict[KognitionsGeltung, "ArbeitsgedaechtnisGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KognitionsGeltung.GESPERRT] = ArbeitsgedaechtnisGeltung.GESPERRT
    _GELTUNG_MAP[KognitionsGeltung.KOGNITIV] = ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV
    _GELTUNG_MAP[KognitionsGeltung.GRUNDLEGEND_KOGNITIV] = ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV


class ArbeitsgedaechtnisTyp(Enum):
    SCHUTZ_ARBEITSGEDAECHTNIS = "schutz-arbeitsgedaechtnis"
    ORDNUNGS_ARBEITSGEDAECHTNIS = "ordnungs-arbeitsgedaechtnis"
    SOUVERAENITAETS_ARBEITSGEDAECHTNIS = "souveraenitaets-arbeitsgedaechtnis"


class ArbeitsgedaechtnispProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ArbeitsgedaechtnisGeltung(Enum):
    GESPERRT = "gesperrt"
    ARBEITSGEDAECHTNISAKTIV = "arbeitsgedaechtnisaktiv"
    GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV = "grundlegend-arbeitsgedaechtnisaktiv"


_init_map()

_TYP_MAP: dict[ArbeitsgedaechtnisGeltung, ArbeitsgedaechtnisTyp] = {
    ArbeitsgedaechtnisGeltung.GESPERRT: ArbeitsgedaechtnisTyp.SCHUTZ_ARBEITSGEDAECHTNIS,
    ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV: ArbeitsgedaechtnisTyp.ORDNUNGS_ARBEITSGEDAECHTNIS,
    ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV: ArbeitsgedaechtnisTyp.SOUVERAENITAETS_ARBEITSGEDAECHTNIS,
}

_PROZEDUR_MAP: dict[ArbeitsgedaechtnisGeltung, ArbeitsgedaechtnispProzedur] = {
    ArbeitsgedaechtnisGeltung.GESPERRT: ArbeitsgedaechtnispProzedur.NOTPROZEDUR,
    ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV: ArbeitsgedaechtnispProzedur.REGELPROTOKOLL,
    ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV: ArbeitsgedaechtnispProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ArbeitsgedaechtnisGeltung, float] = {
    ArbeitsgedaechtnisGeltung.GESPERRT: 0.0,
    ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV: 0.04,
    ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV: 0.08,
}

_TIER_DELTA: dict[ArbeitsgedaechtnisGeltung, int] = {
    ArbeitsgedaechtnisGeltung.GESPERRT: 0,
    ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV: 1,
    ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArbeitsgedaechtnisNorm:
    arbeitsgedaechtnis_register_id: str
    arbeitsgedaechtnis_typ: ArbeitsgedaechtnisTyp
    prozedur: ArbeitsgedaechtnispProzedur
    geltung: ArbeitsgedaechtnisGeltung
    arbeitsgedaechtnis_weight: float
    arbeitsgedaechtnis_tier: int
    canonical: bool
    arbeitsgedaechtnis_ids: tuple[str, ...]
    arbeitsgedaechtnis_tags: tuple[str, ...]


@dataclass(frozen=True)
class ArbeitsgedaechtnisRegister:
    register_id: str
    kognitions_feld: KognitionsFeld
    normen: tuple[ArbeitsgedaechtnisNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.arbeitsgedaechtnis_register_id for n in self.normen if n.geltung is ArbeitsgedaechtnisGeltung.GESPERRT)

    @property
    def arbeitsgedaechtnisaktiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.arbeitsgedaechtnis_register_id for n in self.normen if n.geltung is ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.arbeitsgedaechtnis_register_id for n in self.normen if n.geltung is ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV)

    @property
    def register_signal(self):
        if any(n.geltung is ArbeitsgedaechtnisGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is ArbeitsgedaechtnisGeltung.ARBEITSGEDAECHTNISAKTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-arbeitsgedaechtnisaktiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-arbeitsgedaechtnisaktiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_arbeitsgedaechtnis_register(
    kognitions_feld: KognitionsFeld | None = None,
    *,
    register_id: str = "arbeitsgedaechtnis-register",
) -> ArbeitsgedaechtnisRegister:
    if kognitions_feld is None:
        kognitions_feld = build_kognitions_feld(feld_id=f"{register_id}-feld")

    normen: list[ArbeitsgedaechtnisNorm] = []
    for parent_norm in kognitions_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.kognitions_feld_id.removeprefix(f'{kognitions_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.kognitions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kognitions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ArbeitsgedaechtnisGeltung.GRUNDLEGEND_ARBEITSGEDAECHTNISAKTIV)
        normen.append(
            ArbeitsgedaechtnisNorm(
                arbeitsgedaechtnis_register_id=new_id,
                arbeitsgedaechtnis_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                arbeitsgedaechtnis_weight=new_weight,
                arbeitsgedaechtnis_tier=new_tier,
                canonical=is_canonical,
                arbeitsgedaechtnis_ids=parent_norm.kognitions_ids + (new_id,),
                arbeitsgedaechtnis_tags=parent_norm.kognitions_tags + (f"arbeitsgedaechtnis:{new_geltung.value}",),
            )
        )
    return ArbeitsgedaechtnisRegister(
        register_id=register_id,
        kognitions_feld=kognitions_feld,
        normen=tuple(normen),
    )
