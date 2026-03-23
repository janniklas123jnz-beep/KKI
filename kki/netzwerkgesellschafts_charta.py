"""
#499 NetzwerkgesellschaftsCharta — Castells/Barabási/Watts Netzwerkgesellschaft

Manuel Castells (1996): The Rise of the Network Society — Netzwerklogik als dominantes
  Organisationsprinzip der Informationsgesellschaft; Macht fließt durch Netzwerke; Identität
  als Widerstandsressource gegen netzwerkbasierte Dominanz.
Albert-László Barabási (1999): Emergenz von Scale-Free Networks — Preferential Attachment;
  Hubs und Power-Law-Verteilungen in sozialen Netzwerken; Resilienz vs. Angreifbarkeit.
Duncan Watts & Steven Strogatz (1998): Small-World-Netzwerke — kurze Pfadlängen bei hoher
  Clusterbildung; Six Degrees of Separation als universelles soziales Prinzip.
Mark Granovetter (1973): Stärke schwacher Bindungen — Brückenverbindungen verbreiten
  Information; starke Ties bieten Unterstützung, schwache Ties bieten Reichweite.
Leitsterns Terra-Schwarm nutzt Netzwerkprinzipien: GESPERRT sichert Kerntopologie, NETZWERKGESELLSCHAFTLICH
ermöglicht adaptive Netzwerkkoordination, GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH synthetisiert
skalierungsfreie Schwarmvernetzung für die Peta-Schwarm-Architektur.
Parent: SoziologieNorm (#498)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .soziologie_norm import (
    SoziologieNormSatz,
    SoziologieNormGeltung,
    build_soziologie_norm,
)

_GELTUNG_MAP: dict[SoziologieNormGeltung, "NetzwerkgesellschaftsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SoziologieNormGeltung.GESPERRT] = NetzwerkgesellschaftsChartaGeltung.GESPERRT
    _GELTUNG_MAP[SoziologieNormGeltung.SOZIALNORMATIV] = NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH
    _GELTUNG_MAP[SoziologieNormGeltung.GRUNDLEGEND_SOZIALNORMATIV] = NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH


class NetzwerkgesellschaftsChartaTyp(Enum):
    SCHUTZ_NETZWERKGESELLSCHAFT = "schutz-netzwerkgesellschaft"
    ORDNUNGS_NETZWERKGESELLSCHAFT = "ordnungs-netzwerkgesellschaft"
    SOUVERAENITAETS_NETZWERKGESELLSCHAFT = "souveraenitaets-netzwerkgesellschaft"


class NetzwerkgesellschaftsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NetzwerkgesellschaftsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    NETZWERKGESELLSCHAFTLICH = "netzwerkgesellschaftlich"
    GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH = "grundlegend-netzwerkgesellschaftlich"


_init_map()

_TYP_MAP: dict[NetzwerkgesellschaftsChartaGeltung, NetzwerkgesellschaftsChartaTyp] = {
    NetzwerkgesellschaftsChartaGeltung.GESPERRT: NetzwerkgesellschaftsChartaTyp.SCHUTZ_NETZWERKGESELLSCHAFT,
    NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH: NetzwerkgesellschaftsChartaTyp.ORDNUNGS_NETZWERKGESELLSCHAFT,
    NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH: NetzwerkgesellschaftsChartaTyp.SOUVERAENITAETS_NETZWERKGESELLSCHAFT,
}

_PROZEDUR_MAP: dict[NetzwerkgesellschaftsChartaGeltung, NetzwerkgesellschaftsChartaProzedur] = {
    NetzwerkgesellschaftsChartaGeltung.GESPERRT: NetzwerkgesellschaftsChartaProzedur.NOTPROZEDUR,
    NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH: NetzwerkgesellschaftsChartaProzedur.REGELPROTOKOLL,
    NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH: NetzwerkgesellschaftsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NetzwerkgesellschaftsChartaGeltung, float] = {
    NetzwerkgesellschaftsChartaGeltung.GESPERRT: 0.0,
    NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH: 0.04,
    NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH: 0.08,
}

_TIER_DELTA: dict[NetzwerkgesellschaftsChartaGeltung, int] = {
    NetzwerkgesellschaftsChartaGeltung.GESPERRT: 0,
    NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH: 1,
    NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH: 2,
}


@dataclass(frozen=True)
class NetzwerkgesellschaftsChartaNorm:
    netzwerkgesellschafts_charta_id: str
    netzwerkgesellschafts_typ: NetzwerkgesellschaftsChartaTyp
    prozedur: NetzwerkgesellschaftsChartaProzedur
    geltung: NetzwerkgesellschaftsChartaGeltung
    netzwerkgesellschafts_weight: float
    netzwerkgesellschafts_tier: int
    canonical: bool
    netzwerkgesellschafts_ids: tuple[str, ...]
    netzwerkgesellschafts_tags: tuple[str, ...]


@dataclass(frozen=True)
class NetzwerkgesellschaftsCharta:
    charta_id: str
    soziologie_norm: SoziologieNormSatz
    normen: tuple[NetzwerkgesellschaftsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.netzwerkgesellschafts_charta_id for n in self.normen if n.geltung is NetzwerkgesellschaftsChartaGeltung.GESPERRT)

    @property
    def netzwerkgesellschaftlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.netzwerkgesellschafts_charta_id for n in self.normen if n.geltung is NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.netzwerkgesellschafts_charta_id for n in self.normen if n.geltung is NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH)

    @property
    def charta_signal(self):
        if any(n.geltung is NetzwerkgesellschaftsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is NetzwerkgesellschaftsChartaGeltung.NETZWERKGESELLSCHAFTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-netzwerkgesellschaftlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-netzwerkgesellschaftlich")


def build_netzwerkgesellschafts_charta(
    soziologie_norm: SoziologieNormSatz | None = None,
    *,
    charta_id: str = "netzwerkgesellschafts-charta",
) -> NetzwerkgesellschaftsCharta:
    if soziologie_norm is None:
        soziologie_norm = build_soziologie_norm(norm_id=f"{charta_id}-norm")

    normen: list[NetzwerkgesellschaftsChartaNorm] = []
    for parent_norm in soziologie_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{soziologie_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.soziologie_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.soziologie_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NetzwerkgesellschaftsChartaGeltung.GRUNDLEGEND_NETZWERKGESELLSCHAFTLICH)
        normen.append(
            NetzwerkgesellschaftsChartaNorm(
                netzwerkgesellschafts_charta_id=new_id,
                netzwerkgesellschafts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                netzwerkgesellschafts_weight=new_weight,
                netzwerkgesellschafts_tier=new_tier,
                canonical=is_canonical,
                netzwerkgesellschafts_ids=parent_norm.soziologie_norm_ids + (new_id,),
                netzwerkgesellschafts_tags=parent_norm.soziologie_norm_tags + (f"netzwerkgesellschafts-charta:{new_geltung.value}",),
            )
        )
    return NetzwerkgesellschaftsCharta(
        charta_id=charta_id,
        soziologie_norm=soziologie_norm,
        normen=tuple(normen),
    )
