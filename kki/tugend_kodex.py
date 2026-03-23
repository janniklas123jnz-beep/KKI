"""
#504 TugendKodex — Aristoteles/MacIntyre/Nussbaum Grundlagen der Tugendethik

Aristoteles (350 v. Chr.): Nikomachische Ethik — Eudaimonia als höchstes menschliches Gut;
  Tugend (arete) als stabiler Charakterzug in der Mitte zwischen Extremen; Phronesis
  (praktische Vernunft) als Leitprinzip tugendhaften Handelns; Freundschaft (philia) als
  tugendethische Sozialform; Gewohnheit (ethos) als Quelle des Charakters.
Alasdair MacIntyre (1981): After Virtue — Wiederentdeckung aristotelischer Tugendethik gegen
  modernen Moralemotivismus; narrative Identität: Tugenden nur verständlich im Kontext einer
  Lebensgeschichte und sozialen Praxis; Tradition als Träger moralischer Rationalität.
Martha Nussbaum (1986/1990): Fragility of Goodness / Love's Knowledge — menschliche
  Verletzlichkeit als konstitutiv für Tugend; Fähigkeitenliste als Basis gerechter Gesellschaft;
  Literatur und Emotion als Quellen moralischer Erkenntnis.
Phronesis als Leitprinzip des Peta-Schwarms: GESPERRT sichert tugendhafte Kernnormen,
TUGENDHAFT ermöglicht adaptive Charakterentwicklung über Millionen Agenten,
GRUNDLEGEND_TUGENDHAFT synthetisiert das vollständige Tugendfundament für souveräne
Peta-Schwarm-Souveränität. 🏛️
Parent: GerechtigkeitsCharta (#503)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gerechtigkeits_charta import (
    GerechtigkeitsCharta,
    GerechtigkeitsChartaGeltung,
    build_gerechtigkeits_charta,
)

_GELTUNG_MAP: dict[GerechtigkeitsChartaGeltung, "TugendKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GerechtigkeitsChartaGeltung.GESPERRT] = TugendKodexGeltung.GESPERRT
    _GELTUNG_MAP[GerechtigkeitsChartaGeltung.GERECHTIGKEITLICH] = TugendKodexGeltung.TUGENDHAFT
    _GELTUNG_MAP[GerechtigkeitsChartaGeltung.GRUNDLEGEND_GERECHTIGKEITLICH] = TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT


class TugendKodexTyp(Enum):
    SCHUTZ_TUGEND = "schutz-tugend"
    ORDNUNGS_TUGEND = "ordnungs-tugend"
    SOUVERAENITAETS_TUGEND = "souveraenitaets-tugend"


class TugendKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TugendKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    TUGENDHAFT = "tugendhaft"
    GRUNDLEGEND_TUGENDHAFT = "grundlegend-tugendhaft"


_init_map()

_TYP_MAP: dict[TugendKodexGeltung, TugendKodexTyp] = {
    TugendKodexGeltung.GESPERRT: TugendKodexTyp.SCHUTZ_TUGEND,
    TugendKodexGeltung.TUGENDHAFT: TugendKodexTyp.ORDNUNGS_TUGEND,
    TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT: TugendKodexTyp.SOUVERAENITAETS_TUGEND,
}

_PROZEDUR_MAP: dict[TugendKodexGeltung, TugendKodexProzedur] = {
    TugendKodexGeltung.GESPERRT: TugendKodexProzedur.NOTPROZEDUR,
    TugendKodexGeltung.TUGENDHAFT: TugendKodexProzedur.REGELPROTOKOLL,
    TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT: TugendKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[TugendKodexGeltung, float] = {
    TugendKodexGeltung.GESPERRT: 0.0,
    TugendKodexGeltung.TUGENDHAFT: 0.04,
    TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT: 0.08,
}

_TIER_DELTA: dict[TugendKodexGeltung, int] = {
    TugendKodexGeltung.GESPERRT: 0,
    TugendKodexGeltung.TUGENDHAFT: 1,
    TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT: 2,
}


@dataclass(frozen=True)
class TugendKodexNorm:
    tugend_kodex_id: str
    tugend_typ: TugendKodexTyp
    prozedur: TugendKodexProzedur
    geltung: TugendKodexGeltung
    tugend_weight: float
    tugend_tier: int
    canonical: bool
    tugend_ids: tuple[str, ...]
    tugend_tags: tuple[str, ...]


@dataclass(frozen=True)
class TugendKodex:
    kodex_id: str
    gerechtigkeits_charta: GerechtigkeitsCharta
    normen: tuple[TugendKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.tugend_kodex_id for n in self.normen if n.geltung is TugendKodexGeltung.GESPERRT)

    @property
    def tugendhaft_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.tugend_kodex_id for n in self.normen if n.geltung is TugendKodexGeltung.TUGENDHAFT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.tugend_kodex_id for n in self.normen if n.geltung is TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT)

    @property
    def kodex_signal(self):
        if any(n.geltung is TugendKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is TugendKodexGeltung.TUGENDHAFT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-tugendhaft")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-tugendhaft")


def build_tugend_kodex(
    gerechtigkeits_charta: GerechtigkeitsCharta | None = None,
    *,
    kodex_id: str = "tugend-kodex",
) -> TugendKodex:
    if gerechtigkeits_charta is None:
        gerechtigkeits_charta = build_gerechtigkeits_charta(charta_id=f"{kodex_id}-charta")

    normen: list[TugendKodexNorm] = []
    for parent_norm in gerechtigkeits_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.gerechtigkeits_charta_id.removeprefix(f'{gerechtigkeits_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.gerechtigkeits_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gerechtigkeits_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT)
        normen.append(
            TugendKodexNorm(
                tugend_kodex_id=new_id,
                tugend_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                tugend_weight=new_weight,
                tugend_tier=new_tier,
                canonical=is_canonical,
                tugend_ids=parent_norm.gerechtigkeits_ids + (new_id,),
                tugend_tags=parent_norm.gerechtigkeits_tags + (f"tugend-kodex:{new_geltung.value}",),
            )
        )
    return TugendKodex(
        kodex_id=kodex_id,
        gerechtigkeits_charta=gerechtigkeits_charta,
        normen=tuple(normen),
    )
