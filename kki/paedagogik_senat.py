"""
#587 PaedagogikSenat — Montessori/Freinet/Makarenko Pädagogik Senat

Maria Montessori (1909): Il Metodo della Pedagogia Scientifica — Selbsttätigkeit als
  Bildungsprinzip; vorbereitete Umgebung als pädagogisches Konzept; sensitive Phasen als
  Entwicklungsfenster; Freiheit im Rahmen als pädagogische Grundhaltung; Beobachtung
  als Aufgabe der Lehrperson im Peta-Schwarm Leitstern.
Célestin Freinet (1925): Moderne Schule — Kooperatives Lernen als Unterrichtsform;
  Druckerei als Werkzeug der Selbstäußerung; Klassenrat als demokratische Institution;
  Natürliche Methode als didaktisches Konzept; Korrespondenz als Lernmedium im
  Peta-Schwarm Leitstern.
Anton Makarenko (1933): Der Weg ins Leben — Kollektive Erziehung als pädagogisches
  Modell; produktive Arbeit als Bildungsmittel; Selbstverwaltung als Erziehungsprinzip;
  Kollektiv als Erziehungssubjekt; Disziplin als Freiheitsvoraussetzung im
  Peta-Schwarm Leitstern. 🏛️📐
Parent: BildungsinstitutionPakt (#586)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bildungsinstitution_pakt import (
    BildungsinstitutionPakt,
    BildungsinstitutionPaktGeltung,
    build_bildungsinstitution_pakt,
)

_WEIGHT_DELTA: dict["PaedagogikSenatGeltung", float] = {}
_TIER_DELTA: dict["PaedagogikSenatGeltung", int] = {}
_TYP_MAP: dict["PaedagogikSenatGeltung", "PaedagogikSenatTyp"] = {}
_PROZEDUR_MAP: dict["PaedagogikSenatGeltung", "PaedagogikSenatProzedur"] = {}
_GELTUNG_MAP: dict[BildungsinstitutionPaktGeltung, "PaedagogikSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PaedagogikSenatGeltung.GESPERRT: 0.0,
        PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH: 0.05,
        PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH: 0.1,
    })
    _TIER_DELTA.update({
        PaedagogikSenatGeltung.GESPERRT: 0,
        PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH: 1,
        PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH: 2,
    })
    _TYP_MAP.update({
        PaedagogikSenatGeltung.GESPERRT: PaedagogikSenatTyp.SCHUTZ_PAEDAGOGIKSENAT,
        PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH: PaedagogikSenatTyp.ORDNUNGS_PAEDAGOGIKSENAT,
        PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH: PaedagogikSenatTyp.SOUVERAENITAETS_PAEDAGOGIKSENAT,
    })
    _PROZEDUR_MAP.update({
        PaedagogikSenatGeltung.GESPERRT: PaedagogikSenatProzedur.NOTPROZEDUR,
        PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH: PaedagogikSenatProzedur.REGELPROTOKOLL,
        PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH: PaedagogikSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        BildungsinstitutionPaktGeltung.GESPERRT: PaedagogikSenatGeltung.GESPERRT,
        BildungsinstitutionPaktGeltung.INSTITUTIONELL_BILDEND: PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH,
        BildungsinstitutionPaktGeltung.GRUNDLEGEND_INSTITUTIONELL_BILDEND: PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH,
    })


class PaedagogikSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    PAEDAGOGISCH_SENATORISCH = "paedagogisch-senatorisch"
    GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH = "grundlegend-paedagogisch-senatorisch"


class PaedagogikSenatTyp(Enum):
    SCHUTZ_PAEDAGOGIKSENAT = "schutz-paedagogiksenat"
    ORDNUNGS_PAEDAGOGIKSENAT = "ordnungs-paedagogiksenat"
    SOUVERAENITAETS_PAEDAGOGIKSENAT = "souveraenitaets-paedagogiksenat"


class PaedagogikSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class PaedagogikSenatNorm:
    paedagogik_senat_id: str
    paedagogik_typ: PaedagogikSenatTyp
    prozedur: PaedagogikSenatProzedur
    geltung: PaedagogikSenatGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PaedagogikSenat:
    senat_id: str
    bildungsinstitution_pakt: BildungsinstitutionPakt
    normen: tuple[PaedagogikSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.paedagogik_senat_id for n in self.normen
            if n.geltung is PaedagogikSenatGeltung.GESPERRT
        )

    @property
    def paedagogisch_senatorisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.paedagogik_senat_id for n in self.normen
            if n.geltung is PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.paedagogik_senat_id for n in self.normen
            if n.geltung is PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH
        )

    @property
    def senat_signal(self):
        if any(n.geltung is PaedagogikSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is PaedagogikSenatGeltung.PAEDAGOGISCH_SENATORISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-paedagogisch-senatorisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-paedagogisch-senatorisch")


_init_map()


def build_paedagogik_senat(
    bildungsinstitution_pakt: BildungsinstitutionPakt | None = None,
    *,
    senat_id: str = "paedagogik-senat",
) -> PaedagogikSenat:
    if bildungsinstitution_pakt is None:
        bildungsinstitution_pakt = build_bildungsinstitution_pakt(
            pakt_id=f"{senat_id}-pakt"
        )

    normen: list[PaedagogikSenatNorm] = []
    for parent_norm in bildungsinstitution_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.bildungsinstitution_pakt_id.removeprefix(f'{bildungsinstitution_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PaedagogikSenatGeltung.GRUNDLEGEND_PAEDAGOGISCH_SENATORISCH)
        normen.append(
            PaedagogikSenatNorm(
                paedagogik_senat_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.paedagogik_ids + (new_id,),
                paedagogik_tags=parent_norm.paedagogik_tags + (f"paedagogik-senat:{new_geltung.value}",),
            )
        )
    return PaedagogikSenat(
        senat_id=senat_id,
        bildungsinstitution_pakt=bildungsinstitution_pakt,
        normen=tuple(normen),
    )
