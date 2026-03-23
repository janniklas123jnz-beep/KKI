"""
#547 GeschichtsSenat — Senat der Geschichtswissenschaft (Syntheseinstanz)

Wilhelm Dilthey (1883): Einleitung in die Geisteswissenschaften — Verstehen vs. Erklären;
  Geisteswissenschaften als eigenständige Erkenntnisform gegenüber den Naturwissenschaften;
  Hermeneutischer Zirkel als methodisches Grundprinzip geschichtswissenschaftlicher Erkenntnis.
Hans-Georg Gadamer (1960): Wahrheit und Methode — Hermeneutik als universale Sinnerschließung;
  Horizontverschmelzung als Modell des Verstehens historischer Texte und Überlieferungen;
  Wirkungsgeschichte als konstitutive Dimension jeder Begegnung mit historischer Überlieferung.
Paul Ricoeur (1983–1985): Temps et récit — narrative Identität und Geschichtstheorie;
  Narrative Struktur als vermittelndes Medium zwischen gelebter und erzählter Zeit;
  Mimesis als dreifacher Prozess der Vor-, Um- und Nachgestaltung historischer Erfahrung.
Parent: ZeitgeschichtsPakt (#546)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zeitgeschichts_pakt import (
    ZeitgeschichtsPakt,
    ZeitgeschichtsPaktGeltung,
    build_zeitgeschichts_pakt,
)

_WEIGHT_DELTA: dict["GeschichtsSenatGeltung", float] = {}
_TIER_DELTA: dict["GeschichtsSenatGeltung", int] = {}
_TYP_MAP: dict["GeschichtsSenatGeltung", "GeschichtsSenatTyp"] = {}
_PROZEDUR_MAP: dict["GeschichtsSenatGeltung", "GeschichtsSenatProzedur"] = {}
_GELTUNG_MAP: dict[ZeitgeschichtsPaktGeltung, "GeschichtsSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GeschichtsSenatGeltung.GESPERRT: 0.0,
        GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH: 0.05,
        GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        GeschichtsSenatGeltung.GESPERRT: 0,
        GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH: 1,
        GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        GeschichtsSenatGeltung.GESPERRT: GeschichtsSenatTyp.SCHUTZ_GESCHICHTSSENAT,
        GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH: GeschichtsSenatTyp.ORDNUNGS_GESCHICHTSSENAT,
        GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH: GeschichtsSenatTyp.SOUVERAENITAETS_GESCHICHTSSENAT,
    })
    _PROZEDUR_MAP.update({
        GeschichtsSenatGeltung.GESPERRT: GeschichtsSenatProzedur.NOTPROZEDUR,
        GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH: GeschichtsSenatProzedur.REGELPROTOKOLL,
        GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH: GeschichtsSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        ZeitgeschichtsPaktGeltung.GESPERRT: GeschichtsSenatGeltung.GESPERRT,
        ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH: GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH,
        ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH: GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH,
    })


class GeschichtsSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    GESCHICHTSWISSENSCHAFTLICH = "geschichtswissenschaftlich"
    GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH = "grundlegend-geschichtswissenschaftlich"


class GeschichtsSenatTyp(Enum):
    SCHUTZ_GESCHICHTSSENAT = "schutz-geschichtssenat"
    ORDNUNGS_GESCHICHTSSENAT = "ordnungs-geschichtssenat"
    SOUVERAENITAETS_GESCHICHTSSENAT = "souveraenitaets-geschichtssenat"


class GeschichtsSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class GeschichtsSenatNorm:
    geschichts_senat_id: str
    geschichts_typ: GeschichtsSenatTyp
    prozedur: GeschichtsSenatProzedur
    geltung: GeschichtsSenatGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class GeschichtsSenat:
    senat_id: str
    zeitgeschichts_pakt: ZeitgeschichtsPakt
    normen: tuple[GeschichtsSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.geschichts_senat_id for n in self.normen
            if n.geltung is GeschichtsSenatGeltung.GESPERRT
        )

    @property
    def geschichtswissenschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.geschichts_senat_id for n in self.normen
            if n.geltung is GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.geschichts_senat_id for n in self.normen
            if n.geltung is GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH
        )

    @property
    def senat_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is GeschichtsSenatGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is GeschichtsSenatGeltung.GESCHICHTSWISSENSCHAFTLICH for n in self.normen):
            return SimpleNamespace(status="senat-geschichtswissenschaftlich")
        return SimpleNamespace(status="senat-grundlegend-geschichtswissenschaftlich")


_init_map()


def build_geschichts_senat(
    zeitgeschichts_pakt: ZeitgeschichtsPakt | None = None,
    *,
    senat_id: str = "geschichts-senat",
) -> GeschichtsSenat:
    if zeitgeschichts_pakt is None:
        zeitgeschichts_pakt = build_zeitgeschichts_pakt(pakt_id=f"{senat_id}-pakt")
    normen: list[GeschichtsSenatNorm] = []
    for parent_norm in zeitgeschichts_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.zeitgeschichts_pakt_id.removeprefix(f'{zeitgeschichts_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GeschichtsSenatGeltung.GRUNDLEGEND_GESCHICHTSWISSENSCHAFTLICH)
        normen.append(GeschichtsSenatNorm(
            geschichts_senat_id=new_id,
            geschichts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            geschichts_weight=new_weight,
            geschichts_tier=new_tier,
            canonical=is_canonical,
            geschichts_ids=parent_norm.geschichts_ids + (new_id,),
            geschichts_tags=parent_norm.geschichts_tags + (f"geschichts-senat:{new_geltung.value}",),
        ))
    return GeschichtsSenat(
        senat_id=senat_id,
        zeitgeschichts_pakt=zeitgeschichts_pakt,
        normen=tuple(normen),
    )
