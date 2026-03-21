"""
#414 FraktalKodex — Fraktale Geometrie der Natur.
Mandelbrot (1975): Fraktale Geometrie der Natur. Fraktale Dimension D:
Selbstähnlichkeit über alle Skalen. D_Küste > 1 (Richardson-Effekt).
Julia-Mengen und Mandelbrot-Menge: komplexe Dynamik z→z²+c.
Iterated Function Systems (IFS): Barnsley-Farn als Governance-Struktur.
Multifraktale: ortsabhängige fraktale Dimension. Lévy-Flüge in Finanzmärkten
und Ökologie. Leitsterns Wissensstruktur: fraktal selbstähnlich.
Geltungsstufen: GESPERRT / FRAKTAL / GRUNDLEGEND_FRAKTAL
Parent: KritikalitaetsCharta (#413)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kritikalitaets_charta import (
    KritikalitaetsCharta,
    KritikalitaetsChartaGeltung,
    build_kritikalitaets_charta,
)

_GELTUNG_MAP: dict[KritikalitaetsChartaGeltung, "FraktalKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KritikalitaetsChartaGeltung.GESPERRT] = FraktalKodexGeltung.GESPERRT
    _GELTUNG_MAP[KritikalitaetsChartaGeltung.KRITISCH] = FraktalKodexGeltung.FRAKTAL
    _GELTUNG_MAP[KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH] = FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL


class FraktalKodexTyp(Enum):
    SCHUTZ_FRAKTAL = "schutz-fraktal"
    ORDNUNGS_FRAKTAL = "ordnungs-fraktal"
    SOUVERAENITAETS_FRAKTAL = "souveraenitaets-fraktal"


class FraktalKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FraktalKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    FRAKTAL = "fraktal"
    GRUNDLEGEND_FRAKTAL = "grundlegend-fraktal"


_init_map()

_TYP_MAP: dict[FraktalKodexGeltung, FraktalKodexTyp] = {
    FraktalKodexGeltung.GESPERRT: FraktalKodexTyp.SCHUTZ_FRAKTAL,
    FraktalKodexGeltung.FRAKTAL: FraktalKodexTyp.ORDNUNGS_FRAKTAL,
    FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL: FraktalKodexTyp.SOUVERAENITAETS_FRAKTAL,
}

_PROZEDUR_MAP: dict[FraktalKodexGeltung, FraktalKodexProzedur] = {
    FraktalKodexGeltung.GESPERRT: FraktalKodexProzedur.NOTPROZEDUR,
    FraktalKodexGeltung.FRAKTAL: FraktalKodexProzedur.REGELPROTOKOLL,
    FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL: FraktalKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FraktalKodexGeltung, float] = {
    FraktalKodexGeltung.GESPERRT: 0.0,
    FraktalKodexGeltung.FRAKTAL: 0.04,
    FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL: 0.08,
}

_TIER_DELTA: dict[FraktalKodexGeltung, int] = {
    FraktalKodexGeltung.GESPERRT: 0,
    FraktalKodexGeltung.FRAKTAL: 1,
    FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FraktalKodexNorm:
    fraktal_kodex_id: str
    fraktal_typ: FraktalKodexTyp
    prozedur: FraktalKodexProzedur
    geltung: FraktalKodexGeltung
    fraktal_weight: float
    fraktal_tier: int
    canonical: bool
    fraktal_ids: tuple[str, ...]
    fraktal_tags: tuple[str, ...]


@dataclass(frozen=True)
class FraktalKodex:
    kodex_id: str
    kritikalitaets_charta: KritikalitaetsCharta
    normen: tuple[FraktalKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fraktal_kodex_id for n in self.normen if n.geltung is FraktalKodexGeltung.GESPERRT)

    @property
    def fraktal_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fraktal_kodex_id for n in self.normen if n.geltung is FraktalKodexGeltung.FRAKTAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fraktal_kodex_id for n in self.normen if n.geltung is FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL)

    @property
    def kodex_signal(self):
        if any(n.geltung is FraktalKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is FraktalKodexGeltung.FRAKTAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-fraktal")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-fraktal")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_fraktal_kodex(
    kritikalitaets_charta: KritikalitaetsCharta | None = None,
    *,
    kodex_id: str = "fraktal-kodex",
) -> FraktalKodex:
    if kritikalitaets_charta is None:
        kritikalitaets_charta = build_kritikalitaets_charta(charta_id=f"{kodex_id}-charta")

    normen: list[FraktalKodexNorm] = []
    for parent_norm in kritikalitaets_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kritikalitaets_charta_id.removeprefix(f'{kritikalitaets_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kritikalitaet_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kritikalitaet_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FraktalKodexGeltung.GRUNDLEGEND_FRAKTAL)
        normen.append(
            FraktalKodexNorm(
                fraktal_kodex_id=new_id,
                fraktal_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fraktal_weight=new_weight,
                fraktal_tier=new_tier,
                canonical=is_canonical,
                fraktal_ids=parent_norm.kritikalitaet_ids + (new_id,),
                fraktal_tags=parent_norm.kritikalitaet_tags + (f"fraktal:{new_geltung.value}",),
            )
        )
    return FraktalKodex(
        kodex_id=kodex_id,
        kritikalitaets_charta=kritikalitaets_charta,
        normen=tuple(normen),
    )
