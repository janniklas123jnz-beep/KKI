"""
#395 GedaechtnisKonsolidierungsPakt — Squire (1992): Gedächtnistaxonomie.
Deklarativ: episodisch (Tulving — autobiografisch, zeitlich kontextualisiert) +
semantisch (Fakten, Konzepte). Prozedural: Fertigkeiten, Priming, Konditionierung.
Hippocampale Konsolidierung: Transfer Kurz→Langzeit durch Schlaf-Replay (Wilson &
McNaughton 1994). System-Konsolidierung über Jahre (Squire & Alvarez 1995).
Engram-Theorie (Josselyn & Frankland 2015): Gedächtnisspur als physikalisches
Substrat veränderbarer Synapsen. LTP (Hebb 1949, Bliss & Lømo 1973): Long-Term
Potentiation als zelluläres Gedächtnissubstrat. Leitsterns Governance-Normen
konsolidieren durch Wiederholung: episodische Ereignisse werden semantische Regeln.
Geltungsstufen: GESPERRT / KONSOLIDIERT / GRUNDLEGEND_KONSOLIDIERT
Parent: EntscheidungsKodex (#394)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entscheidungs_kodex import (
    EntscheidungsGeltung,
    EntscheidungsKodex,
    build_entscheidungs_kodex,
)

_GELTUNG_MAP: dict[EntscheidungsGeltung, "GedaechtnisKonsolidierungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EntscheidungsGeltung.GESPERRT] = GedaechtnisKonsolidierungsGeltung.GESPERRT
    _GELTUNG_MAP[EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV] = GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT
    _GELTUNG_MAP[EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV] = GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT


class GedaechtnisKonsolidierungsTyp(Enum):
    SCHUTZ_GEDAECHTNIS_KONSOLIDIERUNG = "schutz-gedaechtnis-konsolidierung"
    ORDNUNGS_GEDAECHTNIS_KONSOLIDIERUNG = "ordnungs-gedaechtnis-konsolidierung"
    SOUVERAENITAETS_GEDAECHTNIS_KONSOLIDIERUNG = "souveraenitaets-gedaechtnis-konsolidierung"


class GedaechtnisKonsolidierungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GedaechtnisKonsolidierungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KONSOLIDIERT = "konsolidiert"
    GRUNDLEGEND_KONSOLIDIERT = "grundlegend-konsolidiert"


_init_map()

_TYP_MAP: dict[GedaechtnisKonsolidierungsGeltung, GedaechtnisKonsolidierungsTyp] = {
    GedaechtnisKonsolidierungsGeltung.GESPERRT: GedaechtnisKonsolidierungsTyp.SCHUTZ_GEDAECHTNIS_KONSOLIDIERUNG,
    GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT: GedaechtnisKonsolidierungsTyp.ORDNUNGS_GEDAECHTNIS_KONSOLIDIERUNG,
    GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT: GedaechtnisKonsolidierungsTyp.SOUVERAENITAETS_GEDAECHTNIS_KONSOLIDIERUNG,
}

_PROZEDUR_MAP: dict[GedaechtnisKonsolidierungsGeltung, GedaechtnisKonsolidierungsProzedur] = {
    GedaechtnisKonsolidierungsGeltung.GESPERRT: GedaechtnisKonsolidierungsProzedur.NOTPROZEDUR,
    GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT: GedaechtnisKonsolidierungsProzedur.REGELPROTOKOLL,
    GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT: GedaechtnisKonsolidierungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GedaechtnisKonsolidierungsGeltung, float] = {
    GedaechtnisKonsolidierungsGeltung.GESPERRT: 0.0,
    GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT: 0.04,
    GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT: 0.08,
}

_TIER_DELTA: dict[GedaechtnisKonsolidierungsGeltung, int] = {
    GedaechtnisKonsolidierungsGeltung.GESPERRT: 0,
    GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT: 1,
    GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GedaechtnisKonsolidierungsNorm:
    gedaechtnis_konsolidierungs_pakt_id: str
    gedaechtnis_konsolidierungs_typ: GedaechtnisKonsolidierungsTyp
    prozedur: GedaechtnisKonsolidierungsProzedur
    geltung: GedaechtnisKonsolidierungsGeltung
    gedaechtnis_konsolidierungs_weight: float
    gedaechtnis_konsolidierungs_tier: int
    canonical: bool
    gedaechtnis_konsolidierungs_ids: tuple[str, ...]
    gedaechtnis_konsolidierungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class GedaechtnisKonsolidierungsPakt:
    pakt_id: str
    entscheidungs_kodex: EntscheidungsKodex
    normen: tuple[GedaechtnisKonsolidierungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_konsolidierungs_pakt_id for n in self.normen if n.geltung is GedaechtnisKonsolidierungsGeltung.GESPERRT)

    @property
    def konsolidiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_konsolidierungs_pakt_id for n in self.normen if n.geltung is GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_konsolidierungs_pakt_id for n in self.normen if n.geltung is GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT)

    @property
    def pakt_signal(self):
        if any(n.geltung is GedaechtnisKonsolidierungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is GedaechtnisKonsolidierungsGeltung.KONSOLIDIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-konsolidiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-konsolidiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_gedaechtnis_konsolidierungs_pakt(
    entscheidungs_kodex: EntscheidungsKodex | None = None,
    *,
    pakt_id: str = "gedaechtnis-konsolidierungs-pakt",
) -> GedaechtnisKonsolidierungsPakt:
    if entscheidungs_kodex is None:
        entscheidungs_kodex = build_entscheidungs_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[GedaechtnisKonsolidierungsNorm] = []
    for parent_norm in entscheidungs_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.entscheidungs_kodex_id.removeprefix(f'{entscheidungs_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.entscheidungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.entscheidungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GedaechtnisKonsolidierungsGeltung.GRUNDLEGEND_KONSOLIDIERT)
        normen.append(
            GedaechtnisKonsolidierungsNorm(
                gedaechtnis_konsolidierungs_pakt_id=new_id,
                gedaechtnis_konsolidierungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gedaechtnis_konsolidierungs_weight=new_weight,
                gedaechtnis_konsolidierungs_tier=new_tier,
                canonical=is_canonical,
                gedaechtnis_konsolidierungs_ids=parent_norm.entscheidungs_ids + (new_id,),
                gedaechtnis_konsolidierungs_tags=parent_norm.entscheidungs_tags + (f"gedaechtnis-konsolidierung:{new_geltung.value}",),
            )
        )
    return GedaechtnisKonsolidierungsPakt(
        pakt_id=pakt_id,
        entscheidungs_kodex=entscheidungs_kodex,
        normen=tuple(normen),
    )
