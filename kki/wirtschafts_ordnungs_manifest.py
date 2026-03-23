"""
#525 WirtschaftsOrdnungsManifest — Hayek/Eucken/Röpke Spontane Ordnung und Wettbewerbsordnung

Friedrich von Hayek (1944/1960): Der Weg zur Knechtschaft / Die Verfassung der Freiheit —
  Spontane Ordnung als emergentes Resultat individueller Handlungen; Preissystem als
  dezentraler Informationsverarbeitungsmechanismus; Regel des Rechts als Ordnungsrahmen
  für den Peta-Schwarm Leitstern.
Walter Eucken (1952): Grundsätze der Wirtschaftspolitik — Ordoliberalismus und
  konstituierende Prinzipien einer Wettbewerbsordnung; Primat der Währungsstabilität;
  staatliche Rahmensetzung ohne Eingriff in den Marktprozess als Schwarmgovernance.
Wilhelm Röpke (1942): Die Gesellschaftskrisis der Gegenwart — Soziale Marktwirtschaft
  als dritter Weg zwischen Laissez-faire und Zentralplanung; Dezentralisierung und
  humane Wirtschaftsordnung; Vitalpolitik jenseits des Marktmechanismus im Schwarm.
Ludwig Erhard (1957): Wohlstand für alle — praktische Umsetzung der sozialen
  Marktwirtschaft; Wettbewerb als Entdeckungsverfahren für Effizienz und Innovation. 🏛️
Module #525, Parent: KonjunkturKodex (#524)
Block #521–#530: Wirtschaftstheorie & Ökonomie
Note: kki/ordnungs_manifest.py is taken by a different module chain; this file serves as
  the #525 OrdnungsManifest in the Wirtschaftstheorie block.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .konjunktur_kodex import (
    KonjunkturKodex,
    KonjunkturKodexGeltung,
    build_konjunktur_kodex,
)

_WEIGHT_DELTA: dict["WirtschaftsOrdnungsManifestGeltung", float] = {}
_TIER_DELTA: dict["WirtschaftsOrdnungsManifestGeltung", int] = {}
_TYP_MAP: dict["WirtschaftsOrdnungsManifestGeltung", "WirtschaftsOrdnungsManifestTyp"] = {}
_PROZEDUR_MAP: dict["WirtschaftsOrdnungsManifestGeltung", "WirtschaftsOrdnungsManifestProzedur"] = {}
_GELTUNG_MAP: dict[KonjunkturKodexGeltung, "WirtschaftsOrdnungsManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WirtschaftsOrdnungsManifestGeltung.GESPERRT: 0.0,
        WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH: 0.05,
        WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH: 0.1,
    })
    _TIER_DELTA.update({
        WirtschaftsOrdnungsManifestGeltung.GESPERRT: 0,
        WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH: 1,
        WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH: 2,
    })
    _TYP_MAP.update({
        WirtschaftsOrdnungsManifestGeltung.GESPERRT: WirtschaftsOrdnungsManifestTyp.SCHUTZ_ORDNUNG,
        WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH: WirtschaftsOrdnungsManifestTyp.ORDNUNGS_ORDNUNG,
        WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH: WirtschaftsOrdnungsManifestTyp.SOUVERAENITAETS_ORDNUNG,
    })
    _PROZEDUR_MAP.update({
        WirtschaftsOrdnungsManifestGeltung.GESPERRT: WirtschaftsOrdnungsManifestProzedur.NOTPROZEDUR,
        WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH: WirtschaftsOrdnungsManifestProzedur.REGELPROTOKOLL,
        WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH: WirtschaftsOrdnungsManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KonjunkturKodexGeltung.GESPERRT: WirtschaftsOrdnungsManifestGeltung.GESPERRT,
        KonjunkturKodexGeltung.KONJUNKTURELL: WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH,
        KonjunkturKodexGeltung.GRUNDLEGEND_KONJUNKTURELL: WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH,
    })


class WirtschaftsOrdnungsManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    ORDNUNGSOEKONOMISCH = "ordnungsoekonomisch"
    GRUNDLEGEND_ORDNUNGSOEKONOMISCH = "grundlegend-ordnungsoekonomisch"


class WirtschaftsOrdnungsManifestTyp(Enum):
    SCHUTZ_ORDNUNG = "schutz-ordnung"
    ORDNUNGS_ORDNUNG = "ordnungs-ordnung"
    SOUVERAENITAETS_ORDNUNG = "souveraenitaets-ordnung"


class WirtschaftsOrdnungsManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class WirtschaftsOrdnungsManifestNorm:
    ordnungs_manifest_id: str
    ordnungs_typ: WirtschaftsOrdnungsManifestTyp
    prozedur: WirtschaftsOrdnungsManifestProzedur
    geltung: WirtschaftsOrdnungsManifestGeltung
    ordnungs_weight: float
    ordnungs_tier: int
    canonical: bool
    ordnungs_ids: tuple[str, ...]
    ordnungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class WirtschaftsOrdnungsManifest:
    manifest_id: str
    konjunktur_kodex: KonjunkturKodex
    normen: tuple[WirtschaftsOrdnungsManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ordnungs_manifest_id for n in self.normen if n.geltung is WirtschaftsOrdnungsManifestGeltung.GESPERRT)

    @property
    def ordnungsoekonomisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ordnungs_manifest_id for n in self.normen if n.geltung is WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ordnungs_manifest_id for n in self.normen if n.geltung is WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is WirtschaftsOrdnungsManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is WirtschaftsOrdnungsManifestGeltung.ORDNUNGSOEKONOMISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-ordnungsoekonomisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-ordnungsoekonomisch")


_init_map()


def build_ordnungs_manifest(
    konjunktur_kodex: KonjunkturKodex | None = None,
    *,
    manifest_id: str = "ordnungs-manifest",
) -> WirtschaftsOrdnungsManifest:
    if konjunktur_kodex is None:
        konjunktur_kodex = build_konjunktur_kodex(
            kodex_id=f"{manifest_id}-konjunktur-kodex"
        )

    normen: list[WirtschaftsOrdnungsManifestNorm] = []
    for parent_norm in konjunktur_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.konjunktur_kodex_id.removeprefix(f'{konjunktur_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.konjunktur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.konjunktur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WirtschaftsOrdnungsManifestGeltung.GRUNDLEGEND_ORDNUNGSOEKONOMISCH)
        normen.append(
            WirtschaftsOrdnungsManifestNorm(
                ordnungs_manifest_id=new_id,
                ordnungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                ordnungs_weight=new_weight,
                ordnungs_tier=new_tier,
                canonical=is_canonical,
                ordnungs_ids=parent_norm.konjunktur_ids + (new_id,),
                ordnungs_tags=parent_norm.konjunktur_tags + (f"ordnungs-manifest:{new_geltung.value}",),
            )
        )
    return WirtschaftsOrdnungsManifest(
        manifest_id=manifest_id,
        konjunktur_kodex=konjunktur_kodex,
        normen=tuple(normen),
    )
