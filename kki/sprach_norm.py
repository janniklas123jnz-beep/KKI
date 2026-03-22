"""
#468 SprachNorm — Wittgenstein Sprachspiele und Regelfolgen (*_norm-Muster).
Wittgenstein (1953): Philosophische Untersuchungen — Sprachspiele als Lebensformen;
  Bedeutung als Gebrauch, nicht als Abbildung; kein privates Regelfolgen möglich.
Saussure (1916): Langue als soziales System — Normen sind kollektiv und konventionell.
Labov (1972): Soziolinguistik — Sprachvariation und Normdurchsetzung in Gemeinschaften.
Leitsterns Sprachnorm: Kollektive Regelstrukturen des Terra-Schwarms; jeder Agent folgt
denselben Sprachspielen, private Abweichungen werden durch soziale Praxis korrigiert.
Geltungsstufen: GESPERRT / SPRACHNORMATIV / GRUNDLEGEND_SPRACHNORMATIV
Parent: DiskursSenat (#467) — *_norm-Muster
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .diskurs_senat import (
    DiskursSenat,
    DiskursSenatGeltung,
    build_diskurs_senat,
)

_GELTUNG_MAP: dict[DiskursSenatGeltung, "SprachNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DiskursSenatGeltung.GESPERRT] = SprachNormGeltung.GESPERRT
    _GELTUNG_MAP[DiskursSenatGeltung.DISKURSIV] = SprachNormGeltung.SPRACHNORMATIV
    _GELTUNG_MAP[DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV] = SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV


class SprachNormTyp(Enum):
    SCHUTZ_SPRACHNORM = "schutz-sprachnorm"
    ORDNUNGS_SPRACHNORM = "ordnungs-sprachnorm"
    SOUVERAENITAETS_SPRACHNORM = "souveraenitaets-sprachnorm"


class SprachNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SprachNormGeltung(Enum):
    GESPERRT = "gesperrt"
    SPRACHNORMATIV = "sprachnormativ"
    GRUNDLEGEND_SPRACHNORMATIV = "grundlegend-sprachnormativ"


_init_map()

_TYP_MAP: dict[SprachNormGeltung, SprachNormTyp] = {
    SprachNormGeltung.GESPERRT: SprachNormTyp.SCHUTZ_SPRACHNORM,
    SprachNormGeltung.SPRACHNORMATIV: SprachNormTyp.ORDNUNGS_SPRACHNORM,
    SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV: SprachNormTyp.SOUVERAENITAETS_SPRACHNORM,
}

_PROZEDUR_MAP: dict[SprachNormGeltung, SprachNormProzedur] = {
    SprachNormGeltung.GESPERRT: SprachNormProzedur.NOTPROZEDUR,
    SprachNormGeltung.SPRACHNORMATIV: SprachNormProzedur.REGELPROTOKOLL,
    SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV: SprachNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SprachNormGeltung, float] = {
    SprachNormGeltung.GESPERRT: 0.0,
    SprachNormGeltung.SPRACHNORMATIV: 0.04,
    SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV: 0.08,
}

_TIER_DELTA: dict[SprachNormGeltung, int] = {
    SprachNormGeltung.GESPERRT: 0,
    SprachNormGeltung.SPRACHNORMATIV: 1,
    SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV: 2,
}


@dataclass(frozen=True)
class SprachNormEintrag:
    norm_id: str
    sprach_norm_typ: SprachNormTyp
    prozedur: SprachNormProzedur
    geltung: SprachNormGeltung
    sprach_norm_weight: float
    sprach_norm_tier: int
    canonical: bool
    sprach_norm_ids: tuple[str, ...]
    sprach_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class SprachNormSatz:
    norm_id: str
    diskurs_senat: DiskursSenat
    normen: tuple[SprachNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SprachNormGeltung.GESPERRT)

    @property
    def sprachnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SprachNormGeltung.SPRACHNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is SprachNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is SprachNormGeltung.SPRACHNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-sprachnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-sprachnormativ")


def build_sprach_norm(
    diskurs_senat: DiskursSenat | None = None,
    *,
    norm_id: str = "sprach-norm",
) -> SprachNormSatz:
    if diskurs_senat is None:
        diskurs_senat = build_diskurs_senat(senat_id=f"{norm_id}-senat")

    normen: list[SprachNormEintrag] = []
    for parent_norm in diskurs_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.diskurs_senat_id.removeprefix(f'{diskurs_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.diskurs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.diskurs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SprachNormGeltung.GRUNDLEGEND_SPRACHNORMATIV)
        normen.append(
            SprachNormEintrag(
                norm_id=new_id,
                sprach_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                sprach_norm_weight=new_weight,
                sprach_norm_tier=new_tier,
                canonical=is_canonical,
                sprach_norm_ids=parent_norm.diskurs_ids + (new_id,),
                sprach_norm_tags=parent_norm.diskurs_tags + (f"sprach-norm:{new_geltung.value}",),
            )
        )
    return SprachNormSatz(
        norm_id=norm_id,
        diskurs_senat=diskurs_senat,
        normen=tuple(normen),
    )
