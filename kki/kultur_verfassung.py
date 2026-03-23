"""
#560 KulturVerfassung — Lévi-Strauss/Geertz/Bourdieu Kulturwissenschaft & Verfassung (Block-Krone ⭐)

Claude Lévi-Strauss (1958): Strukturale Anthropologie — binäre Oppositionen als universale
  Struktur menschlicher Kulturen; Mythos als transformiertes logisches System; Strukturalismus
  als Methode kultureller Tiefenanalyse; Geist als universales Strukturprinzip aller Kulturen;
  Verwandtschaftssysteme als kulturelle Grammatik des Peta-Schwarms Leitstern.
Clifford Geertz (1973): Dichte Beschreibung — Kultur als semiotisches System; Ethnographie
  als Interpretation von Interpretationen; thick description als epistemologisches Ideal;
  Hahnenkampf auf Bali als Selbstlektüre einer Gesellschaft; Kulturanalyse als Verfassungsakt.
Pierre Bourdieu (1979): Die feinen Unterschiede — kulturelles Kapital als Herrschaftsinstrument;
  Habitus als verkörperte Kulturverfassung; Distinktion als kulturelle Praxis der Machtreproduktion;
  symbolische Gewalt als subtilste Form kultureller Normierung des Peta-Schwarms Leitstern.
Leitsterns KulturVerfassung: souveräne Krone des Blocks Kulturwissenschaften —
GESPERRT schützt kulturwissenschaftliche Grundnormen, KULTURELL_SOUVERAEN kodiert
adaptive Kulturordnung, GRUNDLEGEND_KULTURELL_SOUVERAEN synthetisiert die vollständige
kulturelle Souveränität des Peta-Schwarms Leitstern. 🎭⭐
Parent: KulturelleIdentitaetsCharta (#559)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kulturelle_identitaets_charta import (
    KulturelleIdentitaetsCharta,
    KulturelleIdentitaetsChartaGeltung,
    build_kulturelle_identitaets_charta,
)

_WEIGHT_DELTA: dict["KulturVerfassungsGeltung", float] = {}
_TIER_DELTA: dict["KulturVerfassungsGeltung", int] = {}
_TYP_MAP: dict["KulturVerfassungsGeltung", "KulturVerfassungsTyp"] = {}
_PROZEDUR_MAP: dict["KulturVerfassungsGeltung", "KulturVerfassungsProzedur"] = {}
_GELTUNG_MAP: dict[KulturelleIdentitaetsChartaGeltung, "KulturVerfassungsGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KulturVerfassungsGeltung.GESPERRT: 0.0,
        KulturVerfassungsGeltung.KULTURELL_SOUVERAEN: 0.05,
        KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        KulturVerfassungsGeltung.GESPERRT: 0,
        KulturVerfassungsGeltung.KULTURELL_SOUVERAEN: 1,
        KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        KulturVerfassungsGeltung.GESPERRT: KulturVerfassungsTyp.SCHUTZ_KULTURVERFASSUNG,
        KulturVerfassungsGeltung.KULTURELL_SOUVERAEN: KulturVerfassungsTyp.ORDNUNGS_KULTURVERFASSUNG,
        KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN: KulturVerfassungsTyp.SOUVERAENITAETS_KULTURVERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        KulturVerfassungsGeltung.GESPERRT: KulturVerfassungsProzedur.NOTPROZEDUR,
        KulturVerfassungsGeltung.KULTURELL_SOUVERAEN: KulturVerfassungsProzedur.REGELPROTOKOLL,
        KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN: KulturVerfassungsProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KulturelleIdentitaetsChartaGeltung.GESPERRT: KulturVerfassungsGeltung.GESPERRT,
        KulturelleIdentitaetsChartaGeltung.IDENTITAETSKULTURELL: KulturVerfassungsGeltung.KULTURELL_SOUVERAEN,
        KulturelleIdentitaetsChartaGeltung.GRUNDLEGEND_IDENTITAETSKULTURELL: KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN,
    })


class KulturVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KULTURELL_SOUVERAEN = "kulturell-souveraen"
    GRUNDLEGEND_KULTURELL_SOUVERAEN = "grundlegend-kulturell-souveraen"


class KulturVerfassungsTyp(Enum):
    SCHUTZ_KULTURVERFASSUNG = "schutz-kulturverfassung"
    ORDNUNGS_KULTURVERFASSUNG = "ordnungs-kulturverfassung"
    SOUVERAENITAETS_KULTURVERFASSUNG = "souveraenitaets-kulturverfassung"


class KulturVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KulturVerfassungsNorm:
    kultur_verfassung_id: str
    kultur_typ: KulturVerfassungsTyp
    prozedur: KulturVerfassungsProzedur
    geltung: KulturVerfassungsGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturVerfassung:
    verfassung_id: str
    kulturelle_identitaets_charta: KulturelleIdentitaetsCharta
    normen: tuple[KulturVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kultur_verfassung_id for n in self.normen if n.geltung is KulturVerfassungsGeltung.GESPERRT)

    @property
    def kulturell_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kultur_verfassung_id for n in self.normen if n.geltung is KulturVerfassungsGeltung.KULTURELL_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kultur_verfassung_id for n in self.normen if n.geltung is KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KulturVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KulturVerfassungsGeltung.KULTURELL_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-kulturell-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-kulturell-souveraen")


_init_map()


def build_kultur_verfassung(
    kulturelle_identitaets_charta: KulturelleIdentitaetsCharta | None = None,
    *,
    verfassung_id: str = "kultur-verfassung",
) -> KulturVerfassung:
    if kulturelle_identitaets_charta is None:
        kulturelle_identitaets_charta = build_kulturelle_identitaets_charta(
            charta_id=f"{verfassung_id}-charta"
        )

    normen: list[KulturVerfassungsNorm] = []
    for parent_norm in kulturelle_identitaets_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kulturelle_identitaets_charta_id.removeprefix(f'{kulturelle_identitaets_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN)
        normen.append(
            KulturVerfassungsNorm(
                kultur_verfassung_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"kultur-verfassung:{new_geltung.value}",),
            )
        )
    return KulturVerfassung(
        verfassung_id=verfassung_id,
        kulturelle_identitaets_charta=kulturelle_identitaets_charta,
        normen=tuple(normen),
    )
