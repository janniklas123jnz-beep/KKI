"""
#577 KunstsoziologieSenat — Bourdieu/Hauser/Heinich Kunstwissenschaft Soziologie

Pierre Bourdieu (1979): La Distinction — kulturelles Kapital als ästhetisches
  Urteil; Habitus als inkorporiertes soziales Erbe; Kunstfeld als Arena des
  symbolischen Kampfes; Geschmack als Klassifikationsmerkmal sozialer Positionen im
  Peta-Schwarm Leitstern.
Arnold Hauser (1951): Sozialgeschichte der Kunst und Literatur — Kunstwerke als
  Produkte sozialer Verhältnisse; Mäzenatentum und Markt als Produktionsbedingungen;
  Periodisierung nach gesellschaftlichen Epochen; Kunst als Spiegel sozialer
  Strukturen im Peta-Schwarm Leitstern.
Nathalie Heinich (2014): Le paradigme de l'art contemporain — Soziologie des
  Kunstfeldes als normativer Rahmen; Transgression als konstitutives Prinzip der
  Gegenwartskunst; Wertregime als analytische Kategorie; empirische Kunstsoziologie
  jenseits der Kritik im Peta-Schwarm Leitstern. 🏛️🤝
Parent: IkonographiePakt (#576)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ikonographie_pakt import (
    IkonographiePakt,
    IkonographiePaktGeltung,
    build_ikonographie_pakt,
)

_WEIGHT_DELTA: dict["KunstsoziologieSenatGeltung", float] = {}
_TIER_DELTA: dict["KunstsoziologieSenatGeltung", int] = {}
_TYP_MAP: dict["KunstsoziologieSenatGeltung", "KunstsoziologieSenatTyp"] = {}
_PROZEDUR_MAP: dict["KunstsoziologieSenatGeltung", "KunstsoziologieSenatProzedur"] = {}
_GELTUNG_MAP: dict[IkonographiePaktGeltung, "KunstsoziologieSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KunstsoziologieSenatGeltung.GESPERRT: 0.0,
        KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH: 0.05,
        KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        KunstsoziologieSenatGeltung.GESPERRT: 0,
        KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH: 1,
        KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        KunstsoziologieSenatGeltung.GESPERRT: KunstsoziologieSenatTyp.SCHUTZ_KUNSTSOZIOLOGIE,
        KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH: KunstsoziologieSenatTyp.ORDNUNGS_KUNSTSOZIOLOGIE,
        KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH: KunstsoziologieSenatTyp.SOUVERAENITAETS_KUNSTSOZIOLOGIE,
    })
    _PROZEDUR_MAP.update({
        KunstsoziologieSenatGeltung.GESPERRT: KunstsoziologieSenatProzedur.NOTPROZEDUR,
        KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH: KunstsoziologieSenatProzedur.REGELPROTOKOLL,
        KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH: KunstsoziologieSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        IkonographiePaktGeltung.GESPERRT: KunstsoziologieSenatGeltung.GESPERRT,
        IkonographiePaktGeltung.IKONOGRAPHISCH: KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH,
        IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH: KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH,
    })


class KunstsoziologieSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    KUNSTSOZIOLOGISCH = "kunstsoziologisch"
    GRUNDLEGEND_KUNSTSOZIOLOGISCH = "grundlegend-kunstsoziologisch"


class KunstsoziologieSenatTyp(Enum):
    SCHUTZ_KUNSTSOZIOLOGIE = "schutz-kunstsoziologie"
    ORDNUNGS_KUNSTSOZIOLOGIE = "ordnungs-kunstsoziologie"
    SOUVERAENITAETS_KUNSTSOZIOLOGIE = "souveraenitaets-kunstsoziologie"


class KunstsoziologieSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KunstsoziologieSenatNorm:
    kunstsoziologie_senat_id: str
    kunst_typ: KunstsoziologieSenatTyp
    prozedur: KunstsoziologieSenatProzedur
    geltung: KunstsoziologieSenatGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class KunstsoziologieSenat:
    senat_id: str
    ikonographie_pakt: IkonographiePakt
    normen: tuple[KunstsoziologieSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunstsoziologie_senat_id for n in self.normen if n.geltung is KunstsoziologieSenatGeltung.GESPERRT)

    @property
    def kunstsoziologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunstsoziologie_senat_id for n in self.normen if n.geltung is KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunstsoziologie_senat_id for n in self.normen if n.geltung is KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is KunstsoziologieSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is KunstsoziologieSenatGeltung.KUNSTSOZIOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-kunstsoziologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-kunstsoziologisch")


_init_map()


def build_kunstsoziologie_senat(
    ikonographie_pakt: IkonographiePakt | None = None,
    *,
    senat_id: str = "kunstsoziologie-senat",
) -> KunstsoziologieSenat:
    if ikonographie_pakt is None:
        ikonographie_pakt = build_ikonographie_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[KunstsoziologieSenatNorm] = []
    for parent_norm in ikonographie_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.ikonographie_pakt_id.removeprefix(f'{ikonographie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KunstsoziologieSenatGeltung.GRUNDLEGEND_KUNSTSOZIOLOGISCH)
        normen.append(
            KunstsoziologieSenatNorm(
                kunstsoziologie_senat_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"kunstsoziologie-senat:{new_geltung.value}",),
            )
        )
    return KunstsoziologieSenat(
        senat_id=senat_id,
        ikonographie_pakt=ikonographie_pakt,
        normen=tuple(normen),
    )
