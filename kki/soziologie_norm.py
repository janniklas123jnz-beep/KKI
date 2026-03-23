"""
#498 SoziologieNorm — Merton/Coleman/Elias Soziale Normen & Kollektivregeln (*_norm-Muster)

Robert K. Merton (1949): Soziale Theorie und soziale Struktur — Normen als soziale Erwartungen;
  manifeste vs. latente Funktionen; Anomie als Normdissonanz zwischen Zielen und Mitteln.
James S. Coleman (1990): Grundlagen der Sozialtheorie — soziales Kapital als Normressource;
  Kollektivgüter durch normative Bindungen; Vertrauen als generalisierte Norm.
Norbert Elias (1939): Über den Prozess der Zivilisation — Langzeitprozesse der Norm-Internalisierung;
  Figurationssysteme; Fremdzwänge werden zu Selbstzwängen durch Sozialisation.
Erving Goffman (1959): Wir alle spielen Theater — Interaktionsnormen; face-work; dramaturgische
  Analyse sozialer Normbefolgung im Alltag des Terra-Schwarms.
Leitsterns Soziologie-Normen: kollektive Verhaltenserwartungen des Terra-Schwarms; GESPERRT sichert
Kernnormen, SOZIALNORMATIV kodiert adaptive Gesellschaftsregeln, GRUNDLEGEND_SOZIALNORMATIV
synthetisiert zivilisatorische Normintegration für die Peta-Schwarm-Koordination.
Geltungsstufen: GESPERRT / SOZIALNORMATIV / GRUNDLEGEND_SOZIALNORMATIV
Parent: KommunikationsSenat (#497) — *_norm-Muster
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kommunikations_senat import (
    KommunikationsSenat,
    KommunikationsSenatGeltung,
    build_kommunikations_senat,
)

_GELTUNG_MAP: dict[KommunikationsSenatGeltung, "SoziologieNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KommunikationsSenatGeltung.GESPERRT] = SoziologieNormGeltung.GESPERRT
    _GELTUNG_MAP[KommunikationsSenatGeltung.KOMMUNIKATIV] = SoziologieNormGeltung.SOZIALNORMATIV
    _GELTUNG_MAP[KommunikationsSenatGeltung.GRUNDLEGEND_KOMMUNIKATIV] = SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV


class SoziologieNormTyp(Enum):
    SCHUTZ_SOZIOLOGIENORM = "schutz-soziologienorm"
    ORDNUNGS_SOZIOLOGIENORM = "ordnungs-soziologienorm"
    SOUVERAENITAETS_SOZIOLOGIENORM = "souveraenitaets-soziologienorm"


class SoziologieNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SoziologieNormGeltung(Enum):
    GESPERRT = "gesperrt"
    SOZIALNORMATIV = "sozialnormativ"
    GRUNDLEGEND_SOZIALNORMATIV = "grundlegend-sozialnormativ"


_init_map()

_TYP_MAP: dict[SoziologieNormGeltung, SoziologieNormTyp] = {
    SoziologieNormGeltung.GESPERRT: SoziologieNormTyp.SCHUTZ_SOZIOLOGIENORM,
    SoziologieNormGeltung.SOZIALNORMATIV: SoziologieNormTyp.ORDNUNGS_SOZIOLOGIENORM,
    SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV: SoziologieNormTyp.SOUVERAENITAETS_SOZIOLOGIENORM,
}

_PROZEDUR_MAP: dict[SoziologieNormGeltung, SoziologieNormProzedur] = {
    SoziologieNormGeltung.GESPERRT: SoziologieNormProzedur.NOTPROZEDUR,
    SoziologieNormGeltung.SOZIALNORMATIV: SoziologieNormProzedur.REGELPROTOKOLL,
    SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV: SoziologieNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SoziologieNormGeltung, float] = {
    SoziologieNormGeltung.GESPERRT: 0.0,
    SoziologieNormGeltung.SOZIALNORMATIV: 0.04,
    SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV: 0.08,
}

_TIER_DELTA: dict[SoziologieNormGeltung, int] = {
    SoziologieNormGeltung.GESPERRT: 0,
    SoziologieNormGeltung.SOZIALNORMATIV: 1,
    SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV: 2,
}


@dataclass(frozen=True)
class SoziologieNormEintrag:
    norm_id: str
    soziologie_norm_typ: SoziologieNormTyp
    prozedur: SoziologieNormProzedur
    geltung: SoziologieNormGeltung
    soziologie_norm_weight: float
    soziologie_norm_tier: int
    canonical: bool
    soziologie_norm_ids: tuple[str, ...]
    soziologie_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class SoziologieNormSatz:
    norm_id: str
    kommunikations_senat: KommunikationsSenat
    normen: tuple[SoziologieNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SoziologieNormGeltung.GESPERRT)

    @property
    def sozialnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SoziologieNormGeltung.SOZIALNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is SoziologieNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is SoziologieNormGeltung.SOZIALNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-sozialnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-sozialnormativ")


def build_soziologie_norm(
    kommunikations_senat: KommunikationsSenat | None = None,
    *,
    norm_id: str = "soziologie-norm",
) -> SoziologieNormSatz:
    if kommunikations_senat is None:
        kommunikations_senat = build_kommunikations_senat(senat_id=f"{norm_id}-senat")

    normen: list[SoziologieNormEintrag] = []
    for parent_norm in kommunikations_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.kommunikations_senat_id.removeprefix(f'{kommunikations_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.kommunikations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kommunikations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV)
        normen.append(
            SoziologieNormEintrag(
                norm_id=new_id,
                soziologie_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                soziologie_norm_weight=new_weight,
                soziologie_norm_tier=new_tier,
                canonical=is_canonical,
                soziologie_norm_ids=parent_norm.kommunikations_ids + (new_id,),
                soziologie_norm_tags=parent_norm.kommunikations_tags + (f"soziologie-norm:{new_geltung.value}",),
            )
        )
    return SoziologieNormSatz(
        norm_id=norm_id,
        kommunikations_senat=kommunikations_senat,
        normen=tuple(normen),
    )
