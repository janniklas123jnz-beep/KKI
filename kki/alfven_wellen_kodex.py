"""
#354 AlfvenWellenKodex — Alfvén-Wellen: kohärente MHD-Transversalwellen, die
sich mit v_A = B/√(μ₀ρ) entlang des Magnetfeldes ausbreiten. Governance-
Entscheidungen breiten sich wie Alfvén-Wellen verlustfrei durch den Schwarm
aus — Informationsübertragung ohne Dissipation.
Geltungsstufen: GESPERRT / ALFVENWELLIG / GRUNDLEGEND_ALFVENWELLIG
Parent: DebyeAbschirmungCharta (#353)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .debye_abschirmung_charta import (
    DebyeAbschirmungCharta,
    DebyeAbschirmungGeltung,
    build_debye_abschirmung_charta,
)

_GELTUNG_MAP: dict[DebyeAbschirmungGeltung, "AlfvenWellenGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DebyeAbschirmungGeltung.GESPERRT] = AlfvenWellenGeltung.GESPERRT
    _GELTUNG_MAP[DebyeAbschirmungGeltung.DEBYEABGESCHIRMT] = AlfvenWellenGeltung.ALFVENWELLIG
    _GELTUNG_MAP[DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT] = AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG


class AlfvenWellenTyp(Enum):
    SCHUTZ_ALFVEN_WELLEN = "schutz-alfven-wellen"
    ORDNUNGS_ALFVEN_WELLEN = "ordnungs-alfven-wellen"
    SOUVERAENITAETS_ALFVEN_WELLEN = "souveraenitaets-alfven-wellen"


class AlfvenWellenProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AlfvenWellenGeltung(Enum):
    GESPERRT = "gesperrt"
    ALFVENWELLIG = "alfvenwellig"
    GRUNDLEGEND_ALFVENWELLIG = "grundlegend-alfvenwellig"


_init_map()

_TYP_MAP: dict[AlfvenWellenGeltung, AlfvenWellenTyp] = {
    AlfvenWellenGeltung.GESPERRT: AlfvenWellenTyp.SCHUTZ_ALFVEN_WELLEN,
    AlfvenWellenGeltung.ALFVENWELLIG: AlfvenWellenTyp.ORDNUNGS_ALFVEN_WELLEN,
    AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG: AlfvenWellenTyp.SOUVERAENITAETS_ALFVEN_WELLEN,
}

_PROZEDUR_MAP: dict[AlfvenWellenGeltung, AlfvenWellenProzedur] = {
    AlfvenWellenGeltung.GESPERRT: AlfvenWellenProzedur.NOTPROZEDUR,
    AlfvenWellenGeltung.ALFVENWELLIG: AlfvenWellenProzedur.REGELPROTOKOLL,
    AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG: AlfvenWellenProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AlfvenWellenGeltung, float] = {
    AlfvenWellenGeltung.GESPERRT: 0.0,
    AlfvenWellenGeltung.ALFVENWELLIG: 0.04,
    AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG: 0.08,
}

_TIER_DELTA: dict[AlfvenWellenGeltung, int] = {
    AlfvenWellenGeltung.GESPERRT: 0,
    AlfvenWellenGeltung.ALFVENWELLIG: 1,
    AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AlfvenWellenNorm:
    alfven_wellen_kodex_id: str
    alfven_wellen_typ: AlfvenWellenTyp
    prozedur: AlfvenWellenProzedur
    geltung: AlfvenWellenGeltung
    alfven_wellen_weight: float
    alfven_wellen_tier: int
    canonical: bool
    alfven_wellen_ids: tuple[str, ...]
    alfven_wellen_tags: tuple[str, ...]


@dataclass(frozen=True)
class AlfvenWellenKodex:
    kodex_id: str
    debye_abschirmung_charta: DebyeAbschirmungCharta
    normen: tuple[AlfvenWellenNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.alfven_wellen_kodex_id for n in self.normen if n.geltung is AlfvenWellenGeltung.GESPERRT)

    @property
    def alfvenwellig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.alfven_wellen_kodex_id for n in self.normen if n.geltung is AlfvenWellenGeltung.ALFVENWELLIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.alfven_wellen_kodex_id for n in self.normen if n.geltung is AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG)

    @property
    def kodex_signal(self):
        if any(n.geltung is AlfvenWellenGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is AlfvenWellenGeltung.ALFVENWELLIG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-alfvenwellig")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-alfvenwellig")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_alfven_wellen_kodex(
    debye_abschirmung_charta: DebyeAbschirmungCharta | None = None,
    *,
    kodex_id: str = "alfven-wellen-kodex",
) -> AlfvenWellenKodex:
    if debye_abschirmung_charta is None:
        debye_abschirmung_charta = build_debye_abschirmung_charta(charta_id=f"{kodex_id}-charta")

    normen: list[AlfvenWellenNorm] = []
    for parent_norm in debye_abschirmung_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.debye_abschirmung_charta_id.removeprefix(f'{debye_abschirmung_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.debye_abschirmung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.debye_abschirmung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AlfvenWellenGeltung.GRUNDLEGEND_ALFVENWELLIG)
        normen.append(
            AlfvenWellenNorm(
                alfven_wellen_kodex_id=new_id,
                alfven_wellen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                alfven_wellen_weight=new_weight,
                alfven_wellen_tier=new_tier,
                canonical=is_canonical,
                alfven_wellen_ids=parent_norm.debye_abschirmung_ids + (new_id,),
                alfven_wellen_tags=parent_norm.debye_abschirmung_tags + (f"alfven-wellen:{new_geltung.value}",),
            )
        )
    return AlfvenWellenKodex(
        kodex_id=kodex_id,
        debye_abschirmung_charta=debye_abschirmung_charta,
        normen=tuple(normen),
    )
