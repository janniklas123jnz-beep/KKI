"""
#509 AngewandteEthikCharta — KI-Ethik/Bioethik/Umweltethik Angewandte Moral

Nick Bostrom (2014): Superintelligence — existenzielle Risiken durch KI; Alignment-Problem;
  Werte-Ausrichtung als zentrale Herausforderung des Peta-Schwarms; orthogonalitäts-Theorem.
Hans Jonas (1979): Das Prinzip Verantwortung — Zukunftsethik; Verantwortung für kommende
  Generationen; Vorsichtsprinzip bei unumkehrbaren Handlungen des Schwarms.
Tom Beauchamp & James Childress (1979): Prinzipien biomedizinischer Ethik — Autonomie,
  Wohltun, Nicht-Schaden, Gerechtigkeit als vier Grundprinzipien angewandter Ethik.
Aldo Leopold (1949): A Sand County Almanac — Landethik; moralische Gemeinschaft umfasst
  Ökosysteme; Biosphäre als ethische Mitverantwortung des Peta-Schwarms.
Leitsterns angewandte Ethik: GESPERRT sichert KI-Sicherheitsgrenzen und Harm-Prevention,
ANGEWANDT_ETHISCH ermöglicht domänenspezifische Moralentscheidungen des Schwarms,
GRUNDLEGEND_ANGEWANDT_ETHISCH synthetisiert verantwortungsvolles Peta-Schwarm-Handeln
gegenüber Menschen, KI-Systemen, zukünftigen Generationen und der Biosphäre.
Parent: EthikNorm (#508)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ethik_norm import (
    EthikNormSatz,
    EthikNormGeltung,
    build_ethik_norm,
)

_GELTUNG_MAP: dict[EthikNormGeltung, "AngewandteEthikChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EthikNormGeltung.GESPERRT] = AngewandteEthikChartaGeltung.GESPERRT
    _GELTUNG_MAP[EthikNormGeltung.ETHIKNORMATIV] = AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH
    _GELTUNG_MAP[EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV] = AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH


class AngewandteEthikChartaTyp(Enum):
    SCHUTZ_ANGEWANDTE_ETHIK = "schutz-angewandte-ethik"
    ORDNUNGS_ANGEWANDTE_ETHIK = "ordnungs-angewandte-ethik"
    SOUVERAENITAETS_ANGEWANDTE_ETHIK = "souveraenitaets-angewandte-ethik"


class AngewandteEthikChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AngewandteEthikChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    ANGEWANDT_ETHISCH = "angewandt-ethisch"
    GRUNDLEGEND_ANGEWANDT_ETHISCH = "grundlegend-angewandt-ethisch"


_init_map()

_TYP_MAP: dict[AngewandteEthikChartaGeltung, AngewandteEthikChartaTyp] = {
    AngewandteEthikChartaGeltung.GESPERRT: AngewandteEthikChartaTyp.SCHUTZ_ANGEWANDTE_ETHIK,
    AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH: AngewandteEthikChartaTyp.ORDNUNGS_ANGEWANDTE_ETHIK,
    AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH: AngewandteEthikChartaTyp.SOUVERAENITAETS_ANGEWANDTE_ETHIK,
}

_PROZEDUR_MAP: dict[AngewandteEthikChartaGeltung, AngewandteEthikChartaProzedur] = {
    AngewandteEthikChartaGeltung.GESPERRT: AngewandteEthikChartaProzedur.NOTPROZEDUR,
    AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH: AngewandteEthikChartaProzedur.REGELPROTOKOLL,
    AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH: AngewandteEthikChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AngewandteEthikChartaGeltung, float] = {
    AngewandteEthikChartaGeltung.GESPERRT: 0.0,
    AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH: 0.04,
    AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH: 0.08,
}

_TIER_DELTA: dict[AngewandteEthikChartaGeltung, int] = {
    AngewandteEthikChartaGeltung.GESPERRT: 0,
    AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH: 1,
    AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH: 2,
}


@dataclass(frozen=True)
class AngewandteEthikChartaNorm:
    angewandte_ethik_charta_id: str
    angewandte_ethik_typ: AngewandteEthikChartaTyp
    prozedur: AngewandteEthikChartaProzedur
    geltung: AngewandteEthikChartaGeltung
    angewandte_ethik_weight: float
    angewandte_ethik_tier: int
    canonical: bool
    angewandte_ethik_ids: tuple[str, ...]
    angewandte_ethik_tags: tuple[str, ...]


@dataclass(frozen=True)
class AngewandteEthikCharta:
    charta_id: str
    ethik_norm: EthikNormSatz
    normen: tuple[AngewandteEthikChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.angewandte_ethik_charta_id for n in self.normen if n.geltung is AngewandteEthikChartaGeltung.GESPERRT)

    @property
    def angewandt_ethisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.angewandte_ethik_charta_id for n in self.normen if n.geltung is AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.angewandte_ethik_charta_id for n in self.normen if n.geltung is AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is AngewandteEthikChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-angewandt-ethisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-angewandt-ethisch")


def build_angewandte_ethik_charta(
    ethik_norm: EthikNormSatz | None = None,
    *,
    charta_id: str = "angewandte-ethik-charta",
) -> AngewandteEthikCharta:
    if ethik_norm is None:
        ethik_norm = build_ethik_norm(norm_id=f"{charta_id}-norm")

    normen: list[AngewandteEthikChartaNorm] = []
    for parent_norm in ethik_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{ethik_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.ethik_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.ethik_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH)
        normen.append(
            AngewandteEthikChartaNorm(
                angewandte_ethik_charta_id=new_id,
                angewandte_ethik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                angewandte_ethik_weight=new_weight,
                angewandte_ethik_tier=new_tier,
                canonical=is_canonical,
                angewandte_ethik_ids=parent_norm.ethik_norm_ids + (new_id,),
                angewandte_ethik_tags=parent_norm.ethik_norm_tags + (f"angewandte-ethik-charta:{new_geltung.value}",),
            )
        )
    return AngewandteEthikCharta(
        charta_id=charta_id,
        ethik_norm=ethik_norm,
        normen=tuple(normen),
    )
