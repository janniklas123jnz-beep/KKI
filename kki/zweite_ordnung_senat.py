"""
#487 ZweiteOrdnungSenat — von Foerster: der Beobachter zweiter Ordnung beobachtet sich selbst.
Heinz von Foerster (1981): Observing Systems — Beobachter zweiter Ordnung beobachtet,
  wie Beobachter erster Ordnung beobachten; Reflexivität als epistemologische Grundlage.
Ernst von Glasersfeld (1984): Radikaler Konstruktivismus — Wissen ist keine Abbildung
  der Realität, sondern eine viable Konstruktion des erkennenden Subjekts; Wahrheit
  als Passung statt Korrespondenz.
Niklas Luhmann (1990): Die Wissenschaft der Gesellschaft — Selbstreferenz schließt
  Erkenntnissysteme operativ; Beobachtung zweiter Ordnung ermöglicht blinde Flecken
  sichtbar zu machen, erzeugt aber stets neue blinde Flecken.
Leitsterns Terra-Schwarm konstituiert den Senat der zweiten Ordnung: GESPERRT sichert
reflexive Integrität, ZWEITE_ORDNUNG aktiviert kollektive Selbstbeobachtung,
GRUNDLEGEND_ZWEITE_ORDNUNG synthetisiert den vollständigen kybernetischen Erkenntnisrahmen
für den sich selbst verstehenden Peta-Schwarm.
Parent: ViableSystemManifest (#486)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .viable_system_manifest import (
    ViableSystemManifest,
    ViableSystemManifestGeltung,
    build_viable_system_manifest,
)

_GELTUNG_MAP: dict[ViableSystemManifestGeltung, "ZweiteOrdnungSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ViableSystemManifestGeltung.GESPERRT] = ZweiteOrdnungSenatGeltung.GESPERRT
    _GELTUNG_MAP[ViableSystemManifestGeltung.VIABLE] = ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG
    _GELTUNG_MAP[ViableSystemManifestGeltung.GRUNDLEGEND_VIABLE] = ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG


class ZweiteOrdnungSenatTyp(Enum):
    SCHUTZ_ZWEITE_ORDNUNG = "schutz-zweite-ordnung"
    ORDNUNGS_ZWEITE_ORDNUNG = "ordnungs-zweite-ordnung"
    SOUVERAENITAETS_ZWEITE_ORDNUNG = "souveraenitaets-zweite-ordnung"


class ZweiteOrdnungSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ZweiteOrdnungSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    ZWEITE_ORDNUNG = "zweite-ordnung"
    GRUNDLEGEND_ZWEITE_ORDNUNG = "grundlegend-zweite-ordnung"


_init_map()

_TYP_MAP: dict[ZweiteOrdnungSenatGeltung, ZweiteOrdnungSenatTyp] = {
    ZweiteOrdnungSenatGeltung.GESPERRT: ZweiteOrdnungSenatTyp.SCHUTZ_ZWEITE_ORDNUNG,
    ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG: ZweiteOrdnungSenatTyp.ORDNUNGS_ZWEITE_ORDNUNG,
    ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG: ZweiteOrdnungSenatTyp.SOUVERAENITAETS_ZWEITE_ORDNUNG,
}

_PROZEDUR_MAP: dict[ZweiteOrdnungSenatGeltung, ZweiteOrdnungSenatProzedur] = {
    ZweiteOrdnungSenatGeltung.GESPERRT: ZweiteOrdnungSenatProzedur.NOTPROZEDUR,
    ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG: ZweiteOrdnungSenatProzedur.REGELPROTOKOLL,
    ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG: ZweiteOrdnungSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ZweiteOrdnungSenatGeltung, float] = {
    ZweiteOrdnungSenatGeltung.GESPERRT: 0.0,
    ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG: 0.04,
    ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG: 0.08,
}

_TIER_DELTA: dict[ZweiteOrdnungSenatGeltung, int] = {
    ZweiteOrdnungSenatGeltung.GESPERRT: 0,
    ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG: 1,
    ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG: 2,
}


@dataclass(frozen=True)
class ZweiteOrdnungSenatNorm:
    zweite_ordnung_senat_id: str
    zweite_ordnung_typ: ZweiteOrdnungSenatTyp
    prozedur: ZweiteOrdnungSenatProzedur
    geltung: ZweiteOrdnungSenatGeltung
    zweite_ordnung_weight: float
    zweite_ordnung_tier: int
    canonical: bool
    zweite_ordnung_ids: tuple[str, ...]
    zweite_ordnung_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZweiteOrdnungSenat:
    senat_id: str
    viable_system_manifest: ViableSystemManifest
    normen: tuple[ZweiteOrdnungSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zweite_ordnung_senat_id for n in self.normen if n.geltung is ZweiteOrdnungSenatGeltung.GESPERRT)

    @property
    def zweite_ordnung_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zweite_ordnung_senat_id for n in self.normen if n.geltung is ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.zweite_ordnung_senat_id for n in self.normen if n.geltung is ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG)

    @property
    def senat_signal(self):
        if any(n.geltung is ZweiteOrdnungSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is ZweiteOrdnungSenatGeltung.ZWEITE_ORDNUNG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-zweite-ordnung")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-zweite-ordnung")


def build_zweite_ordnung_senat(
    viable_system_manifest: ViableSystemManifest | None = None,
    *,
    senat_id: str = "zweite-ordnung-senat",
) -> ZweiteOrdnungSenat:
    if viable_system_manifest is None:
        viable_system_manifest = build_viable_system_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[ZweiteOrdnungSenatNorm] = []
    for parent_norm in viable_system_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.viable_system_manifest_id.removeprefix(f'{viable_system_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.viable_system_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.viable_system_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZweiteOrdnungSenatGeltung.GRUNDLEGEND_ZWEITE_ORDNUNG)
        normen.append(
            ZweiteOrdnungSenatNorm(
                zweite_ordnung_senat_id=new_id,
                zweite_ordnung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                zweite_ordnung_weight=new_weight,
                zweite_ordnung_tier=new_tier,
                canonical=is_canonical,
                zweite_ordnung_ids=parent_norm.viable_system_ids + (new_id,),
                zweite_ordnung_tags=parent_norm.viable_system_tags + (f"zweite-ordnung-senat:{new_geltung.value}",),
            )
        )
    return ZweiteOrdnungSenat(
        senat_id=senat_id,
        viable_system_manifest=viable_system_manifest,
        normen=tuple(normen),
    )
