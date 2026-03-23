"""
#575 KunstgeschichteManifest — Warburg/Gombrich/Belting Kunstwissenschaft Geschichte

Aby Warburg (1920): Mnemosyne-Atlas — Pathosformel als Bildgedächtnis; Nachleben
  der Antike als kulturelles Gedächtnis; Bilderatlas als Methode der Kunstwissenschaft;
  emotionale Formeln als Träger kollektiven Ausdrucks; Ikonologie als
  kulturwissenschaftliche Methode im Peta-Schwarm Leitstern.
Ernst Gombrich (1950): The Story of Art — Kunstgeschichte als Geschichte von
  Problemen und Lösungen; Schema und Korrektur als Lernprozess des Sehens;
  Popularisierung als wissenschaftliche Leistung; Bild als kognitives Werkzeug im
  Peta-Schwarm Leitstern.
Hans Belting (1983): Das Ende der Kunstgeschichte — Bild-Anthropologie als neue
  Kunstwissenschaft; Unterscheidung von Bild, Medium und Körper; das Bild jenseits
  der Kunst; Kunstgeschichte nach dem Ende ihrer Leiterzählung im
  Peta-Schwarm Leitstern. 📜🎨
Parent: StilkritikKodex (#574)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .stilkritik_kodex import (
    StilkritikKodex,
    StilkritikKodexGeltung,
    build_stilkritik_kodex,
)

_WEIGHT_DELTA: dict["KunstgeschichteManifestGeltung", float] = {}
_TIER_DELTA: dict["KunstgeschichteManifestGeltung", int] = {}
_TYP_MAP: dict["KunstgeschichteManifestGeltung", "KunstgeschichteManifestTyp"] = {}
_PROZEDUR_MAP: dict["KunstgeschichteManifestGeltung", "KunstgeschichteManifestProzedur"] = {}
_GELTUNG_MAP: dict[StilkritikKodexGeltung, "KunstgeschichteManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KunstgeschichteManifestGeltung.GESPERRT: 0.0,
        KunstgeschichteManifestGeltung.KUNSTHISTORISCH: 0.05,
        KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH: 0.1,
    })
    _TIER_DELTA.update({
        KunstgeschichteManifestGeltung.GESPERRT: 0,
        KunstgeschichteManifestGeltung.KUNSTHISTORISCH: 1,
        KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH: 2,
    })
    _TYP_MAP.update({
        KunstgeschichteManifestGeltung.GESPERRT: KunstgeschichteManifestTyp.SCHUTZ_KUNSTGESCHICHTE,
        KunstgeschichteManifestGeltung.KUNSTHISTORISCH: KunstgeschichteManifestTyp.ORDNUNGS_KUNSTGESCHICHTE,
        KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH: KunstgeschichteManifestTyp.SOUVERAENITAETS_KUNSTGESCHICHTE,
    })
    _PROZEDUR_MAP.update({
        KunstgeschichteManifestGeltung.GESPERRT: KunstgeschichteManifestProzedur.NOTPROZEDUR,
        KunstgeschichteManifestGeltung.KUNSTHISTORISCH: KunstgeschichteManifestProzedur.REGELPROTOKOLL,
        KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH: KunstgeschichteManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        StilkritikKodexGeltung.GESPERRT: KunstgeschichteManifestGeltung.GESPERRT,
        StilkritikKodexGeltung.STILKRITISCH: KunstgeschichteManifestGeltung.KUNSTHISTORISCH,
        StilkritikKodexGeltung.GRUNDLEGEND_STILKRITISCH: KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH,
    })


class KunstgeschichteManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    KUNSTHISTORISCH = "kunsthistorisch"
    GRUNDLEGEND_KUNSTHISTORISCH = "grundlegend-kunsthistorisch"


class KunstgeschichteManifestTyp(Enum):
    SCHUTZ_KUNSTGESCHICHTE = "schutz-kunstgeschichte"
    ORDNUNGS_KUNSTGESCHICHTE = "ordnungs-kunstgeschichte"
    SOUVERAENITAETS_KUNSTGESCHICHTE = "souveraenitaets-kunstgeschichte"


class KunstgeschichteManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KunstgeschichteManifestNorm:
    kunstgeschichte_manifest_id: str
    kunst_typ: KunstgeschichteManifestTyp
    prozedur: KunstgeschichteManifestProzedur
    geltung: KunstgeschichteManifestGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class KunstgeschichteManifest:
    manifest_id: str
    stilkritik_kodex: StilkritikKodex
    normen: tuple[KunstgeschichteManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunstgeschichte_manifest_id for n in self.normen if n.geltung is KunstgeschichteManifestGeltung.GESPERRT)

    @property
    def kunsthistorisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunstgeschichte_manifest_id for n in self.normen if n.geltung is KunstgeschichteManifestGeltung.KUNSTHISTORISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunstgeschichte_manifest_id for n in self.normen if n.geltung is KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is KunstgeschichteManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is KunstgeschichteManifestGeltung.KUNSTHISTORISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-kunsthistorisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-kunsthistorisch")


_init_map()


def build_kunstgeschichte_manifest(
    stilkritik_kodex: StilkritikKodex | None = None,
    *,
    manifest_id: str = "kunstgeschichte-manifest",
) -> KunstgeschichteManifest:
    if stilkritik_kodex is None:
        stilkritik_kodex = build_stilkritik_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[KunstgeschichteManifestNorm] = []
    for parent_norm in stilkritik_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.stilkritik_kodex_id.removeprefix(f'{stilkritik_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KunstgeschichteManifestGeltung.GRUNDLEGEND_KUNSTHISTORISCH)
        normen.append(
            KunstgeschichteManifestNorm(
                kunstgeschichte_manifest_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.kunst_ids + (new_id,),
                kunst_tags=parent_norm.kunst_tags + (f"kunstgeschichte-manifest:{new_geltung.value}",),
            )
        )
    return KunstgeschichteManifest(
        manifest_id=manifest_id,
        stilkritik_kodex=stilkritik_kodex,
        normen=tuple(normen),
    )
