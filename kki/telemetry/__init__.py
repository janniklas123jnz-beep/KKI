"""Telemetry boundary for audit, diagnostics, and evidence flows."""

from kki.module_boundaries import ModuleBoundary, module_boundary
from kki.telemetry.foundation import (
    AuditTrailEntry,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    audit_entry_for_artifact,
    audit_entry_for_message,
    build_telemetry_snapshot,
    telemetry_alert,
    telemetry_signal_from_event,
)
from kki.telemetry.correlation import (
    CorrelatedOperation,
    correlate_operation,
    dispatch_signal,
    gate_signal,
    operation_alerts,
)

BOUNDARY: ModuleBoundary = module_boundary("telemetry")

__all__ = [
    "AuditTrailEntry",
    "BOUNDARY",
    "CorrelatedOperation",
    "TelemetryAlert",
    "TelemetrySignal",
    "TelemetrySnapshot",
    "audit_entry_for_artifact",
    "audit_entry_for_message",
    "build_telemetry_snapshot",
    "correlate_operation",
    "dispatch_signal",
    "gate_signal",
    "operation_alerts",
    "telemetry_alert",
    "telemetry_signal_from_event",
]
