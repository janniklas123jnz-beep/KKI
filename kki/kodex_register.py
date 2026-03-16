"""Kodex register persisting Leitstern codex sections as versioned references."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .data_models import PersistenceRecord
from .leitstern_codex import CodexCanon, CodexSection, CodexStatus, LeitsternCodex, build_leitstern_codex
from .module_boundaries import ModuleBoundaryName
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class RegisterTier(str, Enum):
    """Version tier assigned to one codex register entry."""

    RESERVED = "reserved"
    CURATED = "curated"
    CANONIZED = "canonized"


class RegisterRetention(str, Enum):
    """Retention posture for codex register entries."""

    AUDIT = "audit"
    GOVERNANCE = "governance"
    CONSTITUTIONAL = "constitutional"


@dataclass(frozen=True)
class KodexRegisterEntry:
    """One versioned register entry derived from a codex section."""

    entry_id: str
    sequence: int
    section_id: str
    directive_id: str
    delegation_id: str
    mission_ref: str
    codex_canon: CodexCanon
    register_tier: RegisterTier
    retention: RegisterRetention
    version: str
    reference_key: str
    persistence_record: PersistenceRecord
    case_ids: tuple[str, ...]
    release_ready: bool
    register_weight: float
    register_tags: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_id", _non_empty(self.entry_id, field_name="entry_id"))
        object.__setattr__(self, "section_id", _non_empty(self.section_id, field_name="section_id"))
        object.__setattr__(self, "directive_id", _non_empty(self.directive_id, field_name="directive_id"))
        object.__setattr__(self, "delegation_id", _non_empty(self.delegation_id, field_name="delegation_id"))
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "version", _non_empty(self.version, field_name="version"))
        object.__setattr__(self, "reference_key", _non_empty(self.reference_key, field_name="reference_key"))
        object.__setattr__(self, "register_weight", _clamp01(self.register_weight))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "sequence": self.sequence,
            "section_id": self.section_id,
            "directive_id": self.directive_id,
            "delegation_id": self.delegation_id,
            "mission_ref": self.mission_ref,
            "codex_canon": self.codex_canon.value,
            "register_tier": self.register_tier.value,
            "retention": self.retention.value,
            "version": self.version,
            "reference_key": self.reference_key,
            "persistence_record": self.persistence_record.to_dict(),
            "case_ids": list(self.case_ids),
            "release_ready": self.release_ready,
            "register_weight": self.register_weight,
            "register_tags": list(self.register_tags),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class KodexRegister:
    """Versioned register over the canonical Leitstern codex."""

    register_id: str
    leitstern_codex: LeitsternCodex
    entries: tuple[KodexRegisterEntry, ...]
    register_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_id", _non_empty(self.register_id, field_name="register_id"))

    @property
    def reserved_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.register_tier is RegisterTier.RESERVED)

    @property
    def curated_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.register_tier is RegisterTier.CURATED)

    @property
    def canonized_entry_ids(self) -> tuple[str, ...]:
        return tuple(entry.entry_id for entry in self.entries if entry.register_tier is RegisterTier.CANONIZED)

    def to_dict(self) -> dict[str, object]:
        return {
            "register_id": self.register_id,
            "leitstern_codex": self.leitstern_codex.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
            "register_signal": self.register_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "reserved_entry_ids": list(self.reserved_entry_ids),
            "curated_entry_ids": list(self.curated_entry_ids),
            "canonized_entry_ids": list(self.canonized_entry_ids),
        }


def _register_tier(section: CodexSection) -> RegisterTier:
    return {
        CodexStatus.GUARDED: RegisterTier.RESERVED,
        CodexStatus.GOVERNED: RegisterTier.CURATED,
        CodexStatus.CANONICAL: RegisterTier.CANONIZED,
    }[section.codex_status]


def _retention(section: CodexSection) -> RegisterRetention:
    return {
        CodexStatus.GUARDED: RegisterRetention.AUDIT,
        CodexStatus.GOVERNED: RegisterRetention.GOVERNANCE,
        CodexStatus.CANONICAL: RegisterRetention.CONSTITUTIONAL,
    }[section.codex_status]


def _version(sequence: int) -> str:
    return f"v1.{sequence}"


def _reference_key(register_id: str, section: CodexSection) -> str:
    return f"{register_id}:{section.codex_canon.value}:{section.section_id}"


def _register_weight(section: CodexSection) -> float:
    bonus = {
        RegisterTier.RESERVED: 0.0,
        RegisterTier.CURATED: 0.04,
        RegisterTier.CANONIZED: 0.08,
    }[_register_tier(section)]
    return round(min(1.0, section.codex_strength + bonus), 3)


def _persistence_retention(section: CodexSection) -> str:
    return {
        RegisterRetention.AUDIT: "audit",
        RegisterRetention.GOVERNANCE: "audit",
        RegisterRetention.CONSTITUTIONAL: "knowledge",
    }[_retention(section)]


def _persistence_record(
    register_id: str,
    boundary: ModuleBoundaryName,
    section: CodexSection,
    *,
    version: str,
    reference_key: str,
) -> PersistenceRecord:
    return PersistenceRecord(
        record_type="leitstern-codex-register-entry",
        boundary=boundary,
        schema_version="1.0",
        retention_class=_persistence_retention(section),
        payload={
            "register_id": register_id,
            "section_id": section.section_id,
            "directive_id": section.directive_id,
            "delegation_id": section.delegation_id,
            "mission_ref": section.mission_ref,
            "codex_canon": section.codex_canon.value,
            "codex_axis": section.codex_axis.value,
            "codex_status": section.codex_status.value,
            "version": version,
            "reference_key": reference_key,
            "case_ids": list(section.case_ids),
        },
    )


def build_kodex_register(
    leitstern_codex: LeitsternCodex | None = None,
    *,
    register_id: str = "kodex-register",
) -> KodexRegister:
    """Build the versioned register over Leitstern codex sections."""

    resolved_codex = build_leitstern_codex(codex_id=f"{register_id}-codex") if leitstern_codex is None else leitstern_codex
    entries = tuple(
        KodexRegisterEntry(
            entry_id=f"{register_id}-{section.section_id.removeprefix(f'{resolved_codex.codex_id}-')}",
            sequence=index,
            section_id=section.section_id,
            directive_id=section.directive_id,
            delegation_id=section.delegation_id,
            mission_ref=section.mission_ref,
            codex_canon=section.codex_canon,
            register_tier=_register_tier(section),
            retention=_retention(section),
            version=_version(index),
            reference_key=_reference_key(register_id, section),
            persistence_record=_persistence_record(
                register_id,
                resolved_codex.codex_signal.boundary,
                section,
                version=_version(index),
                reference_key=_reference_key(register_id, section),
            ),
            case_ids=section.case_ids,
            release_ready=section.release_ready and _register_tier(section) is RegisterTier.CANONIZED,
            register_weight=_register_weight(section),
            register_tags=tuple(
                dict.fromkeys(
                    (
                        *section.codex_tags,
                        _register_tier(section).value,
                        _retention(section).value,
                        _version(index),
                    )
                )
            ),
            summary=(
                f"{section.section_id} is registered as {_register_tier(section).value} entry "
                f"with {_retention(section).value} retention in {_version(index)}."
            ),
        )
        for index, section in enumerate(resolved_codex.sections, start=1)
    )
    if not entries:
        raise ValueError("kodex register requires at least one entry")

    severity = "info"
    status = "register-canonized"
    if any(entry.register_tier is RegisterTier.RESERVED for entry in entries):
        severity = "critical"
        status = "register-reserved"
    elif any(entry.register_tier is RegisterTier.CURATED for entry in entries):
        severity = "warning"
        status = "register-curated"

    register_signal = TelemetrySignal(
        signal_name="kodex-register",
        boundary=resolved_codex.codex_signal.boundary,
        correlation_id=register_id,
        severity=severity,
        status=status,
        metrics={
            "entry_count": float(len(entries)),
            "reserved_count": float(len([entry for entry in entries if entry.register_tier is RegisterTier.RESERVED])),
            "curated_count": float(len([entry for entry in entries if entry.register_tier is RegisterTier.CURATED])),
            "canonized_count": float(len([entry for entry in entries if entry.register_tier is RegisterTier.CANONIZED])),
            "release_ready_count": float(len([entry for entry in entries if entry.release_ready])),
            "avg_register_weight": round(sum(entry.register_weight for entry in entries) / len(entries), 3),
        },
        labels={"register_id": register_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_codex.final_snapshot.runtime_stage,
        signals=(register_signal, *resolved_codex.final_snapshot.signals),
        alerts=resolved_codex.final_snapshot.alerts,
        audit_entries=resolved_codex.final_snapshot.audit_entries,
        active_controls=resolved_codex.final_snapshot.active_controls,
    )
    return KodexRegister(
        register_id=register_id,
        leitstern_codex=resolved_codex,
        entries=entries,
        register_signal=register_signal,
        final_snapshot=final_snapshot,
    )
