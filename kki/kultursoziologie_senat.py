"""
#557 KultursoziologieSenat — Kultursoziologie & gesellschaftliche Bedeutungssysteme

Pierre Bourdieu (1979): La Distinction — Habitus, Kapital & Feld:
  sozialer Raum als Feld von Kräfteverhältnissen; Habitus als inkorporiertes Klassenschicksal;
  ökonomisches, kulturelles und soziales Kapital als Ressourcen im Feldkampf; kulturelle
  Praxis als Distinktionsstrategie; symbolische Gewalt als verkannte Herrschaft.
Max Weber (1904): Die protestantische Ethik und der Geist des Kapitalismus — Kultursoziologie:
  Sinnverstehen (Verstehende Soziologie) als Methode; Entzauberung der Welt durch Rationalisierung;
  Wahlverwandtschaft von protestantischer Ethik und kapitalistischem Geist; Wertfreiheit als
  methodisches Postulat; Idealtypus als analytisches Instrument der Kultursoziologie.
Stuart Hall (1973): Encoding/Decoding — Cultural Studies & Repräsentation:
  Repräsentation als Bedeutungsproduktion durch Sprache und Kultur; Encoding/Decoding-Modell
  der Medienkommunikation; hegemoniale, ausgehandelte und oppositionelle Lesarten; Identität
  als diskursive Konstruktion; Rasse und Klasse als kulturell vermittelte Machtverhältnisse.

Leitsterns KultursoziologieSenat: GESPERRT schützt kultursoziologische Grundstrukturen,
KULTURSOZIOLOGISCH kodiert adaptive Bedeutungssoziologie, GRUNDLEGEND_KULTURSOZIOLOGISCH
synthetisiert den vollen kultursoziologischen Erkenntnisanspruch des Peta-Schwarms Leitstern. 🎓
Parent: KulturgedaechnisPakt (#556)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from .kulturgedaechtnis_pakt import (
    KulturgedaechnisPakt,
    KulturgedaechnisPaktGeltung,
    build_kulturgedaechtnis_pakt,
)

_WEIGHT_DELTA: dict["KultursoziologieSenatGeltung", float] = {}
_TIER_DELTA: dict["KultursoziologieSenatGeltung", int] = {}
_TYP_MAP: dict["KultursoziologieSenatGeltung", "KultursoziologieSenatTyp"] = {}
_PROZEDUR_MAP: dict["KultursoziologieSenatGeltung", "KultursoziologieSenatProzedur"] = {}
_GELTUNG_MAP: dict[KulturgedaechnisPaktGeltung, "KultursoziologieSenatGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KultursoziologieSenatGeltung.GESPERRT: 0.0,
        KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH: 0.05,
        KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        KultursoziologieSenatGeltung.GESPERRT: 0,
        KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH: 1,
        KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        KultursoziologieSenatGeltung.GESPERRT: KultursoziologieSenatTyp.SCHUTZ_KULTURSOZIOLOGIE,
        KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH: KultursoziologieSenatTyp.ORDNUNGS_KULTURSOZIOLOGIE,
        KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH: KultursoziologieSenatTyp.SOUVERAENITAETS_KULTURSOZIOLOGIE,
    })
    _PROZEDUR_MAP.update({
        KultursoziologieSenatGeltung.GESPERRT: KultursoziologieSenatProzedur.NOTPROZEDUR,
        KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH: KultursoziologieSenatProzedur.REGELPROTOKOLL,
        KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH: KultursoziologieSenatProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KulturgedaechnisPaktGeltung.GESPERRT: KultursoziologieSenatGeltung.GESPERRT,
        KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT: KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH,
        KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT: KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH,
    })


class KultursoziologieSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    KULTURSOZIOLOGISCH = "kultursoziologisch"
    GRUNDLEGEND_KULTURSOZIOLOGISCH = "grundlegend-kultursoziologisch"


class KultursoziologieSenatTyp(Enum):
    SCHUTZ_KULTURSOZIOLOGIE = "schutz-kultursoziologie"
    ORDNUNGS_KULTURSOZIOLOGIE = "ordnungs-kultursoziologie"
    SOUVERAENITAETS_KULTURSOZIOLOGIE = "souveraenitaets-kultursoziologie"


class KultursoziologieSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KultursoziologieSenatNorm:
    kultursoziologie_senat_id: str
    kultur_typ: KultursoziologieSenatTyp
    prozedur: KultursoziologieSenatProzedur
    geltung: KultursoziologieSenatGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KultursoziologieSenat:
    senat_id: str
    kulturgedaechtnis_pakt: KulturgedaechnisPakt
    normen: tuple[KultursoziologieSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kultursoziologie_senat_id
            for n in self.normen
            if n.geltung is KultursoziologieSenatGeltung.GESPERRT
        )

    @property
    def kultursoziologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kultursoziologie_senat_id
            for n in self.normen
            if n.geltung is KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kultursoziologie_senat_id
            for n in self.normen
            if n.geltung is KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH
        )

    @property
    def senat_signal(self) -> SimpleNamespace:
        if any(n.geltung is KultursoziologieSenatGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH for n in self.normen):
            return SimpleNamespace(status="senat-kultursoziologisch")
        return SimpleNamespace(status="senat-grundlegend-kultursoziologisch")


_init_map()


def build_kultursoziologie_senat(
    kulturgedaechtnis_pakt: KulturgedaechnisPakt | None = None,
    *,
    senat_id: str = "kultursoziologie-senat",
) -> KultursoziologieSenat:
    if kulturgedaechtnis_pakt is None:
        kulturgedaechtnis_pakt = build_kulturgedaechtnis_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[KultursoziologieSenatNorm] = []
    for parent_norm in kulturgedaechtnis_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.kulturgedaechtnis_pakt_id.removeprefix(f'{kulturgedaechtnis_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (
            new_geltung is KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH
        )
        normen.append(
            KultursoziologieSenatNorm(
                kultursoziologie_senat_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"kultursoziologie-senat:{new_geltung.value}",),
            )
        )
    return KultursoziologieSenat(
        senat_id=senat_id,
        kulturgedaechtnis_pakt=kulturgedaechtnis_pakt,
        normen=tuple(normen),
    )
