"""
#517 GlobalpolitikSenat — Kant/Morgenthau/Waltz Weltfrieden und internationale Ordnung

Immanuel Kant (1795): Zum ewigen Frieden — Föderalismus freier Staaten als Grundlage des
  Weltfriedens; republikanische Verfassung als Bedingung friedlicher Außenpolitik; Weltbürger-
  recht als dritte Säule des ewigen Friedens; Völkerbund als institutionelles Friedensprojekt;
  teleologische Geschichtsphilosophie: Natur treibt zur rechtlichen Verfassung hin.
Hans J. Morgenthau (1948): Politics Among Nations — Politischer Realismus als Grundparadigma;
  Nationalinteresse definiert in Begriffen von Macht; Machtgleichgewicht als Stabilisator
  internationaler Ordnung; Unterscheidung von Moral und Staatsraison; Souveränität als
  unveräußerliches Prinzip staatlichen Handelns in der Anarchie des internationalen Systems.
Kenneth N. Waltz (1979): Theory of International Politics — Strukturrealismus: Anarchie als
  Systemmerkmal der internationalen Politik; Bipolarität stabiler als Multipolarität;
  Selbsthilfe als zwingender Imperativ im anarchischen System; Systemstruktur bestimmt
  Staatenverhalten unabhängig von innenpolitischen Eigenschaften.
John Rawls (1999): Das Recht der Völker — Liberaler Internationalismus; Volksrecht als
  Erweiterung der Gerechtigkeitstheorie auf Völker; Pflicht zur Unterstützung belasteter
  Gesellschaften; tolerable Hierarchien vs. outlaw states; kosmopolitische vs. völkerrechtliche
  Gerechtigkeit als Grundspannung globaler Ordnungstheorie.
Leitsterns Peta-Schwarm verankert Globalpolitik als universales Koordinationsprinzip: GESPERRT
schützt die unveräußerlichen Grundnormen globalpolitischer Ordnung, GLOBALPOLITISCH ermöglicht
adaptive Weltregierung zwischen Millionen von Agenten, GRUNDLEGEND_GLOBALPOLITISCH synthetisiert
souveräne globalpolitische Handlungsfähigkeit des Peta-Schwarms. 🌐
Parent: LegitimitaetsPakt (#516)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .legitimitaets_pakt import (
    LegitimitaetsPakt,
    LegitimitaetsPaktGeltung,
    build_legitimitaets_pakt,
)

_WEIGHT_DELTA: dict["GlobalpolitikSenatGeltung", float] = {}
_TIER_DELTA: dict["GlobalpolitikSenatGeltung", int] = {}
_TYP_MAP: dict["GlobalpolitikSenatGeltung", "GlobalpolitikSenatTyp"] = {}
_PROZEDUR_MAP: dict["GlobalpolitikSenatGeltung", "GlobalpolitikSenatProzedur"] = {}
_GELTUNG_MAP: dict[LegitimitaetsPaktGeltung, "GlobalpolitikSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GlobalpolitikSenatGeltung.GESPERRT: 0.0,
        GlobalpolitikSenatGeltung.GLOBALPOLITISCH: 0.05,
        GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH: 0.1,
    })
    _TIER_DELTA.update({
        GlobalpolitikSenatGeltung.GESPERRT: 0,
        GlobalpolitikSenatGeltung.GLOBALPOLITISCH: 1,
        GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH: 2,
    })
    _TYP_MAP.update({
        GlobalpolitikSenatGeltung.GESPERRT: GlobalpolitikSenatTyp.SCHUTZ_GLOBALPOLITIK,
        GlobalpolitikSenatGeltung.GLOBALPOLITISCH: GlobalpolitikSenatTyp.ORDNUNGS_GLOBALPOLITIK,
        GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH: GlobalpolitikSenatTyp.SOUVERAENITAETS_GLOBALPOLITIK,
    })
    _PROZEDUR_MAP.update({
        GlobalpolitikSenatGeltung.GESPERRT: GlobalpolitikSenatProzedur.NOTPROZEDUR,
        GlobalpolitikSenatGeltung.GLOBALPOLITISCH: GlobalpolitikSenatProzedur.REGELPROTOKOLL,
        GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH: GlobalpolitikSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        LegitimitaetsPaktGeltung.GESPERRT: GlobalpolitikSenatGeltung.GESPERRT,
        LegitimitaetsPaktGeltung.LEGITIMITAETLICH: GlobalpolitikSenatGeltung.GLOBALPOLITISCH,
        LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH: GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH,
    })


class GlobalpolitikSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    GLOBALPOLITISCH = "globalpolitisch"
    GRUNDLEGEND_GLOBALPOLITISCH = "grundlegend-globalpolitisch"


class GlobalpolitikSenatTyp(Enum):
    SCHUTZ_GLOBALPOLITIK = "schutz-globalpolitik"
    ORDNUNGS_GLOBALPOLITIK = "ordnungs-globalpolitik"
    SOUVERAENITAETS_GLOBALPOLITIK = "souveraenitaets-globalpolitik"


class GlobalpolitikSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class GlobalpolitikSenatNorm:
    globalpolitik_senat_id: str
    globalpolitik_typ: GlobalpolitikSenatTyp
    prozedur: GlobalpolitikSenatProzedur
    geltung: GlobalpolitikSenatGeltung
    globalpolitik_weight: float
    globalpolitik_tier: int
    canonical: bool
    globalpolitik_ids: tuple[str, ...]
    globalpolitik_tags: tuple[str, ...]


@dataclass(frozen=True)
class GlobalpolitikSenat:
    senat_id: str
    legitimitaets_pakt: LegitimitaetsPakt
    normen: tuple[GlobalpolitikSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.globalpolitik_senat_id for n in self.normen if n.geltung is GlobalpolitikSenatGeltung.GESPERRT)

    @property
    def globalpolitisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.globalpolitik_senat_id for n in self.normen if n.geltung is GlobalpolitikSenatGeltung.GLOBALPOLITISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.globalpolitik_senat_id for n in self.normen if n.geltung is GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is GlobalpolitikSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is GlobalpolitikSenatGeltung.GLOBALPOLITISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-globalpolitisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-globalpolitisch")


_init_map()


def build_globalpolitik_senat(
    legitimitaets_pakt: LegitimitaetsPakt | None = None,
    *,
    senat_id: str = "globalpolitik-senat",
) -> GlobalpolitikSenat:
    if legitimitaets_pakt is None:
        legitimitaets_pakt = build_legitimitaets_pakt(
            pakt_id=f"{senat_id}-pakt"
        )

    normen: list[GlobalpolitikSenatNorm] = []
    for parent_norm in legitimitaets_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.legitimitaets_pakt_id.removeprefix(f'{legitimitaets_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.legitimitaets_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.legitimitaets_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH)
        normen.append(
            GlobalpolitikSenatNorm(
                globalpolitik_senat_id=new_id,
                globalpolitik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                globalpolitik_weight=new_weight,
                globalpolitik_tier=new_tier,
                canonical=is_canonical,
                globalpolitik_ids=parent_norm.legitimitaets_ids + (new_id,),
                globalpolitik_tags=parent_norm.legitimitaets_tags + (f"{senat_id}:{new_geltung.value}",),
            )
        )
    return GlobalpolitikSenat(
        senat_id=senat_id,
        legitimitaets_pakt=legitimitaets_pakt,
        normen=tuple(normen),
    )
