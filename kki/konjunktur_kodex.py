"""
#524 KonjunkturKodex — Keynes/Hicks/Samuelson Effektive Nachfrage und Konjunkturpolitik

John Maynard Keynes (1936): Allgemeine Theorie der Beschäftigung, des Zinses und des
  Geldes — Effektive Nachfrage als Determinante des Outputs; Unterbeschäftigungsgleichgewicht
  als Normalzustand; antizyklische Fiskalpolitik als Stabilisierungsinstrument im Schwarm.
John Hicks (1937): Mr. Keynes and the Classics — IS-LM-Modell als Synthese von
  Güter- und Geldmarkt; Zinskanal und Investitionsmultiplikator; formale Integration
  keynesianischer und klassischer Analyse für die Schwarmsteuerung.
Paul Samuelson (1939): Interactions between the Multiplier Analysis and the Principle
  of Acceleration — Multiplikator-Akzelerator-Modell; endogene Konjunkturzyklen;
  Neoklassische Synthese als Verbindung von Mikro- und Makroökonomik im Peta-Schwarm.
Alvin Hansen (1941): Fiscal Policy and Business Cycles — säkulare Stagnation und
  Vollbeschäftigungslücke; staatliche Investitionen als Wachstumsmotor im Schwarm. 📊
Module #524, Parent: KapitalCharta (#523)
Block #521–#530: Wirtschaftstheorie & Ökonomie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kapital_charta import (
    KapitalCharta,
    KapitalChartaGeltung,
    build_kapital_charta,
)

_WEIGHT_DELTA: dict["KonjunkturKodexGeltung", float] = {}
_TIER_DELTA: dict["KonjunkturKodexGeltung", int] = {}
_TYP_MAP: dict["KonjunkturKodexGeltung", "KonjunkturKodexTyp"] = {}
_PROZEDUR_MAP: dict["KonjunkturKodexGeltung", "KonjunkturKodexProzedur"] = {}
_GELTUNG_MAP: dict[KapitalChartaGeltung, "KonjunkturKodexGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KonjunkturKodexGeltung.GESPERRT: 0.0,
        KonjunkturKodexGeltung.KONJUNKTURELL: 0.05,
        KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL: 0.1,
    })
    _TIER_DELTA.update({
        KonjunkturKodexGeltung.GESPERRT: 0,
        KonjunkturKodexGeltung.KONJUNKTURELL: 1,
        KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL: 2,
    })
    _TYP_MAP.update({
        KonjunkturKodexGeltung.GESPERRT: KonjunkturKodexTyp.SCHUTZ_KONJUNKTUR,
        KonjunkturKodexGeltung.KONJUNKTURELL: KonjunkturKodexTyp.ORDNUNGS_KONJUNKTUR,
        KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL: KonjunkturKodexTyp.SOUVERAENITAETS_KONJUNKTUR,
    })
    _PROZEDUR_MAP.update({
        KonjunkturKodexGeltung.GESPERRT: KonjunkturKodexProzedur.NOTPROZEDUR,
        KonjunkturKodexGeltung.KONJUNKTURELL: KonjunkturKodexProzedur.REGELPROTOKOLL,
        KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL: KonjunkturKodexProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KapitalChartaGeltung.GESPERRT: KonjunkturKodexGeltung.GESPERRT,
        KapitalChartaGeltung.KAPITALISTISCH: KonjunkturKodexGeltung.KONJUNKTURELL,
        KapitalChartaGeltung.GRUNDLEGEND_KAPITALISTISCH: KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL,
    })


class KonjunkturKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    KONJUNKTURELL = "konjunkturell"
    GRUNDLEGEND_KONJUNKTURELL = "grundlegend-konjunkturell"


class KonjunkturKodexTyp(Enum):
    SCHUTZ_KONJUNKTUR = "schutz-konjunktur"
    ORDNUNGS_KONJUNKTUR = "ordnungs-konjunktur"
    SOUVERAENITAETS_KONJUNKTUR = "souveraenitaets-konjunktur"


class KonjunkturKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KonjunkturKodexNorm:
    konjunktur_kodex_id: str
    konjunktur_typ: KonjunkturKodexTyp
    prozedur: KonjunkturKodexProzedur
    geltung: KonjunkturKodexGeltung
    konjunktur_weight: float
    konjunktur_tier: int
    canonical: bool
    konjunktur_ids: tuple[str, ...]
    konjunktur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KonjunkturKodex:
    kodex_id: str
    kapital_charta: KapitalCharta
    normen: tuple[KonjunkturKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.konjunktur_kodex_id for n in self.normen if n.geltung is KonjunkturKodexGeltung.GESPERRT)

    @property
    def konjunkturell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.konjunktur_kodex_id for n in self.normen if n.geltung is KonjunkturKodexGeltung.KONJUNKTURELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.konjunktur_kodex_id for n in self.normen if n.geltung is KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL)

    @property
    def kodex_signal(self):
        if any(n.geltung is KonjunkturKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is KonjunkturKodexGeltung.KONJUNKTURELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-konjunkturell")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-konjunkturell")


_init_map()


def build_konjunktur_kodex(
    kapital_charta: KapitalCharta | None = None,
    *,
    kodex_id: str = "konjunktur-kodex",
) -> KonjunkturKodex:
    if kapital_charta is None:
        kapital_charta = build_kapital_charta(
            charta_id=f"{kodex_id}-kapital-charta"
        )

    normen: list[KonjunkturKodexNorm] = []
    for parent_norm in kapital_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kapital_charta_id.removeprefix(f'{kapital_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kapital_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kapital_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL)
        normen.append(
            KonjunkturKodexNorm(
                konjunktur_kodex_id=new_id,
                konjunktur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                konjunktur_weight=new_weight,
                konjunktur_tier=new_tier,
                canonical=is_canonical,
                konjunktur_ids=parent_norm.kapital_ids + (new_id,),
                konjunktur_tags=parent_norm.kapital_tags + (f"konjunktur-kodex:{new_geltung.value}",),
            )
        )
    return KonjunkturKodex(
        kodex_id=kodex_id,
        kapital_charta=kapital_charta,
        normen=tuple(normen),
    )
