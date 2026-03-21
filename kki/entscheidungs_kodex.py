"""
#394 EntscheidungsKodex — Kahneman & Tversky: Dual-Process Theory (2011).
System 1: schnell, automatisch, assoziativ, heuristisch, emotional, unbewusst.
System 2: langsam, deliberat, analytisch, regelbasiert, bewusst, aufwändig.
Prospect Theory (1979): Verlustaversion — Verluste wiegen 2x schwerer als Gewinne.
Somatic Marker Hypothesis (Damasio 1994): somatische Marker = emotionale Signale
als Entscheidungsheuristiken. Iowa Gambling Task: vmPFC-Patienten verlieren trotz
Wissen. Leitsterns Entscheidungsarchitektur: System 1 liefert schnelle Heuristiken,
System 2 überwacht und korrigiert — Alignment durch rationale Kontrolle.
Geltungsstufen: GESPERRT / ENTSCHEIDUNGSAKTIV / GRUNDLEGEND_ENTSCHEIDUNGSAKTIV
Parent: AufmerksamkeitsCharta (#393)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .aufmerksamkeits_charta import (
    AufmerksamkeitsCharta,
    AufmerksamkeitsGeltung,
    build_aufmerksamkeits_charta,
)

_GELTUNG_MAP: dict[AufmerksamkeitsGeltung, "EntscheidungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AufmerksamkeitsGeltung.GESPERRT] = EntscheidungsGeltung.GESPERRT
    _GELTUNG_MAP[AufmerksamkeitsGeltung.AUFMERKSAMKEITSGELEITET] = EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV
    _GELTUNG_MAP[AufmerksamkeitsGeltung.GRUNDLEGEND_AUFMERKSAMKEITSGELEITET] = EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV


class EntscheidungsTyp(Enum):
    SCHUTZ_ENTSCHEIDUNG = "schutz-entscheidung"
    ORDNUNGS_ENTSCHEIDUNG = "ordnungs-entscheidung"
    SOUVERAENITAETS_ENTSCHEIDUNG = "souveraenitaets-entscheidung"


class EntscheidungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EntscheidungsGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTSCHEIDUNGSAKTIV = "entscheidungsaktiv"
    GRUNDLEGEND_ENTSCHEIDUNGSAKTIV = "grundlegend-entscheidungsaktiv"


_init_map()

_TYP_MAP: dict[EntscheidungsGeltung, EntscheidungsTyp] = {
    EntscheidungsGeltung.GESPERRT: EntscheidungsTyp.SCHUTZ_ENTSCHEIDUNG,
    EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV: EntscheidungsTyp.ORDNUNGS_ENTSCHEIDUNG,
    EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV: EntscheidungsTyp.SOUVERAENITAETS_ENTSCHEIDUNG,
}

_PROZEDUR_MAP: dict[EntscheidungsGeltung, EntscheidungsProzedur] = {
    EntscheidungsGeltung.GESPERRT: EntscheidungsProzedur.NOTPROZEDUR,
    EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV: EntscheidungsProzedur.REGELPROTOKOLL,
    EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV: EntscheidungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EntscheidungsGeltung, float] = {
    EntscheidungsGeltung.GESPERRT: 0.0,
    EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV: 0.04,
    EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV: 0.08,
}

_TIER_DELTA: dict[EntscheidungsGeltung, int] = {
    EntscheidungsGeltung.GESPERRT: 0,
    EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV: 1,
    EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntscheidungsNorm:
    entscheidungs_kodex_id: str
    entscheidungs_typ: EntscheidungsTyp
    prozedur: EntscheidungsProzedur
    geltung: EntscheidungsGeltung
    entscheidungs_weight: float
    entscheidungs_tier: int
    canonical: bool
    entscheidungs_ids: tuple[str, ...]
    entscheidungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntscheidungsKodex:
    kodex_id: str
    aufmerksamkeits_charta: AufmerksamkeitsCharta
    normen: tuple[EntscheidungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungs_kodex_id for n in self.normen if n.geltung is EntscheidungsGeltung.GESPERRT)

    @property
    def entscheidungsaktiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungs_kodex_id for n in self.normen if n.geltung is EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungs_kodex_id for n in self.normen if n.geltung is EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV)

    @property
    def kodex_signal(self):
        if any(n.geltung is EntscheidungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is EntscheidungsGeltung.ENTSCHEIDUNGSAKTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-entscheidungsaktiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-entscheidungsaktiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_entscheidungs_kodex(
    aufmerksamkeits_charta: AufmerksamkeitsCharta | None = None,
    *,
    kodex_id: str = "entscheidungs-kodex",
) -> EntscheidungsKodex:
    if aufmerksamkeits_charta is None:
        aufmerksamkeits_charta = build_aufmerksamkeits_charta(charta_id=f"{kodex_id}-charta")

    normen: list[EntscheidungsNorm] = []
    for parent_norm in aufmerksamkeits_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.aufmerksamkeits_charta_id.removeprefix(f'{aufmerksamkeits_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.aufmerksamkeits_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.aufmerksamkeits_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntscheidungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSAKTIV)
        normen.append(
            EntscheidungsNorm(
                entscheidungs_kodex_id=new_id,
                entscheidungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                entscheidungs_weight=new_weight,
                entscheidungs_tier=new_tier,
                canonical=is_canonical,
                entscheidungs_ids=parent_norm.aufmerksamkeits_ids + (new_id,),
                entscheidungs_tags=parent_norm.aufmerksamkeits_tags + (f"entscheidung:{new_geltung.value}",),
            )
        )
    return EntscheidungsKodex(
        kodex_id=kodex_id,
        aufmerksamkeits_charta=aufmerksamkeits_charta,
        normen=tuple(normen),
    )
