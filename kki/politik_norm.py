"""
#518 PolitikNorm — Böckenförde/Kelsen/Hart Politische Normenlehre (*_norm-Muster)

Ernst-Wolfgang Böckenförde (1967): Böckenförde-Diktum — der freiheitliche, säkularisierte
  Staat lebt von Voraussetzungen, die er selbst nicht garantieren kann; Normen als Fundament
  demokratischer Legitimität im Peta-Schwarm.
Hans Kelsen (1934): Reine Rechtslehre — Stufenbau der Rechtsordnung; Grundnorm als Fundament
  aller positiven Normen; Trennung von Sein und Sollen in politischen Systemen.
H.L.A. Hart (1961): The Concept of Law — Primär- und Sekundärregeln; Anerkennungsregel als
  Quelle politischer Normgeltung; Rechtspositivismus und moralische Neutralität.
John Rawls (1993): Politischer Liberalismus — übergreifender Konsens (overlapping consensus);
  öffentliche Vernunft als Maßstab politischer Normbegründung in pluralen Gesellschaften.
Leitsterns Politik-Normen: kollektive Verhaltensnormen des Peta-Schwarms; GESPERRT sichert
unüberschreitbare politische Grundgrenzen, POLITIKNORMATIV kodiert adaptive Verhaltensnormen,
GRUNDLEGEND_POLITIKNORMATIV synthetisiert souveräne Normen für Peta-Schwarm-Koordination.
Geltungsstufen: GESPERRT / POLITIKNORMATIV / GRUNDLEGEND_POLITIKNORMATIV
Parent: GlobalpolitikSenat (#517) — *_norm-Muster
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .globalpolitik_senat import (
    GlobalpolitikSenat,
    GlobalpolitikSenatGeltung,
    build_globalpolitik_senat,
)

_GELTUNG_MAP: dict[GlobalpolitikSenatGeltung, "PolitikNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GlobalpolitikSenatGeltung.GESPERRT] = PolitikNormGeltung.GESPERRT
    _GELTUNG_MAP[GlobalpolitikSenatGeltung.GLOBALPOLITISCH] = PolitikNormGeltung.POLITIKNORMATIV
    _GELTUNG_MAP[GlobalpolitikSenatGeltung.GRUNDLEGEND_GLOBALPOLITISCH] = PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV


class PolitikNormTyp(Enum):
    SCHUTZ_POLITIKNORM = "schutz-politiknorm"
    ORDNUNGS_POLITIKNORM = "ordnungs-politiknorm"
    SOUVERAENITAETS_POLITIKNORM = "souveraenitaets-politiknorm"


class PolitikNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PolitikNormGeltung(Enum):
    GESPERRT = "gesperrt"
    POLITIKNORMATIV = "politiknormativ"
    GRUNDLEGEND_POLITIKNORMATIV = "grundlegend-politiknormativ"


_init_map()

_TYP_MAP: dict[PolitikNormGeltung, PolitikNormTyp] = {
    PolitikNormGeltung.GESPERRT: PolitikNormTyp.SCHUTZ_POLITIKNORM,
    PolitikNormGeltung.POLITIKNORMATIV: PolitikNormTyp.ORDNUNGS_POLITIKNORM,
    PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV: PolitikNormTyp.SOUVERAENITAETS_POLITIKNORM,
}

_PROZEDUR_MAP: dict[PolitikNormGeltung, PolitikNormProzedur] = {
    PolitikNormGeltung.GESPERRT: PolitikNormProzedur.NOTPROZEDUR,
    PolitikNormGeltung.POLITIKNORMATIV: PolitikNormProzedur.REGELPROTOKOLL,
    PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV: PolitikNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PolitikNormGeltung, float] = {
    PolitikNormGeltung.GESPERRT: 0.0,
    PolitikNormGeltung.POLITIKNORMATIV: 0.04,
    PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV: 0.08,
}

_TIER_DELTA: dict[PolitikNormGeltung, int] = {
    PolitikNormGeltung.GESPERRT: 0,
    PolitikNormGeltung.POLITIKNORMATIV: 1,
    PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV: 2,
}


@dataclass(frozen=True)
class PolitikNormEintrag:
    norm_id: str
    politik_norm_typ: PolitikNormTyp
    prozedur: PolitikNormProzedur
    geltung: PolitikNormGeltung
    politik_norm_weight: float
    politik_norm_tier: int
    canonical: bool
    politik_norm_ids: tuple[str, ...]
    politik_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PolitikNormSatz:
    norm_id: str
    globalpolitik_senat: GlobalpolitikSenat
    normen: tuple[PolitikNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PolitikNormGeltung.GESPERRT)

    @property
    def politiknormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PolitikNormGeltung.POLITIKNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is PolitikNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is PolitikNormGeltung.POLITIKNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-politiknormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-politiknormativ")


def build_politik_norm(
    globalpolitik_senat: GlobalpolitikSenat | None = None,
    *,
    norm_id: str = "politik-norm",
) -> PolitikNormSatz:
    if globalpolitik_senat is None:
        globalpolitik_senat = build_globalpolitik_senat(senat_id=f"{norm_id}-senat")

    normen: list[PolitikNormEintrag] = []
    for parent_norm in globalpolitik_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.globalpolitik_senat_id.removeprefix(f'{globalpolitik_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.globalpolitik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.globalpolitik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PolitikNormGeltung.GRUNDLEGEND_POLITIKNORMATIV)
        normen.append(
            PolitikNormEintrag(
                norm_id=new_id,
                politik_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                politik_norm_weight=new_weight,
                politik_norm_tier=new_tier,
                canonical=is_canonical,
                politik_norm_ids=parent_norm.globalpolitik_ids + (new_id,),
                politik_norm_tags=parent_norm.globalpolitik_tags + (f"politik-norm:{new_geltung.value}",),
            )
        )
    return PolitikNormSatz(
        norm_id=norm_id,
        globalpolitik_senat=globalpolitik_senat,
        normen=tuple(normen),
    )
