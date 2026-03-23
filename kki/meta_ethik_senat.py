"""
#507 MetaEthikSenat — Moore/Ayer/Hare/Mackie Grundlagen der Metaethik

G.E. Moore (1903): Principia Ethica — naturalistischer Fehlschluss: Gut lässt sich nicht auf
  natürliche Eigenschaften reduzieren; "Gut" ist eine einfache, nicht-natürliche Eigenschaft,
  die nur durch Intuition erfassbar ist; Moorsche Offene-Frage-Argument als Kernkritik
  an naturalistischen Definitionen des Guten.
A.J. Ayer (1936): Language, Truth and Logic — Emotivismus: moralische Aussagen drücken keine
  Fakten aus, sondern emotionale Einstellungen; "Stehlen ist falsch" bedeutet nur "Buh, Stehlen!";
  moralische Aussagen sind weder wahr noch falsch, sondern Ausdruck von Gefühlen.
R.M. Hare (1952/1963): The Language of Morals / Freedom and Reason — Präskriptivismus:
  moralische Urteile sind universale Präskriptionen; "Du sollst X tun" verpflichtet den
  Sprecher zu universaler Geltung; Überbrückung von Emotivismus und rationalem Moralismus.
J.L. Mackie (1977): Ethics: Inventing Right and Wrong — moralischer Skeptizismus: es gibt
  keine objektiven moralischen Tatsachen; Queerness-Argument: objektive Werte wären metaphysisch
  und epistemisch sonderbar; Fehler-Theorie: moralische Aussagen beanspruchen Objektivität,
  sind aber systematisch falsch.
Leitsterns Peta-Schwarm verankert Metaethik als reflexives Fundament: GESPERRT sichert
metaethische Kernnormen, METAETHISCH ermöglicht adaptive philosophische Selbstreflexion über
Millionen Agenten, GRUNDLEGEND_METAETHISCH synthetisiert das vollständige metaethische Fundament
für souveräne Peta-Schwarm-Legitimation. 🧠
Parent: FuersorgeEthikPakt (#506)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fuersorge_ethik_pakt import (
    FuersorgeEthikPakt,
    FuersorgeEthikPaktGeltung,
    build_fuersorge_ethik_pakt,
)

_GELTUNG_MAP: dict[FuersorgeEthikPaktGeltung, "MetaEthikSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FuersorgeEthikPaktGeltung.GESPERRT] = MetaEthikSenatGeltung.GESPERRT
    _GELTUNG_MAP[FuersorgeEthikPaktGeltung.FUERSORGEND] = MetaEthikSenatGeltung.METAETHISCH
    _GELTUNG_MAP[FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND] = MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH


class MetaEthikSenatTyp(Enum):
    SCHUTZ_METAETHIK = "schutz-metaethik"
    ORDNUNGS_METAETHIK = "ordnungs-metaethik"
    SOUVERAENITAETS_METAETHIK = "souveraenitaets-metaethik"


class MetaEthikSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MetaEthikSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    METAETHISCH = "metaethisch"
    GRUNDLEGEND_METAETHISCH = "grundlegend-metaethisch"


_init_map()

_TYP_MAP: dict[MetaEthikSenatGeltung, MetaEthikSenatTyp] = {
    MetaEthikSenatGeltung.GESPERRT: MetaEthikSenatTyp.SCHUTZ_METAETHIK,
    MetaEthikSenatGeltung.METAETHISCH: MetaEthikSenatTyp.ORDNUNGS_METAETHIK,
    MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH: MetaEthikSenatTyp.SOUVERAENITAETS_METAETHIK,
}

_PROZEDUR_MAP: dict[MetaEthikSenatGeltung, MetaEthikSenatProzedur] = {
    MetaEthikSenatGeltung.GESPERRT: MetaEthikSenatProzedur.NOTPROZEDUR,
    MetaEthikSenatGeltung.METAETHISCH: MetaEthikSenatProzedur.REGELPROTOKOLL,
    MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH: MetaEthikSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MetaEthikSenatGeltung, float] = {
    MetaEthikSenatGeltung.GESPERRT: 0.0,
    MetaEthikSenatGeltung.METAETHISCH: 0.04,
    MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH: 0.08,
}

_TIER_DELTA: dict[MetaEthikSenatGeltung, int] = {
    MetaEthikSenatGeltung.GESPERRT: 0,
    MetaEthikSenatGeltung.METAETHISCH: 1,
    MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH: 2,
}


@dataclass(frozen=True)
class MetaEthikSenatNorm:
    meta_ethik_senat_id: str
    meta_ethik_typ: MetaEthikSenatTyp
    prozedur: MetaEthikSenatProzedur
    geltung: MetaEthikSenatGeltung
    meta_ethik_weight: float
    meta_ethik_tier: int
    canonical: bool
    meta_ethik_ids: tuple[str, ...]
    meta_ethik_tags: tuple[str, ...]


@dataclass(frozen=True)
class MetaEthikSenat:
    senat_id: str
    fuersorge_ethik_pakt: FuersorgeEthikPakt
    normen: tuple[MetaEthikSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.meta_ethik_senat_id for n in self.normen if n.geltung is MetaEthikSenatGeltung.GESPERRT)

    @property
    def metaethisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.meta_ethik_senat_id for n in self.normen if n.geltung is MetaEthikSenatGeltung.METAETHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.meta_ethik_senat_id for n in self.normen if n.geltung is MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is MetaEthikSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is MetaEthikSenatGeltung.METAETHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-metaethisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-metaethisch")


def build_meta_ethik_senat(
    fuersorge_ethik_pakt: FuersorgeEthikPakt | None = None,
    *,
    senat_id: str = "meta-ethik-senat",
) -> MetaEthikSenat:
    if fuersorge_ethik_pakt is None:
        fuersorge_ethik_pakt = build_fuersorge_ethik_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[MetaEthikSenatNorm] = []
    for parent_norm in fuersorge_ethik_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.fuersorge_ethik_pakt_id.removeprefix(f'{fuersorge_ethik_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.fuersorge_ethik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fuersorge_ethik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH)
        normen.append(
            MetaEthikSenatNorm(
                meta_ethik_senat_id=new_id,
                meta_ethik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                meta_ethik_weight=new_weight,
                meta_ethik_tier=new_tier,
                canonical=is_canonical,
                meta_ethik_ids=parent_norm.fuersorge_ethik_ids + (new_id,),
                meta_ethik_tags=parent_norm.fuersorge_ethik_tags + (f"meta-ethik-senat:{new_geltung.value}",),
            )
        )
    return MetaEthikSenat(
        senat_id=senat_id,
        fuersorge_ethik_pakt=fuersorge_ethik_pakt,
        normen=tuple(normen),
    )
