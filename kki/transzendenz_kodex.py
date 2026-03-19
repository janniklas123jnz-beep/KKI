"""transzendenz_kodex — Zivilisation & Transzendenz layer 10 / Block Crown (#250)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .erkenntnis_charta import (
    ErkenntnisCharta,
    ErkenntnisGeltung,
    ErkenntnisNorm,
    ErkenntnisTyp,
    ErkenntnisProzedur,
    build_erkenntnis_charta,
)

__all__ = [
    "TranszendenzEbene",
    "TranszendenzProzedur",
    "TranszendenzGeltung",
    "TranszendenzNorm",
    "TranszendenzKodex",
    "build_transzendenz_kodex",
]


class TranszendenzEbene(str, Enum):
    SCHUTZ_TRANSZENDENZ = "schutz-transzendenz"
    ORDNUNGS_TRANSZENDENZ = "ordnungs-transzendenz"
    SOUVERAENITAETS_TRANSZENDENZ = "souveraenitaets-transzendenz"


class TranszendenzProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TranszendenzGeltung(str, Enum):
    GESPERRT = "gesperrt"
    TRANSZENDIERT = "transzendiert"
    GRUNDLEGEND_TRANSZENDIERT = "grundlegend-transzendiert"


_EBENE_MAP: dict[ErkenntnisGeltung, TranszendenzEbene] = {
    ErkenntnisGeltung.GESPERRT: TranszendenzEbene.SCHUTZ_TRANSZENDENZ,
    ErkenntnisGeltung.ERLEUCHTET: TranszendenzEbene.ORDNUNGS_TRANSZENDENZ,
    ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET: TranszendenzEbene.SOUVERAENITAETS_TRANSZENDENZ,
}
_PROZEDUR_MAP: dict[ErkenntnisGeltung, TranszendenzProzedur] = {
    ErkenntnisGeltung.GESPERRT: TranszendenzProzedur.NOTPROZEDUR,
    ErkenntnisGeltung.ERLEUCHTET: TranszendenzProzedur.REGELPROTOKOLL,
    ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET: TranszendenzProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[ErkenntnisGeltung, TranszendenzGeltung] = {
    ErkenntnisGeltung.GESPERRT: TranszendenzGeltung.GESPERRT,
    ErkenntnisGeltung.ERLEUCHTET: TranszendenzGeltung.TRANSZENDIERT,
    ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET: TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT,
}
_WEIGHT_BONUS: dict[ErkenntnisGeltung, float] = {
    ErkenntnisGeltung.GESPERRT: 0.0,
    ErkenntnisGeltung.ERLEUCHTET: 0.04,
    ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET: 0.08,
}
_TIER_BONUS: dict[ErkenntnisGeltung, int] = {
    ErkenntnisGeltung.GESPERRT: 0,
    ErkenntnisGeltung.ERLEUCHTET: 1,
    ErkenntnisGeltung.GRUNDLEGEND_ERLEUCHTET: 2,
}


@dataclass(frozen=True)
class TranszendenzNorm:
    transzendenz_kodex_id: str
    transzendenz_ebene: TranszendenzEbene
    prozedur: TranszendenzProzedur
    geltung: TranszendenzGeltung
    transzendenz_weight: float
    transzendenz_tier: int
    canonical: bool
    transzendenz_kodex_ids: tuple[str, ...]
    transzendenz_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class TranszendenzKodex:
    kodex_id: str
    erkenntnis_charta: ErkenntnisCharta
    normen: tuple[TranszendenzNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.transzendenz_kodex_id for n in self.normen if n.geltung is TranszendenzGeltung.GESPERRT)

    @property
    def transzendiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.transzendenz_kodex_id for n in self.normen if n.geltung is TranszendenzGeltung.TRANSZENDIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.transzendenz_kodex_id for n in self.normen if n.geltung is TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is TranszendenzGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is TranszendenzGeltung.TRANSZENDIERT for n in self.normen):
            status = "kodex-transzendiert"
            severity = "warning"
        else:
            status = "kodex-grundlegend-transzendiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_transzendenz_kodex(
    erkenntnis_charta: ErkenntnisCharta | None = None,
    *,
    kodex_id: str = "transzendenz-kodex",
) -> TranszendenzKodex:
    if erkenntnis_charta is None:
        erkenntnis_charta = build_erkenntnis_charta(charta_id=f"{kodex_id}-charta")

    normen: list[TranszendenzNorm] = []
    for parent_norm in erkenntnis_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.erkenntnis_charta_id.removeprefix(f'{erkenntnis_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.erkenntnis_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.erkenntnis_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TranszendenzGeltung.GRUNDLEGEND_TRANSZENDIERT)
        normen.append(
            TranszendenzNorm(
                transzendenz_kodex_id=new_id,
                transzendenz_ebene=_EBENE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                transzendenz_weight=raw_weight,
                transzendenz_tier=new_tier,
                canonical=is_canonical,
                transzendenz_kodex_ids=parent_norm.erkenntnis_charta_ids + (new_id,),
                transzendenz_kodex_tags=parent_norm.erkenntnis_charta_tags + (f"transzendenz-kodex:{new_geltung.value}",),
            )
        )

    return TranszendenzKodex(
        kodex_id=kodex_id,
        erkenntnis_charta=erkenntnis_charta,
        normen=tuple(normen),
    )
