"""
#576 IkonographiePakt — Panofsky/Barthes/Eco Kunstwissenschaft Ikonographie

Erwin Panofsky (1955): Meaning in the Visual Arts — drei Ebenen ikonologischer
  Analyse als vollständiges Interpretationsmodell; vorikonographische Beschreibung,
  ikonographische Analyse und ikonologische Interpretation; Kunstwille als
  Symptom kultureller Werte im Peta-Schwarm Leitstern.
Roland Barthes (1964): Rhétorique de l'image — denotative und konnotative Ebenen
  des Bildes; Ankerung als textuelle Funktion gegenüber Bildbotschaft; das Punctum
  als persönlicher Affektpunkt; Mythologie als ideologische Bedeutungsschicht im
  Peta-Schwarm Leitstern.
Umberto Eco (1962): Opera Aperta — das offene Kunstwerk als semiotisches Projekt;
  Mehrdeutigkeit als ästhetisches Prinzip; Leser als Ko-Produzent von Bedeutung;
  strukturelle Offenheit als Merkmal moderner Kunst im Peta-Schwarm Leitstern. 👁️🔑
Parent: KunstgeschichteManifest (#575)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kunstgeschichte_manifest import (
    KunstgeschichteManifest,
    KunstgeschichteManifestGeltung,
    build_kunstgeschichte_manifest,
)

_WEIGHT_DELTA: dict["IkonographiePaktGeltung", float] = {}
_TIER_DELTA: dict["IkonographiePaktGeltung", int] = {}
_TYP_MAP: dict["IkonographiePaktGeltung", "IkonographiePaktTyp"] = {}
_PROZEDUR_MAP: dict["IkonographiePaktGeltung", "IkonographiePaktProzedur"] = {}
_GELTUNG_MAP: dict[KunstgeschichteManifestGeltung, "IkonographiePaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        IkonographiePaktGeltung.GESPERRT: 0.0,
        IkonographiePaktGeltung.IKONOGRAPHISCH: 0.05,
        IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        IkonographiePaktGeltung.GESPERRT: 0,
        IkonographiePaktGeltung.IKONOGRAPHISCH: 1,
        IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH: 2,
    })
    _TYP_MAP.update({
        IkonographiePaktGeltung.GESPERRT: IkonographiePaktTyp.SCHUTZ_IKONOGRAPHIE,
        IkonographiePaktGeltung.IKONOGRAPHISCH: IkonographiePaktTyp.ORDNUNGS_IKONOGRAPHIE,
        IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH: IkonographiePaktTyp.SOUVERAENITAETS_IKONOGRAPHIE,
    })
    _PROZEDUR_MAP.update({
        IkonographiePaktGeltung.GESPERRT: IkonographiePaktProzedur.NOTPROZEDUR,
        IkonographiePaktGeltung.IKONOGRAPHISCH: IkonographiePaktProzedur.REGELPROTOKOLL,
        IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH: IkonographiePaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KunstgeschichteManifestGeltung.GESPERRT: IkonographiePaktGeltung.GESPERRT,
        KunstgeschichteManifestGeltung.KUNSTHISTORISCH: IkonographiePaktGeltung.IKONOGRAPHISCH,
        KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH: IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH,
    })


class IkonographiePaktGeltung(Enum):
    GESPERRT = "gesperrt"
    IKONOGRAPHISCH = "ikonographisch"
    GRUNDLEGEND_IKONOGRAPHISCH = "grundlegend-ikonographisch"


class IkonographiePaktTyp(Enum):
    SCHUTZ_IKONOGRAPHIE = "schutz-ikonographie"
    ORDNUNGS_IKONOGRAPHIE = "ordnungs-ikonographie"
    SOUVERAENITAETS_IKONOGRAPHIE = "souveraenitaets-ikonographie"


class IkonographiePaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class IkonographiePaktNorm:
    ikonographie_pakt_id: str
    kunst_typ: IkonographiePaktTyp
    prozedur: IkonographiePaktProzedur
    geltung: IkonographiePaktGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class IkonographiePakt:
    pakt_id: str
    kunstgeschichte_manifest: KunstgeschichteManifest
    normen: tuple[IkonographiePaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ikonographie_pakt_id for n in self.normen if n.geltung is IkonographiePaktGeltung.GESPERRT)

    @property
    def ikonographisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ikonographie_pakt_id for n in self.normen if n.geltung is IkonographiePaktGeltung.IKONOGRAPHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ikonographie_pakt_id for n in self.normen if n.geltung is IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is IkonographiePaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is IkonographiePaktGeltung.IKONOGRAPHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-ikonographisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-ikonographisch")


_init_map()


def build_ikonographie_pakt(
    kunstgeschichte_manifest: KunstgeschichteManifest | None = None,
    *,
    pakt_id: str = "ikonographie-pakt",
) -> IkonographiePakt:
    if kunstgeschichte_manifest is None:
        kunstgeschichte_manifest = build_kunstgeschichte_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[IkonographiePaktNorm] = []
    for parent_norm in kunstgeschichte_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.kunstgeschichte_manifest_id.removeprefix(f'{kunstgeschichte_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is IkonographiePaktGeltung.GRUNDLEGEND_IKONOGRAPHISCH)
        normen.append(
            IkonographiePaktNorm(
                ikonographie_pakt_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"ikonographie-pakt:{new_geltung.value}",),
            )
        )
    return IkonographiePakt(
        pakt_id=pakt_id,
        kunstgeschichte_manifest=kunstgeschichte_manifest,
        normen=tuple(normen),
    )
