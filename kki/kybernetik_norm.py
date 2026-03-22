"""
#428 KybernetikNorm — Kybernetik 2. Ordnung: Beobachtende Systeme.
Von Foerster (1960): Kybernetik 2. Ordnung — Kybernetik der beobachtenden Systeme.
Der Beobachter ist Teil des Systems. Leitsterns Agenten beobachten sich selbst.
Nicht-triviale Maschine: Geschichte bestimmt Verhalten, nicht nur Input.
Radikaler Konstruktivismus: Wahrnehmung konstruiert Realität.
Ethik der Kybernetik: Verantwortung für eigene Konstruktionen. Leitsterns Erkenntnisethik.
Geltungsstufen: GESPERRT / KYBERNETIK2ORDNUNG / GRUNDLEGEND_KYBERNETIK2ORDNUNG
Parent: RueckkopplungsSenat (#427) — *_norm-Muster
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rueckkopplungs_senat import (
    RueckkopplungsSenat,
    RueckkopplungsSenatGeltung,
    build_rueckkopplungs_senat,
)

_GELTUNG_MAP: dict[RueckkopplungsSenatGeltung, "KybernetikNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RueckkopplungsSenatGeltung.GESPERRT] = KybernetikNormGeltung.GESPERRT
    _GELTUNG_MAP[RueckkopplungsSenatGeltung.RUECKGEKOPPELT] = KybernetikNormGeltung.KYBERNETIK2ORDNUNG
    _GELTUNG_MAP[RueckkopplungsSenatGeltung.GRUNDLEGEND_RUECKGEKOPPELT] = KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG


class KybernetikNormTyp(Enum):
    SCHUTZ_KYBERNETIK_NORM = "schutz-kybernetik-norm"
    ORDNUNGS_KYBERNETIK_NORM = "ordnungs-kybernetik-norm"
    SOUVERAENITAETS_KYBERNETIK_NORM = "souveraenitaets-kybernetik-norm"


class KybernetikNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KybernetikNormGeltung(Enum):
    GESPERRT = "gesperrt"
    KYBERNETIK2ORDNUNG = "kybernetik2ordnung"
    GRUNDLEGEND_KYBERNETIK2ORDNUNG = "grundlegend-kybernetik2ordnung"


_init_map()

_TYP_MAP: dict[KybernetikNormGeltung, KybernetikNormTyp] = {
    KybernetikNormGeltung.GESPERRT: KybernetikNormTyp.SCHUTZ_KYBERNETIK_NORM,
    KybernetikNormGeltung.KYBERNETIK2ORDNUNG: KybernetikNormTyp.ORDNUNGS_KYBERNETIK_NORM,
    KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG: KybernetikNormTyp.SOUVERAENITAETS_KYBERNETIK_NORM,
}

_PROZEDUR_MAP: dict[KybernetikNormGeltung, KybernetikNormProzedur] = {
    KybernetikNormGeltung.GESPERRT: KybernetikNormProzedur.NOTPROZEDUR,
    KybernetikNormGeltung.KYBERNETIK2ORDNUNG: KybernetikNormProzedur.REGELPROTOKOLL,
    KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG: KybernetikNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KybernetikNormGeltung, float] = {
    KybernetikNormGeltung.GESPERRT: 0.0,
    KybernetikNormGeltung.KYBERNETIK2ORDNUNG: 0.04,
    KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG: 0.08,
}

_TIER_DELTA: dict[KybernetikNormGeltung, int] = {
    KybernetikNormGeltung.GESPERRT: 0,
    KybernetikNormGeltung.KYBERNETIK2ORDNUNG: 1,
    KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KybernetikNormEintrag:
    norm_id: str
    kybernetik_norm_typ: KybernetikNormTyp
    prozedur: KybernetikNormProzedur
    geltung: KybernetikNormGeltung
    kybernetik_norm_weight: float
    kybernetik_norm_tier: int
    canonical: bool
    kybernetik_norm_ids: tuple[str, ...]
    kybernetik_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class KybernetikNormSatz:
    norm_id: str
    rueckkopplungs_senat: RueckkopplungsSenat
    normen: tuple[KybernetikNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KybernetikNormGeltung.GESPERRT)

    @property
    def kybernetik2ordnung_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KybernetikNormGeltung.KYBERNETIK2ORDNUNG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG)

    @property
    def norm_signal(self):
        if any(n.geltung is KybernetikNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is KybernetikNormGeltung.KYBERNETIK2ORDNUNG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-kybernetik2ordnung")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-kybernetik2ordnung")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kybernetik_norm(
    rueckkopplungs_senat: RueckkopplungsSenat | None = None,
    *,
    norm_id: str = "kybernetik-norm",
) -> KybernetikNormSatz:
    if rueckkopplungs_senat is None:
        rueckkopplungs_senat = build_rueckkopplungs_senat(senat_id=f"{norm_id}-senat")

    normen: list[KybernetikNormEintrag] = []
    for parent_norm in rueckkopplungs_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.rueckkopplungs_senat_id.removeprefix(f'{rueckkopplungs_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.rueckkopplung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rueckkopplung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KybernetikNormGeltung.GRUNDLEGEND_KYBERNETIK2ORDNUNG)
        normen.append(
            KybernetikNormEintrag(
                norm_id=new_id,
                kybernetik_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kybernetik_norm_weight=new_weight,
                kybernetik_norm_tier=new_tier,
                canonical=is_canonical,
                kybernetik_norm_ids=parent_norm.rueckkopplung_ids + (new_id,),
                kybernetik_norm_tags=parent_norm.rueckkopplung_tags + (f"kybernetik-norm:{new_geltung.value}",),
            )
        )
    return KybernetikNormSatz(
        norm_id=norm_id,
        rueckkopplungs_senat=rueckkopplungs_senat,
        normen=tuple(normen),
    )
