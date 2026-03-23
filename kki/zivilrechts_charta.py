"""
#539 ZivilrechtsCharta — Savigny/BGB/Common Law Zivilrecht & Vertragsrecht

Friedrich Carl von Savigny (1814): Vom Beruf unserer Zeit für Gesetzgebung und Rechtswissenschaft —
  Historische Rechtsschule: Recht als Ausdruck des Volksgeistes; organische Rechtsentwicklung;
  Kritik an Kodifikation ohne gewachsene Rechtspraxis; Privatrecht als Kernbereich bürgerlicher Freiheit.
Immanuel Kant (1797): Metaphysik der Sitten — Vertragsrecht als Ausdruck autonomer Willensfreiheit;
  äußere Freiheit als Grundlage des Privatrechts; Eigentum als Erweiterung der Person;
  Zivilrecht als Sphäre gleichberechtigter Freiheitsausübung aller Schwarm-Agenten.
Rudolf von Jhering (1865): Geist des römischen Rechts — Zweck im Recht; Interessenjurisprudenz;
  Recht als Mittel sozialer Zweckverwirklichung; Kampf ums Recht als Bürgerpflicht.
Oliver Wendell Holmes (1897): The Path of the Law — Predictive Theory of Law; Recht als
  Prophezeiung gerichtlicher Entscheidungen; pragmatische Jurisprudenz des Peta-Schwarms.
Leitsterns ZivilrechtsCharta: privatrechtliches Herzstück des Rechtsblocks — GESPERRT schützt
zivilrechtliche Grundfreiheiten, ZIVILRECHTLICH kodiert adaptive Vertragsordnung,
GRUNDLEGEND_ZIVILRECHTLICH synthetisiert die volle zivilrechtliche Charta des Peta-Schwarms. 📜
Parent: RechtsNorm (#538)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechts_norm import (
    RechtsNormSatz,
    RechtsNormGeltung,
    build_rechts_norm,
)

_WEIGHT_DELTA: dict["ZivilrechtsChartaGeltung", float] = {}
_TIER_DELTA: dict["ZivilrechtsChartaGeltung", int] = {}
_TYP_MAP: dict["ZivilrechtsChartaGeltung", "ZivilrechtsChartaTyp"] = {}
_PROZEDUR_MAP: dict["ZivilrechtsChartaGeltung", "ZivilrechtsChartaProzedur"] = {}
_GELTUNG_MAP: dict[RechtsNormGeltung, "ZivilrechtsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ZivilrechtsChartaGeltung.GESPERRT: 0.0,
        ZivilrechtsChartaGeltung.ZIVILRECHTLICH: 0.05,
        ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        ZivilrechtsChartaGeltung.GESPERRT: 0,
        ZivilrechtsChartaGeltung.ZIVILRECHTLICH: 1,
        ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH: 2,
    })
    _TYP_MAP.update({
        ZivilrechtsChartaGeltung.GESPERRT: ZivilrechtsChartaTyp.SCHUTZ_ZIVILRECHT,
        ZivilrechtsChartaGeltung.ZIVILRECHTLICH: ZivilrechtsChartaTyp.ORDNUNGS_ZIVILRECHT,
        ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH: ZivilrechtsChartaTyp.SOUVERAENITAETS_ZIVILRECHT,
    })
    _PROZEDUR_MAP.update({
        ZivilrechtsChartaGeltung.GESPERRT: ZivilrechtsChartaProzedur.NOTPROZEDUR,
        ZivilrechtsChartaGeltung.ZIVILRECHTLICH: ZivilrechtsChartaProzedur.REGELPROTOKOLL,
        ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH: ZivilrechtsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RechtsNormGeltung.GESPERRT: ZivilrechtsChartaGeltung.GESPERRT,
        RechtsNormGeltung.RECHTSNORMATIV: ZivilrechtsChartaGeltung.ZIVILRECHTLICH,
        RechtsNormGeltung.GRUNDLEGEND_RECHTSNORMATIV: ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH,
    })


class ZivilrechtsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    ZIVILRECHTLICH = "zivilrechtlich"
    GRUNDLEGEND_ZIVILRECHTLICH = "grundlegend-zivilrechtlich"


class ZivilrechtsChartaTyp(Enum):
    SCHUTZ_ZIVILRECHT = "schutz-zivilrecht"
    ORDNUNGS_ZIVILRECHT = "ordnungs-zivilrecht"
    SOUVERAENITAETS_ZIVILRECHT = "souveraenitaets-zivilrecht"


class ZivilrechtsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class ZivilrechtsChartaNorm:
    zivilrechts_charta_id: str
    zivilrechts_typ: ZivilrechtsChartaTyp
    prozedur: ZivilrechtsChartaProzedur
    geltung: ZivilrechtsChartaGeltung
    zivilrechts_weight: float
    zivilrechts_tier: int
    canonical: bool
    zivilrechts_ids: tuple[str, ...]
    zivilrechts_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZivilrechtsCharta:
    charta_id: str
    rechts_norm: RechtsNormSatz
    normen: tuple[ZivilrechtsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilrechts_charta_id for n in self.normen if n.geltung is ZivilrechtsChartaGeltung.GESPERRT)

    @property
    def zivilrechtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilrechts_charta_id for n in self.normen if n.geltung is ZivilrechtsChartaGeltung.ZIVILRECHTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zivilrechts_charta_id for n in self.normen if n.geltung is ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH)

    @property
    def charta_signal(self):
        if any(n.geltung is ZivilrechtsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is ZivilrechtsChartaGeltung.ZIVILRECHTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-zivilrechtlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-zivilrechtlich")


_init_map()


def build_zivilrechts_charta(
    rechts_norm: RechtsNormSatz | None = None,
    *,
    charta_id: str = "zivilrechts-charta",
) -> ZivilrechtsCharta:
    if rechts_norm is None:
        rechts_norm = build_rechts_norm(norm_id=f"{charta_id}-norm")

    normen: list[ZivilrechtsChartaNorm] = []
    for parent_norm in rechts_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{rechts_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.rechts_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rechts_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZivilrechtsChartaGeltung.GRUNDLEGEND_ZIVILRECHTLICH)
        normen.append(
            ZivilrechtsChartaNorm(
                zivilrechts_charta_id=new_id,
                zivilrechts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                zivilrechts_weight=new_weight,
                zivilrechts_tier=new_tier,
                canonical=is_canonical,
                zivilrechts_ids=parent_norm.rechts_norm_ids + (new_id,),
                zivilrechts_tags=parent_norm.rechts_norm_tags + (f"zivilrechts-charta:{new_geltung.value}",),
            )
        )
    return ZivilrechtsCharta(
        charta_id=charta_id,
        rechts_norm=rechts_norm,
        normen=tuple(normen),
    )
