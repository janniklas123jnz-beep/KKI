"""
#424 RegelkreisKodex — Regelungstechnik: PID-Regler und Stabilitätskriterien.
PID-Regler: u(t) = Kp·e + Ki·∫e dt + Kd·de/dt — robusteste Regelung der Praxis.
Nyquist-Stabilitätskriterium (1932): Frequenzgang-Analyse.
Kalman-Filter (1960): optimale Zustandsschätzung. LQR: optimale Regelung.
Leitsterns Stabilitätszertifikat: geregelt, stabil, optimal.
Geltungsstufen: GESPERRT / GEREGELT / GRUNDLEGEND_GEREGELT
Parent: KybernetikCharta (#423)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kybernetik_charta import (
    KybernetikCharta,
    KybernetikChartaGeltung,
    build_kybernetik_charta,
)

_GELTUNG_MAP: dict[KybernetikChartaGeltung, "RegelkreisKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KybernetikChartaGeltung.GESPERRT] = RegelkreisKodexGeltung.GESPERRT
    _GELTUNG_MAP[KybernetikChartaGeltung.KYBERNETISCH] = RegelkreisKodexGeltung.GEREGELT
    _GELTUNG_MAP[KybernetikChartaGeltung.GRUNDLEGEND_KYBERNETISCH] = RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT


class RegelkreisKodexTyp(Enum):
    SCHUTZ_REGELKREIS = "schutz-regelkreis"
    ORDNUNGS_REGELKREIS = "ordnungs-regelkreis"
    SOUVERAENITAETS_REGELKREIS = "souveraenitaets-regelkreis"


class RegelkreisKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RegelkreisKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    GEREGELT = "geregelt"
    GRUNDLEGEND_GEREGELT = "grundlegend-geregelt"


_init_map()

_TYP_MAP: dict[RegelkreisKodexGeltung, RegelkreisKodexTyp] = {
    RegelkreisKodexGeltung.GESPERRT: RegelkreisKodexTyp.SCHUTZ_REGELKREIS,
    RegelkreisKodexGeltung.GEREGELT: RegelkreisKodexTyp.ORDNUNGS_REGELKREIS,
    RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT: RegelkreisKodexTyp.SOUVERAENITAETS_REGELKREIS,
}

_PROZEDUR_MAP: dict[RegelkreisKodexGeltung, RegelkreisKodexProzedur] = {
    RegelkreisKodexGeltung.GESPERRT: RegelkreisKodexProzedur.NOTPROZEDUR,
    RegelkreisKodexGeltung.GEREGELT: RegelkreisKodexProzedur.REGELPROTOKOLL,
    RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT: RegelkreisKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RegelkreisKodexGeltung, float] = {
    RegelkreisKodexGeltung.GESPERRT: 0.0,
    RegelkreisKodexGeltung.GEREGELT: 0.04,
    RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT: 0.08,
}

_TIER_DELTA: dict[RegelkreisKodexGeltung, int] = {
    RegelkreisKodexGeltung.GESPERRT: 0,
    RegelkreisKodexGeltung.GEREGELT: 1,
    RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegelkreisKodexNorm:
    regelkreis_kodex_id: str
    regelkreis_typ: RegelkreisKodexTyp
    prozedur: RegelkreisKodexProzedur
    geltung: RegelkreisKodexGeltung
    regelkreis_weight: float
    regelkreis_tier: int
    canonical: bool
    regelkreis_ids: tuple[str, ...]
    regelkreis_tags: tuple[str, ...]


@dataclass(frozen=True)
class RegelkreisKodex:
    kodex_id: str
    kybernetik_charta: KybernetikCharta
    normen: tuple[RegelkreisKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.regelkreis_kodex_id for n in self.normen if n.geltung is RegelkreisKodexGeltung.GESPERRT)

    @property
    def geregelt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.regelkreis_kodex_id for n in self.normen if n.geltung is RegelkreisKodexGeltung.GEREGELT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.regelkreis_kodex_id for n in self.normen if n.geltung is RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT)

    @property
    def kodex_signal(self):
        if any(n.geltung is RegelkreisKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is RegelkreisKodexGeltung.GEREGELT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-geregelt")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-geregelt")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_regelkreis_kodex(
    kybernetik_charta: KybernetikCharta | None = None,
    *,
    kodex_id: str = "regelkreis-kodex",
) -> RegelkreisKodex:
    if kybernetik_charta is None:
        kybernetik_charta = build_kybernetik_charta(charta_id=f"{kodex_id}-charta")

    normen: list[RegelkreisKodexNorm] = []
    for parent_norm in kybernetik_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kybernetik_charta_id.removeprefix(f'{kybernetik_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kybernetik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kybernetik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT)
        normen.append(
            RegelkreisKodexNorm(
                regelkreis_kodex_id=new_id,
                regelkreis_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                regelkreis_weight=new_weight,
                regelkreis_tier=new_tier,
                canonical=is_canonical,
                regelkreis_ids=parent_norm.kybernetik_ids + (new_id,),
                regelkreis_tags=parent_norm.kybernetik_tags + (f"regelkreis-kodex:{new_geltung.value}",),
            )
        )
    return RegelkreisKodex(
        kodex_id=kodex_id,
        kybernetik_charta=kybernetik_charta,
        normen=tuple(normen),
    )
