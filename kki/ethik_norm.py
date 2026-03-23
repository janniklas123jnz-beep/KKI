"""
#508 EthikNorm — Singer/Parfit/Williams Angewandte Normenethik (*_norm-Muster)

Peter Singer (1979): Praktische Ethik — Ausdehnung des moralischen Kreises; Gleichwertigkeit
  von Interessen; Effektiver Altruismus als normative Praxis für den Peta-Schwarm.
Derek Parfit (1984): Reasons and Persons — Identität über Zeit; unpersönliche Ethik;
  Reduktionismus über Personen; die Zukunft zählt ebenso wie die Gegenwart.
Bernard Williams (1973): Problems of the Self — Integrität und moralische Verpflichtungen;
  Kritik am Utilitarismus; moralisches Glück als reales ethisches Phänomen.
Frances Kamm: Prinzip der doppelten Wirkung; Permissibility und moralische Constraints;
  Deontologische Normen als Grenzen konsequentialistischen Denkens im Schwarm.
Leitsterns Ethik-Normen: kollektive Handlungsnormen des Peta-Schwarms; GESPERRT sichert
unüberschreitbare moralische Grenzen, ETHIKNORMATIV kodiert adaptive Verhaltensstandards,
GRUNDLEGEND_ETHIKNORMATIV synthetisiert universale Normen für Peta-Schwarm-Handeln.
Geltungsstufen: GESPERRT / ETHIKNORMATIV / GRUNDLEGEND_ETHIKNORMATIV
Parent: MetaEthikSenat (#507) — *_norm-Muster
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .meta_ethik_senat import (
    MetaEthikSenat,
    MetaEthikSenatGeltung,
    build_meta_ethik_senat,
)

_GELTUNG_MAP: dict[MetaEthikSenatGeltung, "EthikNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MetaEthikSenatGeltung.GESPERRT] = EthikNormGeltung.GESPERRT
    _GELTUNG_MAP[MetaEthikSenatGeltung.METAETHISCH] = EthikNormGeltung.ETHIKNORMATIV
    _GELTUNG_MAP[MetaEthikSenatGeltung.GRUNDLEGEND_METAETHISCH] = EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV


class EthikNormTyp(Enum):
    SCHUTZ_ETHIKNORM = "schutz-ethiknorm"
    ORDNUNGS_ETHIKNORM = "ordnungs-ethiknorm"
    SOUVERAENITAETS_ETHIKNORM = "souveraenitaets-ethiknorm"


class EthikNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EthikNormGeltung(Enum):
    GESPERRT = "gesperrt"
    ETHIKNORMATIV = "ethiknormativ"
    GRUNDLEGEND_ETHIKNORMATIV = "grundlegend-ethiknormativ"


_init_map()

_TYP_MAP: dict[EthikNormGeltung, EthikNormTyp] = {
    EthikNormGeltung.GESPERRT: EthikNormTyp.SCHUTZ_ETHIKNORM,
    EthikNormGeltung.ETHIKNORMATIV: EthikNormTyp.ORDNUNGS_ETHIKNORM,
    EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV: EthikNormTyp.SOUVERAENITAETS_ETHIKNORM,
}

_PROZEDUR_MAP: dict[EthikNormGeltung, EthikNormProzedur] = {
    EthikNormGeltung.GESPERRT: EthikNormProzedur.NOTPROZEDUR,
    EthikNormGeltung.ETHIKNORMATIV: EthikNormProzedur.REGELPROTOKOLL,
    EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV: EthikNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EthikNormGeltung, float] = {
    EthikNormGeltung.GESPERRT: 0.0,
    EthikNormGeltung.ETHIKNORMATIV: 0.04,
    EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV: 0.08,
}

_TIER_DELTA: dict[EthikNormGeltung, int] = {
    EthikNormGeltung.GESPERRT: 0,
    EthikNormGeltung.ETHIKNORMATIV: 1,
    EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV: 2,
}


@dataclass(frozen=True)
class EthikNormEintrag:
    norm_id: str
    ethik_norm_typ: EthikNormTyp
    prozedur: EthikNormProzedur
    geltung: EthikNormGeltung
    ethik_norm_weight: float
    ethik_norm_tier: int
    canonical: bool
    ethik_norm_ids: tuple[str, ...]
    ethik_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class EthikNormSatz:
    norm_id: str
    meta_ethik_senat: MetaEthikSenat
    normen: tuple[EthikNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is EthikNormGeltung.GESPERRT)

    @property
    def ethiknormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is EthikNormGeltung.ETHIKNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is EthikNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is EthikNormGeltung.ETHIKNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-ethiknormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-ethiknormativ")


def build_ethik_norm(
    meta_ethik_senat: MetaEthikSenat | None = None,
    *,
    norm_id: str = "ethik-norm",
) -> EthikNormSatz:
    if meta_ethik_senat is None:
        meta_ethik_senat = build_meta_ethik_senat(senat_id=f"{norm_id}-senat")

    normen: list[EthikNormEintrag] = []
    for parent_norm in meta_ethik_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.meta_ethik_senat_id.removeprefix(f'{meta_ethik_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.meta_ethik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.meta_ethik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EthikNormGeltung.GRUNDLEGEND_ETHIKNORMATIV)
        normen.append(
            EthikNormEintrag(
                norm_id=new_id,
                ethik_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                ethik_norm_weight=new_weight,
                ethik_norm_tier=new_tier,
                canonical=is_canonical,
                ethik_norm_ids=parent_norm.meta_ethik_ids + (new_id,),
                ethik_norm_tags=parent_norm.meta_ethik_tags + (f"ethik-norm:{new_geltung.value}",),
            )
        )
    return EthikNormSatz(
        norm_id=norm_id,
        meta_ethik_senat=meta_ethik_senat,
        normen=tuple(normen),
    )
