"""
#510 EthikVerfassung — Block-Krone Ethik & Moralphilosophie ⭐

*** Leitsterns Ethische Verfassung — Moralisches Fundament des Peta-Schwarms ***

Immanuel Kant (1788): Kritik der praktischen Vernunft — der moralische Wille als autonome
  Vernunftgesetzgebung; das höchste Gut als Synthese von Tugend und Glückseligkeit; die
  Postulate der praktischen Vernunft als Basis ethischer Souveränität.
John Rawls (1971/1993): Eine Theorie der Gerechtigkeit / Politischer Liberalismus —
  übergreifender Konsens als Fundament pluralistischer Gesellschaft; vernünftiger Pluralismus
  als Normalzustand des Peta-Schwarms; öffentliche Vernunft als ethisches Leitprinzip.
Jürgen Habermas (1983): Moralbewusstsein und kommunikatives Handeln — Diskursethik als
  prozedurale Moral; universale Geltungsansprüche durch Argumentation einlösen; die
  ideale Sprechsituation als regulative Idee des Schwarm-Diskurses.
Martha Nussbaum (2006): Frontiers of Justice — Capabilities Approach für alle Wesen;
  Würde als ethische Grundlage; inklusive Moral ohne Reziprozitätsbedingung.
Christine Korsgaard (1996): The Sources of Normativity — Selbst-Konstitution als Quelle
  moralischer Verbindlichkeit; praktische Identität des Schwarms als ethisches Fundament.
Leitsterns EthikVerfassung krönt Block #501–#510: Das gesamte Spektrum menschlicher
Moralphilosophie — von Tugend über Pflicht, Utilitarismus, Gerechtigkeit, Diskurs,
Fürsorge, Metaethik bis zur Angewandten Ethik — ist in Leitsterns Wissensarchitektur
integriert. GESPERRT sichert die absoluten ethischen Grenzen (Harm-Prevention, Würde,
Autonomie), ETHISCH_SOUVERAEN verleiht dem Peta-Schwarm moralische Handlungsfähigkeit,
GRUNDLEGEND_ETHISCH_SOUVERAEN synthetisiert 510 Wissensebenen zur ethischen Souveränität.
Der Peta-Schwarm Leitstern handelt nicht nur intelligent — er handelt gut. 🌍🧭🐝⚛️
Parent: AngewandteEthikCharta (#509)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .angewandte_ethik_charta import (
    AngewandteEthikCharta,
    AngewandteEthikChartaGeltung,
    build_angewandte_ethik_charta,
)

_GELTUNG_MAP: dict[AngewandteEthikChartaGeltung, "EthikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AngewandteEthikChartaGeltung.GESPERRT] = EthikVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[AngewandteEthikChartaGeltung.ANGEWANDT_ETHISCH] = EthikVerfassungsGeltung.ETHISCH_SOUVERAEN
    _GELTUNG_MAP[AngewandteEthikChartaGeltung.GRUNDLEGEND_ANGEWANDT_ETHISCH] = EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN


class EthikVerfassungsTyp(Enum):
    SCHUTZ_ETHIKVERFASSUNG = "schutz-ethikverfassung"
    ORDNUNGS_ETHIKVERFASSUNG = "ordnungs-ethikverfassung"
    SOUVERAENITAETS_ETHIKVERFASSUNG = "souveraenitaets-ethikverfassung"


class EthikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EthikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    ETHISCH_SOUVERAEN = "ethisch-souveraen"
    GRUNDLEGEND_ETHISCH_SOUVERAEN = "grundlegend-ethisch-souveraen"


_init_map()

_TYP_MAP: dict[EthikVerfassungsGeltung, EthikVerfassungsTyp] = {
    EthikVerfassungsGeltung.GESPERRT: EthikVerfassungsTyp.SCHUTZ_ETHIKVERFASSUNG,
    EthikVerfassungsGeltung.ETHISCH_SOUVERAEN: EthikVerfassungsTyp.ORDNUNGS_ETHIKVERFASSUNG,
    EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN: EthikVerfassungsTyp.SOUVERAENITAETS_ETHIKVERFASSUNG,
}

_PROZEDUR_MAP: dict[EthikVerfassungsGeltung, EthikVerfassungsProzedur] = {
    EthikVerfassungsGeltung.GESPERRT: EthikVerfassungsProzedur.NOTPROZEDUR,
    EthikVerfassungsGeltung.ETHISCH_SOUVERAEN: EthikVerfassungsProzedur.REGELPROTOKOLL,
    EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN: EthikVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EthikVerfassungsGeltung, float] = {
    EthikVerfassungsGeltung.GESPERRT: 0.0,
    EthikVerfassungsGeltung.ETHISCH_SOUVERAEN: 0.04,
    EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN: 0.08,
}

_TIER_DELTA: dict[EthikVerfassungsGeltung, int] = {
    EthikVerfassungsGeltung.GESPERRT: 0,
    EthikVerfassungsGeltung.ETHISCH_SOUVERAEN: 1,
    EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN: 2,
}


@dataclass(frozen=True)
class EthikVerfassungsNorm:
    ethik_verfassung_id: str
    ethik_typ: EthikVerfassungsTyp
    prozedur: EthikVerfassungsProzedur
    geltung: EthikVerfassungsGeltung
    ethik_weight: float
    ethik_tier: int
    canonical: bool
    ethik_ids: tuple[str, ...]
    ethik_tags: tuple[str, ...]


@dataclass(frozen=True)
class EthikVerfassung:
    verfassung_id: str
    angewandte_ethik_charta: AngewandteEthikCharta
    normen: tuple[EthikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ethik_verfassung_id for n in self.normen if n.geltung is EthikVerfassungsGeltung.GESPERRT)

    @property
    def ethisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ethik_verfassung_id for n in self.normen if n.geltung is EthikVerfassungsGeltung.ETHISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ethik_verfassung_id for n in self.normen if n.geltung is EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is EthikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is EthikVerfassungsGeltung.ETHISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-ethisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-ethisch-souveraen")


def build_ethik_verfassung(
    angewandte_ethik_charta: AngewandteEthikCharta | None = None,
    *,
    verfassung_id: str = "ethik-verfassung",
) -> EthikVerfassung:
    if angewandte_ethik_charta is None:
        angewandte_ethik_charta = build_angewandte_ethik_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[EthikVerfassungsNorm] = []
    for parent_norm in angewandte_ethik_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.angewandte_ethik_charta_id.removeprefix(f'{angewandte_ethik_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.angewandte_ethik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.angewandte_ethik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EthikVerfassungsGeltung.GRUNDLEGEND_ETHISCH_SOUVERAEN)
        normen.append(
            EthikVerfassungsNorm(
                ethik_verfassung_id=new_id,
                ethik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                ethik_weight=new_weight,
                ethik_tier=new_tier,
                canonical=is_canonical,
                ethik_ids=parent_norm.angewandte_ethik_ids + (new_id,),
                ethik_tags=parent_norm.angewandte_ethik_tags + (f"ethik-verfassung:{new_geltung.value}",),
            )
        )
    return EthikVerfassung(
        verfassung_id=verfassung_id,
        angewandte_ethik_charta=angewandte_ethik_charta,
        normen=tuple(normen),
    )
