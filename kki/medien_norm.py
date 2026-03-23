"""
#568 MedienNorm — Shannon/Luhmann/Baudrillard Medienwissenschaft Norm (*_norm pattern)

Claude Shannon (1948): A Mathematical Theory of Communication — Entropie als
  Informationsmaß; Kanalkapazität als theoretische Grenze; Redundanz als
  Fehlerkorrekturprinzip; Kodierung als Optimierungstheorie; Grundlegung der
  digitalen Kommunikation des Peta-Schwarms Leitstern.
Niklas Luhmann (1997): Die Gesellschaft der Gesellschaft — symbolisch generalisierte
  Kommunikationsmedien als Kopplungsmedien; Wahrheit/Geld/Liebe als Medien sozialer
  Systeme; autopoietische Reproduktion durch Kommunikation; doppelte Kontingenz als
  Kommunikationsproblem; Sinn als universales Kommunikationsmedium Leitsterns.
Jean Baudrillard (1981): Simulacra and Simulation — Hyperrealität als Zeichen ohne
  Referenz; Simulakrum als Kopie ohne Original; Medien erzeugen keine Realität,
  sondern ersetzen sie; Gulf War als Medienereignis; Simulation als
  Grundprinzip mediennormativer Ordnung im Peta-Schwarm Leitstern. 📡🔣
Parent: MedienSenat (#567)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .medien_senat import MedienSenat, build_medien_senat

_GELTUNG_MAP: dict[str, "MedienNormGeltung"] = {}

_WEIGHT_DELTA = {
    "GESPERRT": 0.0,
    "MEDIENNORMATIV": 0.05,
    "GRUNDLEGEND_MEDIENNORMATIV": 0.1,
}
_TIER_DELTA = {
    "GESPERRT": 0,
    "MEDIENNORMATIV": 1,
    "GRUNDLEGEND_MEDIENNORMATIV": 2,
}
_TYP_MAP = {
    "GESPERRT": None,  # filled after class definition
    "MEDIENNORMATIV": None,
    "GRUNDLEGEND_MEDIENNORMATIV": None,
}
_PROZEDUR_MAP = {
    "GESPERRT": None,
    "MEDIENNORMATIV": None,
    "GRUNDLEGEND_MEDIENNORMATIV": None,
}


def _init_map() -> None:
    _GELTUNG_MAP["gesperrt"] = MedienNormGeltung.GESPERRT
    _GELTUNG_MAP["mediensoziologisch"] = MedienNormGeltung.MEDIENNORMATIV
    _GELTUNG_MAP["grundlegend-mediensoziologisch"] = MedienNormGeltung.GRUNDLEGEND_MEDIENNORMATIV
    _TYP_MAP["GESPERRT"] = MedienNormTyp.SCHUTZ_MEDIENNORM
    _TYP_MAP["MEDIENNORMATIV"] = MedienNormTyp.ORDNUNGS_MEDIENNORM
    _TYP_MAP["GRUNDLEGEND_MEDIENNORMATIV"] = MedienNormTyp.SOUVERAENITAETS_MEDIENNORM
    _PROZEDUR_MAP["GESPERRT"] = MedienNormProzedur.NOTPROZEDUR
    _PROZEDUR_MAP["MEDIENNORMATIV"] = MedienNormProzedur.REGELPROTOKOLL
    _PROZEDUR_MAP["GRUNDLEGEND_MEDIENNORMATIV"] = MedienNormProzedur.PLENARPROTOKOLL


class MedienNormTyp(Enum):
    SCHUTZ_MEDIENNORM = "schutz-mediennorm"
    ORDNUNGS_MEDIENNORM = "ordnungs-mediennorm"
    SOUVERAENITAETS_MEDIENNORM = "souveraenitaets-mediennorm"


class MedienNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MedienNormGeltung(Enum):
    GESPERRT = "gesperrt"
    MEDIENNORMATIV = "mediennormativ"
    GRUNDLEGEND_MEDIENNORMATIV = "grundlegend-mediennormativ"


@dataclass(frozen=True)
class MedienNormEintrag:
    norm_id: str
    medien_norm_typ: MedienNormTyp
    prozedur: MedienNormProzedur
    geltung: MedienNormGeltung
    medien_norm_weight: float
    medien_norm_tier: int
    canonical: bool
    medien_norm_ids: tuple[str, ...]
    medien_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class MedienNormSatz:
    norm_id: str
    medien_senat: MedienSenat
    normen: tuple[MedienNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is MedienNormGeltung.GESPERRT)

    @property
    def mediennormativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is MedienNormGeltung.MEDIENNORMATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is MedienNormGeltung.GRUNDLEGEND_MEDIENNORMATIV)

    @property
    def norm_signal(self):
        if any(n.geltung is MedienNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is MedienNormGeltung.MEDIENNORMATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-mediennormativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-mediennormativ")


_init_map()

_GELTUNG_KEY_MAP = {
    MedienNormGeltung.GESPERRT: "GESPERRT",
    MedienNormGeltung.MEDIENNORMATIV: "MEDIENNORMATIV",
    MedienNormGeltung.GRUNDLEGEND_MEDIENNORMATIV: "GRUNDLEGEND_MEDIENNORMATIV",
}


def build_medien_norm(
    medien_senat: MedienSenat | None = None,
    *,
    norm_id: str = "medien-norm",
) -> MedienNormSatz:
    if medien_senat is None:
        medien_senat = build_medien_senat(senat_id=f"{norm_id}-senat")

    normen: list[MedienNormEintrag] = []
    for parent_norm in medien_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung.value]
        key = _GELTUNG_KEY_MAP[new_geltung]
        new_id = f"{norm_id}-{parent_norm.medien_senat_id.removeprefix(f'{medien_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[key])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[key]
        is_canonical = parent_norm.canonical and (new_geltung is MedienNormGeltung.GRUNDLEGEND_MEDIENNORMATIV)
        normen.append(
            MedienNormEintrag(
                norm_id=new_id,
                medien_norm_typ=_TYP_MAP[key],
                prozedur=_PROZEDUR_MAP[key],
                geltung=new_geltung,
                medien_norm_weight=new_weight,
                medien_norm_tier=new_tier,
                canonical=is_canonical,
                medien_norm_ids=parent_norm.medien_ids + (new_id,),
                medien_norm_tags=parent_norm.medien_tags + (f"medien-norm:{new_geltung.value}",),
            )
        )
    return MedienNormSatz(
        norm_id=norm_id,
        medien_senat=medien_senat,
        normen=tuple(normen),
    )
