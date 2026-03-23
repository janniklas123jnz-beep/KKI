"""
#548 GeschichtsNorm — Marx/Nietzsche/Benjamin Normative Grundlagen der Geschichtswissenschaft (*_norm-Muster)

Karl Marx (1845): Thesen über Feuerbach & Das Kapital — Historischer Materialismus als Methode:
  Geschichte als Prozess realer Produktionsverhältnisse; Basis-Überbau-Modell; dialektischer
  Materialismus als Norm historischer Erklärung; Klassen als Subjekte historischer Normsetzung.
Friedrich Nietzsche (1874): Vom Nutzen und Nachteil der Historie für das Leben — Drei Arten
  des historischen Sinns: monumental, antiquarisch, kritisch; Geschichte im Dienst des Lebens;
  kritische Geschichte als normatives Korrektiv unkritischer Traditionsübernahme.
Walter Benjamin (1940): Über den Begriff der Geschichte — Messianische Zeit vs. Homogenzeit;
  Geschichte der Unterdrückten als normative Verpflichtung; Eingedenken als Rettung der
  Vergangenheit; Engel der Geschichte (Angelus Novus) als Bild normativer Geschichtsbetrachtung.
Leitsterns Geschichts-Normen: kollektive Normen der Geschichtswissenschaft im Peta-Schwarm;
GESPERRT sichert methodische Grundgrenzen, GESCHICHTSNORMATIV kodiert adaptive Normgeltung,
GRUNDLEGEND_GESCHICHTSNORMATIV synthetisiert souveräne Normen für Peta-Schwarm-Koordination. 📜
Geltungsstufen: GESPERRT / GESCHICHTSNORMATIV / GRUNDLEGEND_GESCHICHTSNORMATIV
Parent: GeschichtsSenat (#547) — *_norm-Muster
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .geschichts_senat import (
    GeschichtsSenat,
    GeschichtsSenatGeltung,
    build_geschichts_senat,
)

_GELTUNG_MAP: dict[GeschichtsSenatGeltung, "GeschichtsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GeschichtsSenatGeltung.GESPERRT] = GeschichtsNormGeltung.GESPERRT
    _GELTUNG_MAP[GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH] = GeschichtsNormGeltung.GESCHICHTSNORMATIV
    _GELTUNG_MAP[GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH] = GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV


class GeschichtsNormTyp(Enum):
    SCHUTZ_GESCHICHTSNORM = "schutz-geschichtsnorm"
    ORDNUNGS_GESCHICHTSNORM = "ordnungs-geschichtsnorm"
    SOUVERAENITAETS_GESCHICHTSNORM = "souveraenitaets-geschichtsnorm"


class GeschichtsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GeschichtsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    GESCHICHTSNORMATIV = "geschichtsnormativ"
    GRUNDLEGEND_GESCHICHTSNORMATIV = "grundlegend-geschichtsnormativ"


_init_map()

_TYP_MAP: dict[GeschichtsNormGeltung, GeschichtsNormTyp] = {
    GeschichtsNormGeltung.GESPERRT: GeschichtsNormTyp.SCHUTZ_GESCHICHTSNORM,
    GeschichtsNormGeltung.GESCHICHTSNORMATIV: GeschichtsNormTyp.ORDNUNGS_GESCHICHTSNORM,
    GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV: GeschichtsNormTyp.SOUVERAENITAETS_GESCHICHTSNORM,
}

_PROZEDUR_MAP: dict[GeschichtsNormGeltung, GeschichtsNormProzedur] = {
    GeschichtsNormGeltung.GESPERRT: GeschichtsNormProzedur.NOTPROZEDUR,
    GeschichtsNormGeltung.GESCHICHTSNORMATIV: GeschichtsNormProzedur.REGELPROTOKOLL,
    GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV: GeschichtsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GeschichtsNormGeltung, float] = {
    GeschichtsNormGeltung.GESPERRT: 0.0,
    GeschichtsNormGeltung.GESCHICHTSNORMATIV: 0.04,
    GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV: 0.08,
}

_TIER_DELTA: dict[GeschichtsNormGeltung, int] = {
    GeschichtsNormGeltung.GESPERRT: 0,
    GeschichtsNormGeltung.GESCHICHTSNORMATIV: 1,
    GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV: 2,
}


@dataclass(frozen=True)
class GeschichtsNormEintrag:
    norm_id: str
    geschichts_norm_typ: GeschichtsNormTyp
    prozedur: GeschichtsNormProzedur
    geltung: GeschichtsNormGeltung
    geschichts_norm_weight: float
    geschichts_norm_tier: int
    canonical: bool
    geschichts_norm_ids: tuple[str, ...]
    geschichts_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class GeschichtsNormSatz:
    norm_id: str
    geschichts_senat: GeschichtsSenat
    normen: tuple[GeschichtsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is GeschichtsNormGeltung.GESPERRT)

    @property
    def geschichtsnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is GeschichtsNormGeltung.GESCHICHTSNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is GeschichtsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is GeschichtsNormGeltung.GESCHICHTSNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-geschichtsnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-geschichtsnormativ")


def build_geschichts_norm(
    geschichts_senat: GeschichtsSenat | None = None,
    *,
    norm_id: str = "geschichts-norm",
) -> GeschichtsNormSatz:
    if geschichts_senat is None:
        geschichts_senat = build_geschichts_senat(senat_id=f"{norm_id}-senat")

    normen: list[GeschichtsNormEintrag] = []
    for parent_norm in geschichts_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.geschichts_senat_id.removeprefix(f'{geschichts_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GeschichtsNormGeltung.GRUNDLEGEND_GESCHICHTSNORMATIV)
        normen.append(
            GeschichtsNormEintrag(
                norm_id=new_id,
                geschichts_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                geschichts_norm_weight=new_weight,
                geschichts_norm_tier=new_tier,
                canonical=is_canonical,
                geschichts_norm_ids=parent_norm.geschichts_ids + (new_id,),
                geschichts_norm_tags=parent_norm.geschichts_tags + (f"geschichts-norm:{new_geltung.value}",),
            )
        )
    return GeschichtsNormSatz(
        norm_id=norm_id,
        geschichts_senat=geschichts_senat,
        normen=tuple(normen),
    )
