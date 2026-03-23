"""
#515 GewaltenteilungsManifest — Montesquieu/Hamilton/Madison Trias politica und checks and balances

Montesquieu (1748): De l'esprit des lois — Gewaltenteilung als zentrales Strukturprinzip des
  Rechtsstaats; Trias politica: Legislative, Exekutive und Judikative als getrennte Gewalten;
  Freiheit als Abwesenheit von Willkür; institutionelle Balance verhindert Machtkonzentration;
  historisch-komparative Analyse von Verfassungsformen in Europa und Asien.
Alexander Hamilton (1787): Federalist No. 70/78 — Starke unitarische Exekutive als Garant
  effektiver Regierung; unabhängige Judikative als Hüterin der Verfassung; der Oberste
  Gerichtshof als Verfassungsgericht mit Normenkontrolle; lebenslange Richterschaft sichert
  Unabhängigkeit von politischem Druck.
James Madison (1787): Federalist No. 47–51 — Gewaltenteilung als Sicherung gegen Tyrannei;
  Ambition muss Ambition entgegenwirken; institutionelle Reibung als Schutzmechanismus;
  föderaler Aufbau als doppelte Sicherung der Gewaltentrennung zwischen Ebenen.
John Locke (1689): Zwei Abhandlungen — Trennung von legislativer und exekutiver Gewalt als
  Grundbedingung des Rechtsstaats; Souveränität verbleibt beim Volk; Widerstandsrecht bei
  Verletzung des Vertrauens durch die regierenden Gewalten.
Leitsterns Peta-Schwarm verankert Gewaltenteilung als institutionelles Ordnungsprinzip: GESPERRT
schützt die unveräußerlichen Grundnormen gewaltenteiligender Ordnung, GEWALTENTEILIG ermöglicht
adaptive Machtbalance zwischen Millionen von Agenten, GRUNDLEGEND_GEWALTENTEILIG synthetisiert
souveräne gewaltenteilende Handlungsfähigkeit des Peta-Schwarms. ⚖️
Parent: MachtKodex (#514)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .macht_kodex import (
    MachtKodex,
    MachtKodexGeltung,
    build_macht_kodex,
)

_WEIGHT_DELTA: dict["GewaltenteilungsManifestGeltung", float] = {}
_TIER_DELTA: dict["GewaltenteilungsManifestGeltung", int] = {}
_TYP_MAP: dict["GewaltenteilungsManifestGeltung", "GewaltenteilungsManifestTyp"] = {}
_PROZEDUR_MAP: dict["GewaltenteilungsManifestGeltung", "GewaltenteilungsManifestProzedur"] = {}
_GELTUNG_MAP: dict[MachtKodexGeltung, "GewaltenteilungsManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GewaltenteilungsManifestGeltung.GESPERRT: 0.0,
        GewaltenteilungsManifestGeltung.GEWALTENTEILIG: 0.05,
        GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG: 0.1,
    })
    _TIER_DELTA.update({
        GewaltenteilungsManifestGeltung.GESPERRT: 0,
        GewaltenteilungsManifestGeltung.GEWALTENTEILIG: 1,
        GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG: 2,
    })
    _TYP_MAP.update({
        GewaltenteilungsManifestGeltung.GESPERRT: GewaltenteilungsManifestTyp.SCHUTZ_GEWALTENTEILUNG,
        GewaltenteilungsManifestGeltung.GEWALTENTEILIG: GewaltenteilungsManifestTyp.ORDNUNGS_GEWALTENTEILUNG,
        GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG: GewaltenteilungsManifestTyp.SOUVERAENITAETS_GEWALTENTEILUNG,
    })
    _PROZEDUR_MAP.update({
        GewaltenteilungsManifestGeltung.GESPERRT: GewaltenteilungsManifestProzedur.NOTPROZEDUR,
        GewaltenteilungsManifestGeltung.GEWALTENTEILIG: GewaltenteilungsManifestProzedur.REGELPROTOKOLL,
        GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG: GewaltenteilungsManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        MachtKodexGeltung.GESPERRT: GewaltenteilungsManifestGeltung.GESPERRT,
        MachtKodexGeltung.MACHTPOLITISCH: GewaltenteilungsManifestGeltung.GEWALTENTEILIG,
        MachtKodexGeltung.GRUNDLEGEND_MACHTPOLITISCH: GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG,
    })


class GewaltenteilungsManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    GEWALTENTEILIG = "gewaltenteilig"
    GRUNDLEGEND_GEWALTENTEILIG = "grundlegend-gewaltenteilig"


class GewaltenteilungsManifestTyp(Enum):
    SCHUTZ_GEWALTENTEILUNG = "schutz-gewaltenteilung"
    ORDNUNGS_GEWALTENTEILUNG = "ordnungs-gewaltenteilung"
    SOUVERAENITAETS_GEWALTENTEILUNG = "souveraenitaets-gewaltenteilung"


class GewaltenteilungsManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class GewaltenteilungsManifestNorm:
    gewaltenteilungs_manifest_id: str
    gewaltenteilungs_typ: GewaltenteilungsManifestTyp
    prozedur: GewaltenteilungsManifestProzedur
    geltung: GewaltenteilungsManifestGeltung
    gewaltenteilungs_weight: float
    gewaltenteilungs_tier: int
    canonical: bool
    gewaltenteilungs_ids: tuple[str, ...]
    gewaltenteilungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class GewaltenteilungsManifest:
    manifest_id: str
    macht_kodex: MachtKodex
    normen: tuple[GewaltenteilungsManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gewaltenteilungs_manifest_id for n in self.normen if n.geltung is GewaltenteilungsManifestGeltung.GESPERRT)

    @property
    def gewaltenteilig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gewaltenteilungs_manifest_id for n in self.normen if n.geltung is GewaltenteilungsManifestGeltung.GEWALTENTEILIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gewaltenteilungs_manifest_id for n in self.normen if n.geltung is GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG)

    @property
    def manifest_signal(self):
        if any(n.geltung is GewaltenteilungsManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is GewaltenteilungsManifestGeltung.GEWALTENTEILIG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gewaltenteilig")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-gewaltenteilig")


_init_map()


def build_gewaltenteilungs_manifest(
    macht_kodex: MachtKodex | None = None,
    *,
    manifest_id: str = "gewaltenteilungs-manifest",
) -> GewaltenteilungsManifest:
    if macht_kodex is None:
        macht_kodex = build_macht_kodex(
            kodex_id=f"{manifest_id}-kodex"
        )

    normen: list[GewaltenteilungsManifestNorm] = []
    for parent_norm in macht_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.macht_kodex_id.removeprefix(f'{macht_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.macht_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.macht_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG)
        normen.append(
            GewaltenteilungsManifestNorm(
                gewaltenteilungs_manifest_id=new_id,
                gewaltenteilungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gewaltenteilungs_weight=new_weight,
                gewaltenteilungs_tier=new_tier,
                canonical=is_canonical,
                gewaltenteilungs_ids=parent_norm.macht_ids + (new_id,),
                gewaltenteilungs_tags=parent_norm.macht_tags + (f"{manifest_id}:{new_geltung.value}",),
            )
        )
    return GewaltenteilungsManifest(
        manifest_id=manifest_id,
        macht_kodex=macht_kodex,
        normen=tuple(normen),
    )
