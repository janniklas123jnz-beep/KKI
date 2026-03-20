"""
#316 HiggsManifest — Higgs-Mechanismus als Masse-Verleihungs-Manifest.
Geltungsstufen: GESPERRT / HIGGSGEKOPPELT / GRUNDLEGEND_HIGGSGEKOPPELT
Parent: EichbosonPakt (#315)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .eichboson_pakt import EichbosonGeltung, EichbosonPakt, build_eichboson_pakt

_GELTUNG_MAP: dict[EichbosonGeltung, "HiggsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EichbosonGeltung.GESPERRT] = HiggsGeltung.GESPERRT
    _GELTUNG_MAP[EichbosonGeltung.EICHBOSONAL] = HiggsGeltung.HIGGSGEKOPPELT
    _GELTUNG_MAP[EichbosonGeltung.GRUNDLEGEND_EICHBOSONAL] = HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT


class HiggsTyp(Enum):
    SCHUTZ_HIGGS = "schutz-higgs"
    ORDNUNGS_HIGGS = "ordnungs-higgs"
    SOUVERAENITAETS_HIGGS = "souveraenitaets-higgs"


class HiggsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HiggsGeltung(Enum):
    GESPERRT = "gesperrt"
    HIGGSGEKOPPELT = "higgsgekoppelt"
    GRUNDLEGEND_HIGGSGEKOPPELT = "grundlegend-higgsgekoppelt"


_init_map()

_TYP_MAP: dict[HiggsGeltung, HiggsTyp] = {
    HiggsGeltung.GESPERRT: HiggsTyp.SCHUTZ_HIGGS,
    HiggsGeltung.HIGGSGEKOPPELT: HiggsTyp.ORDNUNGS_HIGGS,
    HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT: HiggsTyp.SOUVERAENITAETS_HIGGS,
}

_PROZEDUR_MAP: dict[HiggsGeltung, HiggsProzedur] = {
    HiggsGeltung.GESPERRT: HiggsProzedur.NOTPROZEDUR,
    HiggsGeltung.HIGGSGEKOPPELT: HiggsProzedur.REGELPROTOKOLL,
    HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT: HiggsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HiggsGeltung, float] = {
    HiggsGeltung.GESPERRT: 0.0,
    HiggsGeltung.HIGGSGEKOPPELT: 0.04,
    HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT: 0.08,
}

_TIER_DELTA: dict[HiggsGeltung, int] = {
    HiggsGeltung.GESPERRT: 0,
    HiggsGeltung.HIGGSGEKOPPELT: 1,
    HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT: 2,
}


@dataclass(frozen=True)
class HiggsNorm:
    higgs_manifest_id: str
    higgs_typ: HiggsTyp
    prozedur: HiggsProzedur
    geltung: HiggsGeltung
    higgs_weight: float
    higgs_tier: int
    canonical: bool
    higgs_ids: tuple[str, ...]
    higgs_tags: tuple[str, ...]


@dataclass(frozen=True)
class HiggsManifest:
    manifest_id: str
    eichboson_pakt: EichbosonPakt
    normen: tuple[HiggsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.higgs_manifest_id for n in self.normen if n.geltung is HiggsGeltung.GESPERRT)

    @property
    def higgsgekoppelt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.higgs_manifest_id for n in self.normen if n.geltung is HiggsGeltung.HIGGSGEKOPPELT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.higgs_manifest_id for n in self.normen if n.geltung is HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT)

    @property
    def manifest_signal(self):
        if any(n.geltung is HiggsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is HiggsGeltung.HIGGSGEKOPPELT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-higgsgekoppelt")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-higgsgekoppelt")


def build_higgs_manifest(
    eichboson_pakt: EichbosonPakt | None = None,
    *,
    manifest_id: str = "higgs-manifest",
) -> HiggsManifest:
    if eichboson_pakt is None:
        eichboson_pakt = build_eichboson_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[HiggsNorm] = []
    for parent_norm in eichboson_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.eichboson_pakt_id.removeprefix(f'{eichboson_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.eichboson_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.eichboson_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT)
        normen.append(
            HiggsNorm(
                higgs_manifest_id=new_id,
                higgs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                higgs_weight=new_weight,
                higgs_tier=new_tier,
                canonical=is_canonical,
                higgs_ids=parent_norm.eichboson_ids + (new_id,),
                higgs_tags=parent_norm.eichboson_tags + (f"higgs-manifest:{new_geltung.value}",),
            )
        )
    return HiggsManifest(
        manifest_id=manifest_id,
        eichboson_pakt=eichboson_pakt,
        normen=tuple(normen),
    )
