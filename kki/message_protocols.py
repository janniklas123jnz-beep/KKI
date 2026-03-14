"""Message and event envelope primitives for the build-phase package."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4

from .data_models import EvidenceRecord, TransferEnvelope
from .module_boundaries import ModuleBoundaryName, module_boundary


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


def _default_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class MessageKind(str):
    """Canonical message kinds used across build-phase protocols."""

    COMMAND = "command"
    EVENT = "event"
    TRANSFER = "transfer"
    EVIDENCE = "evidence"


class DeliveryMode(str):
    """Transport mode of a canonical message."""

    SYNC = "sync"
    ASYNC = "async"


class DeliveryGuarantee(str):
    """Delivery contract used by a canonical message."""

    ACKNOWLEDGED = "acknowledged"
    BEST_EFFORT = "best-effort"
    REPLAYABLE = "replayable"
    PROOF_BOUND = "proof-bound"


@dataclass(frozen=True)
class ProtocolContext:
    """Shared protocol metadata for messages and events."""

    correlation_id: str
    idempotency_key: str
    occurred_at: str = field(default_factory=_default_timestamp)
    causation_id: str | None = None
    sequence: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "correlation_id", _non_empty(self.correlation_id, field_name="correlation_id"))
        object.__setattr__(self, "idempotency_key", _non_empty(self.idempotency_key, field_name="idempotency_key"))
        object.__setattr__(self, "occurred_at", _non_empty(self.occurred_at, field_name="occurred_at"))
        if self.causation_id is not None:
            object.__setattr__(self, "causation_id", _non_empty(self.causation_id, field_name="causation_id"))
        if self.sequence < 0:
            raise ValueError("sequence must be >= 0")

    def to_dict(self) -> dict[str, object]:
        return {
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "occurred_at": self.occurred_at,
            "causation_id": self.causation_id,
            "sequence": self.sequence,
        }


@dataclass(frozen=True)
class MessageEnvelope:
    """Canonical message envelope for command, transfer, and evidence flows."""

    schema_version: str
    kind: str
    name: str
    source_boundary: ModuleBoundaryName
    target_boundary: ModuleBoundaryName
    delivery_mode: str
    delivery_guarantee: str
    integrity_status: str
    context: ProtocolContext
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _non_empty(self.schema_version, field_name="schema_version"))
        object.__setattr__(self, "name", _non_empty(self.name, field_name="name"))
        if self.kind not in {
            MessageKind.COMMAND,
            MessageKind.EVENT,
            MessageKind.TRANSFER,
            MessageKind.EVIDENCE,
        }:
            raise ValueError("Unsupported message kind")
        if self.delivery_mode not in {DeliveryMode.SYNC, DeliveryMode.ASYNC}:
            raise ValueError("Unsupported delivery mode")
        if self.delivery_guarantee not in {
            DeliveryGuarantee.ACKNOWLEDGED,
            DeliveryGuarantee.BEST_EFFORT,
            DeliveryGuarantee.REPLAYABLE,
            DeliveryGuarantee.PROOF_BOUND,
        }:
            raise ValueError("Unsupported delivery guarantee")
        if self.integrity_status not in {"verified", "attested", "degraded"}:
            raise ValueError("integrity_status must be one of: verified, attested, degraded")
        module_boundary(self.source_boundary)
        module_boundary(self.target_boundary)
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "name": self.name,
            "source_boundary": self.source_boundary.value,
            "target_boundary": self.target_boundary.value,
            "delivery_mode": self.delivery_mode,
            "delivery_guarantee": self.delivery_guarantee,
            "integrity_status": self.integrity_status,
            "context": self.context.to_dict(),
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class EventEnvelope:
    """Canonical asynchronous event envelope with severity and replay hints."""

    message: MessageEnvelope
    event_class: str
    severity: str
    replayable: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_class", _non_empty(self.event_class, field_name="event_class"))
        if self.severity not in {"info", "warning", "critical"}:
            raise ValueError("severity must be one of: info, warning, critical")
        if self.message.kind != MessageKind.EVENT:
            raise ValueError("EventEnvelope requires a message envelope of kind 'event'")
        if self.message.delivery_mode != DeliveryMode.ASYNC:
            raise ValueError("EventEnvelope requires async delivery mode")

    def to_dict(self) -> dict[str, object]:
        return {
            "message": self.message.to_dict(),
            "event_class": self.event_class,
            "severity": self.severity,
            "replayable": self.replayable,
        }


def protocol_context(
    correlation_id: str,
    *,
    causation_id: str | None = None,
    idempotency_key: str | None = None,
    sequence: int = 0,
) -> ProtocolContext:
    """Create a standard protocol context with automatic idempotency fallback."""

    return ProtocolContext(
        correlation_id=correlation_id,
        causation_id=causation_id,
        idempotency_key=idempotency_key or f"msg-{uuid4().hex}",
        sequence=sequence,
    )


def command_message(
    *,
    name: str,
    source_boundary: ModuleBoundaryName | str,
    target_boundary: ModuleBoundaryName | str,
    correlation_id: str,
    payload: Mapping[str, object],
    causation_id: str | None = None,
    sequence: int = 0,
    schema_version: str = "1.0",
    integrity_status: str = "verified",
) -> MessageEnvelope:
    """Create a canonical synchronous command message."""

    source = source_boundary if isinstance(source_boundary, ModuleBoundaryName) else ModuleBoundaryName(source_boundary)
    target = target_boundary if isinstance(target_boundary, ModuleBoundaryName) else ModuleBoundaryName(target_boundary)
    return MessageEnvelope(
        schema_version=schema_version,
        kind=MessageKind.COMMAND,
        name=name,
        source_boundary=source,
        target_boundary=target,
        delivery_mode=DeliveryMode.SYNC,
        delivery_guarantee=DeliveryGuarantee.ACKNOWLEDGED,
        integrity_status=integrity_status,
        context=protocol_context(correlation_id, causation_id=causation_id, sequence=sequence),
        payload=payload,
    )


def event_message(
    *,
    name: str,
    event_class: str,
    severity: str,
    source_boundary: ModuleBoundaryName | str,
    target_boundary: ModuleBoundaryName | str,
    correlation_id: str,
    payload: Mapping[str, object],
    causation_id: str | None = None,
    sequence: int = 0,
    replayable: bool = True,
    schema_version: str = "1.0",
    integrity_status: str = "verified",
) -> EventEnvelope:
    """Create a canonical asynchronous event envelope."""

    source = source_boundary if isinstance(source_boundary, ModuleBoundaryName) else ModuleBoundaryName(source_boundary)
    target = target_boundary if isinstance(target_boundary, ModuleBoundaryName) else ModuleBoundaryName(target_boundary)
    guarantee = DeliveryGuarantee.REPLAYABLE if replayable else DeliveryGuarantee.BEST_EFFORT
    return EventEnvelope(
        message=MessageEnvelope(
            schema_version=schema_version,
            kind=MessageKind.EVENT,
            name=name,
            source_boundary=source,
            target_boundary=target,
            delivery_mode=DeliveryMode.ASYNC,
            delivery_guarantee=guarantee,
            integrity_status=integrity_status,
            context=protocol_context(correlation_id, causation_id=causation_id, sequence=sequence),
            payload=payload,
        ),
        event_class=event_class,
        severity=severity,
        replayable=replayable,
    )


def transfer_message(
    envelope: TransferEnvelope,
    *,
    name: str,
) -> MessageEnvelope:
    """Wrap a transfer envelope into the canonical transfer message contract."""

    return MessageEnvelope(
        schema_version=envelope.schema_version,
        kind=MessageKind.TRANSFER,
        name=name,
        source_boundary=envelope.source_boundary,
        target_boundary=envelope.target_boundary,
        delivery_mode=DeliveryMode.ASYNC,
        delivery_guarantee=DeliveryGuarantee.REPLAYABLE,
        integrity_status=envelope.integrity_status,
        context=ProtocolContext(
            correlation_id=envelope.correlation_id,
            causation_id=envelope.causation_id,
            idempotency_key=f"transfer-{envelope.correlation_id}-{envelope.sequence}",
            sequence=envelope.sequence,
        ),
        payload=envelope.to_dict(),
    )


def evidence_message(
    evidence: EvidenceRecord,
    *,
    source_boundary: ModuleBoundaryName | str,
    target_boundary: ModuleBoundaryName | str,
    name: str = "evidence-record",
) -> MessageEnvelope:
    """Wrap an evidence record into the canonical evidence message contract."""

    source = source_boundary if isinstance(source_boundary, ModuleBoundaryName) else ModuleBoundaryName(source_boundary)
    target = target_boundary if isinstance(target_boundary, ModuleBoundaryName) else ModuleBoundaryName(target_boundary)
    return MessageEnvelope(
        schema_version="1.0",
        kind=MessageKind.EVIDENCE,
        name=name,
        source_boundary=source,
        target_boundary=target,
        delivery_mode=DeliveryMode.ASYNC,
        delivery_guarantee=DeliveryGuarantee.PROOF_BOUND,
        integrity_status="attested",
        context=ProtocolContext(
            correlation_id=evidence.correlation_id,
            idempotency_key=f"evidence-{evidence.audit_ref}",
        ),
        payload=evidence.to_dict(),
    )
