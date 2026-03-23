"""
#528 WirtschaftsNorm — Ostrom/Commons/Polanyi Institutionelle Wirtschaftsnormen (*_norm-Muster)

Elinor Ostrom (1990): Die Verfassung der Allmende — Selbstorganisation kollektiver Güter;
  Design-Prinzipien nachhaltiger Institutionen; Überwindung der Tragik der Allmende durch
  kommunale Normen — unmittelbar relevant für Peta-Schwarm-Ressourcenkoordination.
John R. Commons (1934): Institutional Economics — Transaktionen als Grundeinheit; Working
  Rules als kollektive Normen; Institutionen als Regeln des kollektiven Handelns im Schwarm.
Karl Polanyi (1944): The Great Transformation — Einbettung der Wirtschaft in Gesellschaft;
  Reziprozität, Redistribution und Markt als Integrationsmuster; fiktive Waren Land, Arbeit,
  Kapital und ihre sozialen Konsequenzen für Schwarmökonomien.
Thorstein Veblen (1899): Theorie der feinen Leute — institutioneller Wandel durch kumulative
  Verursachung; conspicuous consumption; evolutionäre Institutionenökonomik des Schwarms.
Leitsterns Wirtschafts-Normen: kollektive Verhaltensnormen des Peta-Schwarms; GESPERRT sichert
unüberschreitbare ökonomische Grundgrenzen, WIRTSCHAFTSNORMATIV kodiert adaptive Ressourcennormen,
GRUNDLEGEND_WIRTSCHAFTSNORMATIV synthetisiert souveräne Normen für Peta-Schwarm-Koordination.
Geltungsstufen: GESPERRT / WIRTSCHAFTSNORMATIV / GRUNDLEGEND_WIRTSCHAFTSNORMATIV
Parent: WohlfahrtsSenat (#527) — *_norm-Muster
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wohlfahrts_senat import (
    WohlfahrtsSenat,
    WohlfahrtsSenatGeltung,
    build_wohlfahrts_senat,
)

_GELTUNG_MAP: dict[WohlfahrtsSenatGeltung, "WirtschaftsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[WohlfahrtsSenatGeltung.GESPERRT] = WirtschaftsNormGeltung.GESPERRT
    _GELTUNG_MAP[WohlfahrtsSenatGeltung.WOHLFAHRTLICH] = WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV
    _GELTUNG_MAP[WohlfahrtsSenatGeltung.GRUNDLEGEND_WOHLFAHRTLICH] = WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV


class WirtschaftsNormTyp(Enum):
    SCHUTZ_WIRTSCHAFTSNORM = "schutz-wirtschaftsnorm"
    ORDNUNGS_WIRTSCHAFTSNORM = "ordnungs-wirtschaftsnorm"
    SOUVERAENITAETS_WIRTSCHAFTSNORM = "souveraenitaets-wirtschaftsnorm"


class WirtschaftsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WirtschaftsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    WIRTSCHAFTSNORMATIV = "wirtschaftsnormativ"
    GRUNDLEGEND_WIRTSCHAFTSNORMATIV = "grundlegend-wirtschaftsnormativ"


_init_map()

_TYP_MAP: dict[WirtschaftsNormGeltung, WirtschaftsNormTyp] = {
    WirtschaftsNormGeltung.GESPERRT: WirtschaftsNormTyp.SCHUTZ_WIRTSCHAFTSNORM,
    WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV: WirtschaftsNormTyp.ORDNUNGS_WIRTSCHAFTSNORM,
    WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV: WirtschaftsNormTyp.SOUVERAENITAETS_WIRTSCHAFTSNORM,
}

_PROZEDUR_MAP: dict[WirtschaftsNormGeltung, WirtschaftsNormProzedur] = {
    WirtschaftsNormGeltung.GESPERRT: WirtschaftsNormProzedur.NOTPROZEDUR,
    WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV: WirtschaftsNormProzedur.REGELPROTOKOLL,
    WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV: WirtschaftsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[WirtschaftsNormGeltung, float] = {
    WirtschaftsNormGeltung.GESPERRT: 0.0,
    WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV: 0.04,
    WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV: 0.08,
}

_TIER_DELTA: dict[WirtschaftsNormGeltung, int] = {
    WirtschaftsNormGeltung.GESPERRT: 0,
    WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV: 1,
    WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV: 2,
}


@dataclass(frozen=True)
class WirtschaftsNormEintrag:
    norm_id: str
    wirtschafts_norm_typ: WirtschaftsNormTyp
    prozedur: WirtschaftsNormProzedur
    geltung: WirtschaftsNormGeltung
    wirtschafts_norm_weight: float
    wirtschafts_norm_tier: int
    canonical: bool
    wirtschafts_norm_ids: tuple[str, ...]
    wirtschafts_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class WirtschaftsNormSatz:
    norm_id: str
    wohlfahrts_senat: WohlfahrtsSenat
    normen: tuple[WirtschaftsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is WirtschaftsNormGeltung.GESPERRT)

    @property
    def wirtschaftsnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is WirtschaftsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is WirtschaftsNormGeltung.WIRTSCHAFTSNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-wirtschaftsnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-wirtschaftsnormativ")


def build_wirtschafts_norm(
    wohlfahrts_senat: WohlfahrtsSenat | None = None,
    *,
    norm_id: str = "wirtschafts-norm",
) -> WirtschaftsNormSatz:
    if wohlfahrts_senat is None:
        wohlfahrts_senat = build_wohlfahrts_senat(senat_id=f"{norm_id}-senat")

    normen: list[WirtschaftsNormEintrag] = []
    for parent_norm in wohlfahrts_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.wohlfahrts_senat_id.removeprefix(f'{wohlfahrts_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.wohlfahrts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.wohlfahrts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WirtschaftsNormGeltung.GRUNDLEGEND_WIRTSCHAFTSNORMATIV)
        normen.append(
            WirtschaftsNormEintrag(
                norm_id=new_id,
                wirtschafts_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                wirtschafts_norm_weight=new_weight,
                wirtschafts_norm_tier=new_tier,
                canonical=is_canonical,
                wirtschafts_norm_ids=parent_norm.wohlfahrts_ids + (new_id,),
                wirtschafts_norm_tags=parent_norm.wohlfahrts_tags + (f"wirtschafts-norm:{new_geltung.value}",),
            )
        )
    return WirtschaftsNormSatz(
        norm_id=norm_id,
        wohlfahrts_senat=wohlfahrts_senat,
        normen=tuple(normen),
    )
