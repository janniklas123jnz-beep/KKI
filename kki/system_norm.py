"""
#488 SystemNorm — Bateson/Beer/Luhmann Systemische Normen & Varietätskontrolle (*_norm-Muster).
Gregory Bateson (1972): Ökologie des Geistes — systemische Muster verbinden; Differenz als
  Information; doppelte Beschreibung für vollständiges Systemverständnis.
Stafford Beer (1972): Brain of the Firm — Management Kybernetik; Varietätsbalancierung;
  Algedonic Signale für Systemgesundheit des Terra-Schwarms.
Niklas Luhmann (1984): Soziale Systeme — Erwartungsstrukturen als Normen; normative vs.
  kognitive Erwartungen; Enttäuschungsresistenz durch Normierung.
Leitsterns System-Norm: Kollektive Erwartungsstrukturen des Terra-Schwarms; Varietätskontrolle
nach Ashby; normierte Feedback-Schleifen sichern Peta-Schwarm-Stabilität.
Geltungsstufen: GESPERRT / SYSTEMNORMATIV / GRUNDLEGEND_SYSTEMNORMATIV
Parent: ZweiteOrdnungSenat (#487) — *_norm-Muster
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zweite_ordnung_senat import (
    ZweiteOrdnungSenat,
    ZweiteOrdnungSenatGeltung,
    build_zweite_ordnung_senat,
)

_GELTUNG_MAP: dict[ZweiteOrdnungSenatGeltung, "SystemNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ZweiteOrdnungSenatGeltung.GESPERRT] = SystemNormGeltung.GESPERRT
    _GELTUNG_MAP[ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG] = SystemNormGeltung.SYSTEMNORMATIV
    _GELTUNG_MAP[ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG] = SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV


class SystemNormTyp(Enum):
    SCHUTZ_SYSTEMNORM = "schutz-systemnorm"
    ORDNUNGS_SYSTEMNORM = "ordnungs-systemnorm"
    SOUVERAENITAETS_SYSTEMNORM = "souveraenitaets-systemnorm"


class SystemNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SystemNormGeltung(Enum):
    GESPERRT = "gesperrt"
    SYSTEMNORMATIV = "systemnormativ"
    GRUNDLEGEND_SYSTEMNORMATIV = "grundlegend-systemnormativ"


_init_map()

_TYP_MAP: dict[SystemNormGeltung, SystemNormTyp] = {
    SystemNormGeltung.GESPERRT: SystemNormTyp.SCHUTZ_SYSTEMNORM,
    SystemNormGeltung.SYSTEMNORMATIV: SystemNormTyp.ORDNUNGS_SYSTEMNORM,
    SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV: SystemNormTyp.SOUVERAENITAETS_SYSTEMNORM,
}

_PROZEDUR_MAP: dict[SystemNormGeltung, SystemNormProzedur] = {
    SystemNormGeltung.GESPERRT: SystemNormProzedur.NOTPROZEDUR,
    SystemNormGeltung.SYSTEMNORMATIV: SystemNormProzedur.REGELPROTOKOLL,
    SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV: SystemNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SystemNormGeltung, float] = {
    SystemNormGeltung.GESPERRT: 0.0,
    SystemNormGeltung.SYSTEMNORMATIV: 0.04,
    SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV: 0.08,
}

_TIER_DELTA: dict[SystemNormGeltung, int] = {
    SystemNormGeltung.GESPERRT: 0,
    SystemNormGeltung.SYSTEMNORMATIV: 1,
    SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV: 2,
}


@dataclass(frozen=True)
class SystemNormEintrag:
    norm_id: str
    system_norm_typ: SystemNormTyp
    prozedur: SystemNormProzedur
    geltung: SystemNormGeltung
    system_norm_weight: float
    system_norm_tier: int
    canonical: bool
    system_norm_ids: tuple[str, ...]
    system_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class SystemNormSatz:
    norm_id: str
    zweite_ordnung_senat: ZweiteOrdnungSenat
    normen: tuple[SystemNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SystemNormGeltung.GESPERRT)

    @property
    def systemnormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SystemNormGeltung.SYSTEMNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is SystemNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is SystemNormGeltung.SYSTEMNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-systemnormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-systemnormativ")


def build_system_norm(
    zweite_ordnung_senat: ZweiteOrdnungSenat | None = None,
    *,
    norm_id: str = "system-norm",
) -> SystemNormSatz:
    if zweite_ordnung_senat is None:
        zweite_ordnung_senat = build_zweite_ordnung_senat(senat_id=f"{norm_id}-senat")

    normen: list[SystemNormEintrag] = []
    for parent_norm in zweite_ordnung_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.zweite_ordnung_senat_id.removeprefix(f'{zweite_ordnung_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.zweite_ordnung_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.zweite_ordnung_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SystemNormGeltung.GRUNDLEGEND_SYSTEMNORMATIV)
        normen.append(
            SystemNormEintrag(
                norm_id=new_id,
                system_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                system_norm_weight=new_weight,
                system_norm_tier=new_tier,
                canonical=is_canonical,
                system_norm_ids=parent_norm.zweite_ordnung_ids + (new_id,),
                system_norm_tags=parent_norm.zweite_ordnung_tags + (f"system-norm:{new_geltung.value}",),
            )
        )
    return SystemNormSatz(
        norm_id=norm_id,
        zweite_ordnung_senat=zweite_ordnung_senat,
        normen=tuple(normen),
    )
