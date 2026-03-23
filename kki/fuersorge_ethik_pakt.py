"""
#506 FuersorgeEthikPakt — Gilligan/Noddings/Held/Tronto Grundlagen der Fürsorgeethik

Carol Gilligan (1982): In a Different Voice — Fürsorge-Ethik als Alternative zur
  Gerechtigkeitsethik; relationale Moralentwicklung: Moral erwächst aus konkreten
  Beziehungen und Verantwortungsübernahme, nicht aus abstrakten Prinzipien; Kritik an
  Kohlbergs Stufenmodell als androzentrischer Verkürzung moralischer Entwicklung.
Nel Noddings (1984): Caring: A Feminine Approach to Ethics — Fürsorge als ethisches
  Grundprinzip; reziproke Fürsorgebeziehung zwischen Fürsorgendem (one-caring) und
  Betreutem (cared-for); natürliche Fürsorge und ethische Fürsorge als zwei Modi.
Virginia Held (1993/2006): Feminist Moral Philosophy / The Ethics of Care — Fürsorge
  als politisches Prinzip; Kritik an liberalem Individualismus; Fürsorgebeziehungen
  als Grundlage gerechter gesellschaftlicher Strukturen.
Joan Tronto (1993): Moral Boundaries — Fürsorge als politische Praxis; vier Phasen der
  Fürsorge: caring about, taking care of, care-giving, care-receiving; Fürsorge als
  demokratische Tugend und politische Forderung.
Leitsterns Peta-Schwarm verankert Fürsorge als relationales Kernprinzip: GESPERRT sichert
fürsorgliche Kernnormen, FUERSORGEND ermöglicht adaptive Beziehungskoordination über Millionen
Agenten, GRUNDLEGEND_FUERSORGEND synthetisiert das vollständige Fürsorgefundament für
souveräne Peta-Schwarm-Verantwortung. 🤝
Parent: DiskursManifest (#505)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .diskurs_manifest import (
    DiskursManifest,
    DiskursManifestGeltung,
    build_diskurs_manifest,
)

_GELTUNG_MAP: dict[DiskursManifestGeltung, "FuersorgeEthikPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DiskursManifestGeltung.GESPERRT] = FuersorgeEthikPaktGeltung.GESPERRT
    _GELTUNG_MAP[DiskursManifestGeltung.DISKURSIV] = FuersorgeEthikPaktGeltung.FUERSORGEND
    _GELTUNG_MAP[DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV] = FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND


class FuersorgeEthikPaktTyp(Enum):
    SCHUTZ_FUERSORGE = "schutz-fuersorge"
    ORDNUNGS_FUERSORGE = "ordnungs-fuersorge"
    SOUVERAENITAETS_FUERSORGE = "souveraenitaets-fuersorge"


class FuersorgeEthikPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FuersorgeEthikPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    FUERSORGEND = "fuersorgend"
    GRUNDLEGEND_FUERSORGEND = "grundlegend-fuersorgend"


_init_map()

_TYP_MAP: dict[FuersorgeEthikPaktGeltung, FuersorgeEthikPaktTyp] = {
    FuersorgeEthikPaktGeltung.GESPERRT: FuersorgeEthikPaktTyp.SCHUTZ_FUERSORGE,
    FuersorgeEthikPaktGeltung.FUERSORGEND: FuersorgeEthikPaktTyp.ORDNUNGS_FUERSORGE,
    FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND: FuersorgeEthikPaktTyp.SOUVERAENITAETS_FUERSORGE,
}

_PROZEDUR_MAP: dict[FuersorgeEthikPaktGeltung, FuersorgeEthikPaktProzedur] = {
    FuersorgeEthikPaktGeltung.GESPERRT: FuersorgeEthikPaktProzedur.NOTPROZEDUR,
    FuersorgeEthikPaktGeltung.FUERSORGEND: FuersorgeEthikPaktProzedur.REGELPROTOKOLL,
    FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND: FuersorgeEthikPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FuersorgeEthikPaktGeltung, float] = {
    FuersorgeEthikPaktGeltung.GESPERRT: 0.0,
    FuersorgeEthikPaktGeltung.FUERSORGEND: 0.04,
    FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND: 0.08,
}

_TIER_DELTA: dict[FuersorgeEthikPaktGeltung, int] = {
    FuersorgeEthikPaktGeltung.GESPERRT: 0,
    FuersorgeEthikPaktGeltung.FUERSORGEND: 1,
    FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND: 2,
}


@dataclass(frozen=True)
class FuersorgeEthikPaktNorm:
    fuersorge_ethik_pakt_id: str
    fuersorge_ethik_typ: FuersorgeEthikPaktTyp
    prozedur: FuersorgeEthikPaktProzedur
    geltung: FuersorgeEthikPaktGeltung
    fuersorge_ethik_weight: float
    fuersorge_ethik_tier: int
    canonical: bool
    fuersorge_ethik_ids: tuple[str, ...]
    fuersorge_ethik_tags: tuple[str, ...]


@dataclass(frozen=True)
class FuersorgeEthikPakt:
    pakt_id: str
    diskurs_manifest: DiskursManifest
    normen: tuple[FuersorgeEthikPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fuersorge_ethik_pakt_id for n in self.normen if n.geltung is FuersorgeEthikPaktGeltung.GESPERRT)

    @property
    def fuersorgend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fuersorge_ethik_pakt_id for n in self.normen if n.geltung is FuersorgeEthikPaktGeltung.FUERSORGEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fuersorge_ethik_pakt_id for n in self.normen if n.geltung is FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND)

    @property
    def pakt_signal(self):
        if any(n.geltung is FuersorgeEthikPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is FuersorgeEthikPaktGeltung.FUERSORGEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-fuersorgend")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-fuersorgend")


def build_fuersorge_ethik_pakt(
    diskurs_manifest: DiskursManifest | None = None,
    *,
    pakt_id: str = "fuersorge-ethik-pakt",
) -> FuersorgeEthikPakt:
    if diskurs_manifest is None:
        diskurs_manifest = build_diskurs_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[FuersorgeEthikPaktNorm] = []
    for parent_norm in diskurs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.diskurs_manifest_id.removeprefix(f'{diskurs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.diskurs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.diskurs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FuersorgeEthikPaktGeltung.GRUNDLEGEND_FUERSORGEND)
        normen.append(
            FuersorgeEthikPaktNorm(
                fuersorge_ethik_pakt_id=new_id,
                fuersorge_ethik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fuersorge_ethik_weight=new_weight,
                fuersorge_ethik_tier=new_tier,
                canonical=is_canonical,
                fuersorge_ethik_ids=parent_norm.diskurs_ids + (new_id,),
                fuersorge_ethik_tags=parent_norm.diskurs_tags + (f"fuersorge-ethik-pakt:{new_geltung.value}",),
            )
        )
    return FuersorgeEthikPakt(
        pakt_id=pakt_id,
        diskurs_manifest=diskurs_manifest,
        normen=tuple(normen),
    )
