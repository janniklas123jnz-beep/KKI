"""Canonical data models for the build-phase package."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from types import MappingProxyType
from typing import Mapping

from .module_boundaries import ModuleBoundaryName, module_boundary
from .runtime_dna import RuntimeDNA, RuntimeStage


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


@dataclass(frozen=True)
class CoreState:
    """Canonical runtime state exported across module boundaries."""

    identity_slug: str
    module_boundary: ModuleBoundaryName
    runtime_stage: RuntimeStage
    status: str
    budget: float
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "identity_slug", _non_empty(self.identity_slug, field_name="identity_slug"))
        object.__setattr__(self, "status", _non_empty(self.status, field_name="status"))
        if not 0.0 <= float(self.budget) <= 1.0:
            raise ValueError("budget must be between 0.0 and 1.0")
        object.__setattr__(self, "budget", float(self.budget))
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    def to_dict(self) -> dict[str, object]:
        return {
            "identity_slug": self.identity_slug,
            "module_boundary": self.module_boundary.value,
            "runtime_stage": self.runtime_stage.value,
            "status": self.status,
            "budget": self.budget,
            "labels": dict(self.labels),
        }


@dataclass(frozen=True)
class TransferEnvelope:
    """Canonical transfer payload for state, replay, rollout, and recovery flows."""

    schema_version: str
    payload_type: str
    source_boundary: ModuleBoundaryName
    target_boundary: ModuleBoundaryName
    correlation_id: str
    integrity_status: str
    payload: Mapping[str, object]
    causation_id: str | None = None
    sequence: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _non_empty(self.schema_version, field_name="schema_version"))
        object.__setattr__(self, "payload_type", _non_empty(self.payload_type, field_name="payload_type"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _non_empty(self.causation_id, field_name="causation_id"))
        if self.integrity_status not in {"verified", "attested", "degraded"}:
            raise ValueError("integrity_status must be one of: verified, attested, degraded")
        if self.sequence < 0:
            raise ValueError("sequence must be >= 0")

        module_boundary(self.source_boundary)
        module_boundary(self.target_boundary)
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "payload_type": self.payload_type,
            "source_boundary": self.source_boundary.value,
            "target_boundary": self.target_boundary.value,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "integrity_status": self.integrity_status,
            "sequence": self.sequence,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class PersistenceRecord:
    """Canonical persistence unit for restart, knowledge, and audit storage."""

    record_type: str
    boundary: ModuleBoundaryName
    schema_version: str
    retention_class: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_type", _non_empty(self.record_type, field_name="record_type"))
        object.__setattr__(self, "schema_version", _non_empty(self.schema_version, field_name="schema_version"))
        if self.retention_class not in {"ephemeral", "restart", "knowledge", "audit"}:
            raise ValueError("retention_class must be one of: ephemeral, restart, knowledge, audit")
        module_boundary(self.boundary)
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "record_type": self.record_type,
            "boundary": self.boundary.value,
            "schema_version": self.schema_version,
            "retention_class": self.retention_class,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class EvidenceRecord:
    """Canonical evidence object for approvals, commitment, and recovery proof chains."""

    evidence_type: str
    subject: str
    correlation_id: str
    audit_ref: str
    payload: Mapping[str, object]
    commitment_ref: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_type", _non_empty(self.evidence_type, field_name="evidence_type"))
        object.__setattr__(self, "subject", _non_empty(self.subject, field_name="subject"))
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "audit_ref", _non_empty(self.audit_ref, field_name="audit_ref"))
        if self.commitment_ref is not None:
            object.__setattr__(self, "commitment_ref", _non_empty(self.commitment_ref, field_name="commitment_ref"))
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_type": self.evidence_type,
            "subject": self.subject,
            "correlation_id": self.correlation_id,
            "audit_ref": self.audit_ref,
            "commitment_ref": self.commitment_ref,
            "payload": dict(self.payload),
        }


def core_state_for_runtime(
    runtime_dna: RuntimeDNA,
    *,
    module: ModuleBoundaryName | str,
    status: str,
    budget: float,
    labels: Mapping[str, object] | None = None,
) -> CoreState:
    """Create a canonical core state snapshot from a runtime DNA profile."""

    boundary_name = module if isinstance(module, ModuleBoundaryName) else ModuleBoundaryName(module)
    return CoreState(
        identity_slug=runtime_dna.identity.slug,
        module_boundary=boundary_name,
        runtime_stage=runtime_dna.identity.stage,
        status=status,
        budget=budget,
        labels=labels,
    )


def transfer_envelope_for_state(
    state: CoreState,
    *,
    target_boundary: ModuleBoundaryName | str,
    correlation_id: str,
    schema_version: str = "1.0",
    integrity_status: str = "verified",
    causation_id: str | None = None,
    sequence: int = 0,
) -> TransferEnvelope:
    """Wrap a canonical state object into the standard transfer envelope."""

    boundary_name = target_boundary if isinstance(target_boundary, ModuleBoundaryName) else ModuleBoundaryName(target_boundary)
    return TransferEnvelope(
        schema_version=schema_version,
        payload_type="core-state",
        source_boundary=state.module_boundary,
        target_boundary=boundary_name,
        correlation_id=correlation_id,
        causation_id=causation_id,
        integrity_status=integrity_status,
        sequence=sequence,
        payload=state.to_dict(),
    )
