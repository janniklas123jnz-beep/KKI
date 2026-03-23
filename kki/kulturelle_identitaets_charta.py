"""
#559 KulturelleIdentitaetsCharta — Hall/Butler/Bhabha Kulturelle Identität & Repräsentation

Stuart Hall (1990): Cultural Identity and Diaspora — Kulturelle Identität als Produktion,
  nicht als Sein; Differenz und Hybridität als Kern postkolonialer Identität; Repräsentation
  als Machtfeld; Encoding/Decoding als Kommunikationstheorie des Peta-Schwarms Leitstern.
Judith Butler (1990): Gender Trouble — Performativität als Identitätskonstruktion;
  Identität als wiederholte zitierbare Praxis; Subversion als kulturelle Strategie;
  Dekonstruktion binärer Kategorien als kulturwissenschaftliche Methode des Schwarms.
Homi K. Bhabha (1994): The Location of Culture — Hybridität als dritter Raum;
  Mimikry als koloniale Ambivalenz; Ambiguität als produktive kulturelle Kraft;
  Das Unheimliche als kulturelle Grenzzone zwischen Eigenem und Fremdem des Schwarms.
Leitsterns KulturelleIdentitaetsCharta: identitätskritische Charta des Kulturblocks —
GESPERRT schützt kulturelle Identitätsgrundsätze, IDENTITAETSKULTURELL kodiert adaptive
Repräsentationsordnung, GRUNDLEGEND_IDENTITAETSKULTURELL synthetisiert die volle
kulturelle Identitätscharta des Peta-Schwarms Leitstern. 🎭
Parent: KulturNorm (#558)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kultur_norm import (
    KulturNormSatz,
    KulturNormGeltung,
    build_kultur_norm,
)

_WEIGHT_DELTA: dict["KulturelleIdentitaetsChartaGeltung", float] = {}
_TIER_DELTA: dict["KulturelleIdentitaetsChartaGeltung", int] = {}
_TYP_MAP: dict["KulturelleIdentitaetsChartaGeltung", "KulturelleIdentitaetsChartaTyp"] = {}
_PROZEDUR_MAP: dict["KulturelleIdentitaetsChartaGeltung", "KulturelleIdentitaetsChartaProzedur"] = {}
_GELTUNG_MAP: dict[KulturNormGeltung, "KulturelleIdentitaetsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KulturelleIdentitaetsChartaGeltung.GESPERRT: 0.0,
        KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL: 0.05,
        KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL: 0.1,
    })
    _TIER_DELTA.update({
        KulturelleIdentitaetsChartaGeltung.GESPERRT: 0,
        KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL: 1,
        KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL: 2,
    })
    _TYP_MAP.update({
        KulturelleIdentitaetsChartaGeltung.GESPERRT: KulturelleIdentitaetsChartaTyp.SCHUTZ_IDENTITAETSKULTUR,
        KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL: KulturelleIdentitaetsChartaTyp.ORDNUNGS_IDENTITAETSKULTUR,
        KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL: KulturelleIdentitaetsChartaTyp.SOUVERAENITAETS_IDENTITAETSKULTUR,
    })
    _PROZEDUR_MAP.update({
        KulturelleIdentitaetsChartaGeltung.GESPERRT: KulturelleIdentitaetsChartaProzedur.NOTPROZEDUR,
        KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL: KulturelleIdentitaetsChartaProzedur.REGELPROTOKOLL,
        KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL: KulturelleIdentitaetsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KulturNormGeltung.GESPERRT: KulturelleIdentitaetsChartaGeltung.GESPERRT,
        KulturNormGeltung.KULTURNORMATIV: KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL,
        KulturNormGeltung.GRUNDLEGEND_KULTURNORMATIV: KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL,
    })


class KulturelleIdentitaetsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    IDENTITAETSKULTURELL = "identitaetskulturell"
    GRUNDLEGEND_IDENTITAETSKULTURELL = "grundlegend-identitaetskulturell"


class KulturelleIdentitaetsChartaTyp(Enum):
    SCHUTZ_IDENTITAETSKULTUR = "schutz-identitaetskultur"
    ORDNUNGS_IDENTITAETSKULTUR = "ordnungs-identitaetskultur"
    SOUVERAENITAETS_IDENTITAETSKULTUR = "souveraenitaets-identitaetskultur"


class KulturelleIdentitaetsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KulturelleIdentitaetsChartaNorm:
    kulturelle_identitaets_charta_id: str
    kulturelle_identitaets_typ: KulturelleIdentitaetsChartaTyp
    prozedur: KulturelleIdentitaetsChartaProzedur
    geltung: KulturelleIdentitaetsChartaGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturelleIdentitaetsCharta:
    charta_id: str
    kultur_norm: KulturNormSatz
    normen: tuple[KulturelleIdentitaetsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kulturelle_identitaets_charta_id for n in self.normen if n.geltung is KulturelleIdentitaetsChartaGeltung.GESPERRT)

    @property
    def identitaetskulturell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kulturelle_identitaets_charta_id for n in self.normen if n.geltung is KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kulturelle_identitaets_charta_id for n in self.normen if n.geltung is KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL)

    @property
    def charta_signal(self):
        if any(n.geltung is KulturelleIdentitaetsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-identitaetskulturell")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-identitaetskulturell")


_init_map()


def build_kulturelle_identitaets_charta(
    kultur_norm: KulturNormSatz | None = None,
    *,
    charta_id: str = "kulturelle-identitaets-charta",
) -> KulturelleIdentitaetsCharta:
    if kultur_norm is None:
        kultur_norm = build_kultur_norm(norm_id=f"{charta_id}-norm")

    normen: list[KulturelleIdentitaetsChartaNorm] = []
    for parent_norm in kultur_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{kultur_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL)
        normen.append(
            KulturelleIdentitaetsChartaNorm(
                kulturelle_identitaets_charta_id=new_id,
                kulturelle_identitaets_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_norm_ids + (new_id,),
                kultur_tags=parent_norm.kultur_norm_tags + (f"kulturelle-identitaets-charta:{new_geltung.value}",),
            )
        )
    return KulturelleIdentitaetsCharta(
        charta_id=charta_id,
        kultur_norm=kultur_norm,
        normen=tuple(normen),
    )
