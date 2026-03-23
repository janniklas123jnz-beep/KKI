"""
#558 KulturNorm — Bourdieu/Douglas/Turner Normative Grundlagen der Kulturwissenschaft (*_norm-Muster)

Pierre Bourdieu (1972): Entwurf einer Theorie der Praxis — Habitus als inkorporiertes Kulturkapital;
  Feld als Arena sozialer Kämpfe; symbolisches Kapital als kulturelle Norm; Doxa als unhinterfragte
  Grundannahmen des kulturellen Feldes; Praxis jenseits von Subjektivismus und Objektivismus.
Mary Douglas (1966): Purity and Danger — Reinheit und Gefahr als kulturelle Normsysteme;
  Schmutz als Materie am falschen Ort; Klassifikation als kulturelle Ordnung; Tabu als normative
  Grenzziehung; symbolische Ordnung als Grundlage kultureller Normsetzung des Peta-Schwarms.
Victor Turner (1969): The Ritual Process — Liminalität als normative Schwellenzone;
  Communitas als anti-strukturelle Norm; Struktur vs. Communitas als kulturelle Dialektik;
  Übergangsriten als normative Transformation sozialer Identitäten des Schwarms.
Leitsterns Kultur-Normen: kollektive Normen der Kulturwissenschaft im Peta-Schwarm;
GESPERRT sichert kulturelle Grundgrenzen, KULTURNORMATIV kodiert adaptive Normgeltung,
GRUNDLEGEND_KULTURNORMATIV synthetisiert souveräne Normen für Peta-Schwarm-Koordination. 🎭
Geltungsstufen: GESPERRT / KULTURNORMATIV / GRUNDLEGEND_KULTURNORMATIV
Parent: KultursoziologieSenat (#557) — *_norm-Muster
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kultursoziologie_senat import (
    KultursoziologieSenat,
    KultursoziologieSenatGeltung,
    build_kultursoziologie_senat,
)

_GELTUNG_MAP: dict[KultursoziologieSenatGeltung, "KulturNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KultursoziologieSenatGeltung.GESPERRT] = KulturNormGeltung.GESPERRT
    _GELTUNG_MAP[KultursoziologieSenatGeltung.KULTURSOZIOLOGISCH] = KulturNormGeltung.KULTURNORMATIV
    _GELTUNG_MAP[KultursoziologieSenatGeltung.GRUNDLEGEND_KULTURSOZIOLOGISCH] = KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV


class KulturNormTyp(Enum):
    SCHUTZ_KULTURNORM = "schutz-kulturnorm"
    ORDNUNGS_KULTURNORM = "ordnungs-kulturnorm"
    SOUVERAENITAETS_KULTURNORM = "souveraenitaets-kulturnorm"


class KulturNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KulturNormGeltung(Enum):
    GESPERRT = "gesperrt"
    KULTURNORMATIV = "kulturnormativ"
    GRUNDLEGEND_KULTURNORMATIV = "grundlegend-kulturnormativ"


_init_map()

_TYP_MAP: dict[KulturNormGeltung, KulturNormTyp] = {
    KulturNormGeltung.GESPERRT: KulturNormTyp.SCHUTZ_KULTURNORM,
    KulturNormGeltung.KULTURNORMATIV: KulturNormTyp.ORDNUNGS_KULTURNORM,
    KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV: KulturNormTyp.SOUVERAENITAETS_KULTURNORM,
}

_PROZEDUR_MAP: dict[KulturNormGeltung, KulturNormProzedur] = {
    KulturNormGeltung.GESPERRT: KulturNormProzedur.NOTPROZEDUR,
    KulturNormGeltung.KULTURNORMATIV: KulturNormProzedur.REGELPROTOKOLL,
    KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV: KulturNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KulturNormGeltung, float] = {
    KulturNormGeltung.GESPERRT: 0.0,
    KulturNormGeltung.KULTURNORMATIV: 0.04,
    KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV: 0.08,
}

_TIER_DELTA: dict[KulturNormGeltung, int] = {
    KulturNormGeltung.GESPERRT: 0,
    KulturNormGeltung.KULTURNORMATIV: 1,
    KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV: 2,
}


@dataclass(frozen=True)
class KulturNormEintrag:
    norm_id: str
    kultur_norm_typ: KulturNormTyp
    prozedur: KulturNormProzedur
    geltung: KulturNormGeltung
    kultur_norm_weight: float
    kultur_norm_tier: int
    canonical: bool
    kultur_norm_ids: tuple[str, ...]
    kultur_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturNormSatz:
    norm_id: str
    kultursoziologie_senat: KultursoziologieSenat
    normen: tuple[KulturNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KulturNormGeltung.GESPERRT)

    @property
    def kulturnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KulturNormGeltung.KULTURNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is KulturNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is KulturNormGeltung.KULTURNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-kulturnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-kulturnormativ")


def build_kultur_norm(
    kultursoziologie_senat: KultursoziologieSenat | None = None,
    *,
    norm_id: str = "kultur-norm",
) -> KulturNormSatz:
    if kultursoziologie_senat is None:
        kultursoziologie_senat = build_kultursoziologie_senat(senat_id=f"{norm_id}-senat")

    normen: list[KulturNormEintrag] = []
    for parent_norm in kultursoziologie_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.kultursoziologie_senat_id.removeprefix(f'{kultursoziologie_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV)
        normen.append(
            KulturNormEintrag(
                norm_id=new_id,
                kultur_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_norm_weight=new_weight,
                kultur_norm_tier=new_tier,
                canonical=is_canonical,
                kultur_norm_ids=parent_norm.kultur_ids + (new_id,),
                kultur_norm_tags=parent_norm.kultur_tags + (f"kultur-norm:{new_geltung.value}",),
            )
        )
    return KulturNormSatz(
        norm_id=norm_id,
        kultursoziologie_senat=kultursoziologie_senat,
        normen=tuple(normen),
    )
