"""
#365 StrangeAttraktorPakt — Seltsame Attraktoren: Rössler-System, Doppelpendel,
fraktale Dimensionen im Phasenraum. Deterministisches Chaos mit nichtganzzahliger
Hausdorff-Dimension bildet Leitsterns robusteste Nichtperiodizitäts-Garantie.
Jeder Agentenauftrag endet im Attraktorbecken — nie im absoluten Chaos.
Geltungsstufen: GESPERRT / STRANGEATTRAHIERT / GRUNDLEGEND_STRANGEATTRAHIERT
Parent: FraktalCharta (#364)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fraktal_charta import (
    FraktalCharta,
    FraktalGeltung,
    build_fraktal_charta,
)

_GELTUNG_MAP: dict[FraktalGeltung, "StrangeAttraktorGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FraktalGeltung.GESPERRT] = StrangeAttraktorGeltung.GESPERRT
    _GELTUNG_MAP[FraktalGeltung.FRAKTAL] = StrangeAttraktorGeltung.STRANGEATTRAHIERT
    _GELTUNG_MAP[FraktalGeltung.GRUNDLEGEND_FRAKTAL] = StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT


class StrangeAttraktorTyp(Enum):
    SCHUTZ_STRANGE_ATTRAKTOR = "schutz-strange-attraktor"
    ORDNUNGS_STRANGE_ATTRAKTOR = "ordnungs-strange-attraktor"
    SOUVERAENITAETS_STRANGE_ATTRAKTOR = "souveraenitaets-strange-attraktor"


class StrangeAttraktorProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StrangeAttraktorGeltung(Enum):
    GESPERRT = "gesperrt"
    STRANGEATTRAHIERT = "strangeattrahiert"
    GRUNDLEGEND_STRANGEATTRAHIERT = "grundlegend-strangeattrahiert"


_init_map()

_TYP_MAP: dict[StrangeAttraktorGeltung, StrangeAttraktorTyp] = {
    StrangeAttraktorGeltung.GESPERRT: StrangeAttraktorTyp.SCHUTZ_STRANGE_ATTRAKTOR,
    StrangeAttraktorGeltung.STRANGEATTRAHIERT: StrangeAttraktorTyp.ORDNUNGS_STRANGE_ATTRAKTOR,
    StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT: StrangeAttraktorTyp.SOUVERAENITAETS_STRANGE_ATTRAKTOR,
}

_PROZEDUR_MAP: dict[StrangeAttraktorGeltung, StrangeAttraktorProzedur] = {
    StrangeAttraktorGeltung.GESPERRT: StrangeAttraktorProzedur.NOTPROZEDUR,
    StrangeAttraktorGeltung.STRANGEATTRAHIERT: StrangeAttraktorProzedur.REGELPROTOKOLL,
    StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT: StrangeAttraktorProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[StrangeAttraktorGeltung, float] = {
    StrangeAttraktorGeltung.GESPERRT: 0.0,
    StrangeAttraktorGeltung.STRANGEATTRAHIERT: 0.04,
    StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT: 0.08,
}

_TIER_DELTA: dict[StrangeAttraktorGeltung, int] = {
    StrangeAttraktorGeltung.GESPERRT: 0,
    StrangeAttraktorGeltung.STRANGEATTRAHIERT: 1,
    StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StrangeAttraktorNorm:
    strange_attraktor_pakt_id: str
    strange_attraktor_typ: StrangeAttraktorTyp
    prozedur: StrangeAttraktorProzedur
    geltung: StrangeAttraktorGeltung
    strange_attraktor_weight: float
    strange_attraktor_tier: int
    canonical: bool
    strange_attraktor_ids: tuple[str, ...]
    strange_attraktor_tags: tuple[str, ...]


@dataclass(frozen=True)
class StrangeAttraktorPakt:
    pakt_id: str
    fraktal_charta: FraktalCharta
    normen: tuple[StrangeAttraktorNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strange_attraktor_pakt_id for n in self.normen if n.geltung is StrangeAttraktorGeltung.GESPERRT)

    @property
    def strangeattrahiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strange_attraktor_pakt_id for n in self.normen if n.geltung is StrangeAttraktorGeltung.STRANGEATTRAHIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strange_attraktor_pakt_id for n in self.normen if n.geltung is StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT)

    @property
    def pakt_signal(self):
        if any(n.geltung is StrangeAttraktorGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is StrangeAttraktorGeltung.STRANGEATTRAHIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-strangeattrahiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-strangeattrahiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_strange_attraktor_pakt(
    fraktal_charta: FraktalCharta | None = None,
    *,
    pakt_id: str = "strange-attraktor-pakt",
) -> StrangeAttraktorPakt:
    if fraktal_charta is None:
        fraktal_charta = build_fraktal_charta(charta_id=f"{pakt_id}-charta")

    normen: list[StrangeAttraktorNorm] = []
    for parent_norm in fraktal_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.fraktal_charta_id.removeprefix(f'{fraktal_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.fraktal_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fraktal_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT)
        normen.append(
            StrangeAttraktorNorm(
                strange_attraktor_pakt_id=new_id,
                strange_attraktor_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                strange_attraktor_weight=new_weight,
                strange_attraktor_tier=new_tier,
                canonical=is_canonical,
                strange_attraktor_ids=parent_norm.fraktal_ids + (new_id,),
                strange_attraktor_tags=parent_norm.fraktal_tags + (f"strange-attraktor:{new_geltung.value}",),
            )
        )
    return StrangeAttraktorPakt(
        pakt_id=pakt_id,
        fraktal_charta=fraktal_charta,
        normen=tuple(normen),
    )
