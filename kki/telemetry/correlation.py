"""Operational telemetry correlation across dispatch, gates, and protocol flow."""

from __future__ import annotations

from dataclasses import dataclass

from kki.governance import GateDecision, GateOutcome
from kki.message_protocols import MessageEnvelope
from kki.module_boundaries import ModuleBoundaryName
from kki.orchestration import DispatchAssignment, DispatchLane
from kki.security.config_loader import LoadedControlPlane
from kki.telemetry.foundation import (
    AuditTrailEntry,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    audit_entry_for_artifact,
    audit_entry_for_message,
    build_telemetry_snapshot,
    telemetry_alert,
)


@dataclass(frozen=True)
class CorrelatedOperation:
    """Correlated runtime view across dispatch, governance, and protocol flow."""

    correlation_id: str
    runtime_stage: str
    message: MessageEnvelope
    dispatch_assignment: DispatchAssignment | None
    gate_decision: GateDecision | None
    signals: tuple[TelemetrySignal, ...]
    alerts: tuple[TelemetryAlert, ...]
    audit_entries: tuple[AuditTrailEntry, ...]
    snapshot: TelemetrySnapshot

    def to_dict(self) -> dict[str, object]:
        return {
            "correlation_id": self.correlation_id,
            "runtime_stage": self.runtime_stage,
            "message": self.message.to_dict(),
            "dispatch_assignment": self.dispatch_assignment.to_dict() if self.dispatch_assignment else None,
            "gate_decision": self.gate_decision.to_dict() if self.gate_decision else None,
            "signals": [signal.to_dict() for signal in self.signals],
            "alerts": [alert.to_dict() for alert in self.alerts],
            "audit_entries": [entry.to_dict() for entry in self.audit_entries],
            "snapshot": self.snapshot.to_dict(),
        }


def dispatch_signal(assignment: DispatchAssignment) -> TelemetrySignal:
    """Project a dispatch assignment into an operational telemetry signal."""

    severity = "warning" if assignment.lane in {DispatchLane.HOLD, DispatchLane.BLOCK} else "info"
    return TelemetrySignal(
        signal_name="dispatch-assignment",
        boundary=assignment.work_unit.boundary,
        correlation_id=assignment.work_unit.correlation_id,
        severity=severity,
        status=assignment.lane.value,
        metrics={
            "priority_score": assignment.priority_score,
            "reserved_budget": assignment.reserved_budget,
            "budget_share": assignment.work_unit.cost_profile.budget_share,
        },
        labels={
            "work_unit_id": assignment.work_unit.unit_id,
            "priority": assignment.work_unit.priority.value,
        },
    )


def gate_signal(decision: GateDecision) -> TelemetrySignal:
    """Project a gate decision into an operational telemetry signal."""

    severity = {
        GateOutcome.GO: "info",
        GateOutcome.HOLD: "warning",
        GateOutcome.BLOCK: "critical",
        GateOutcome.ESCALATE: "warning",
    }[decision.outcome]
    return TelemetrySignal(
        signal_name=decision.gate_name,
        boundary=decision.boundary,
        correlation_id=decision.authorization.to_dict()["message_kind"] + ":" + decision.gate_name,
        severity=severity,
        status=decision.outcome.value,
        metrics={
            "active_controls": len(decision.active_controls),
            "blocker_count": len(decision.blockers),
        },
        labels={
            "action": decision.action.value,
            "operating_mode": decision.operating_mode.value,
            "message_kind": decision.labels.get("message_kind"),
        },
    )


def operation_alerts(
    *,
    message: MessageEnvelope,
    dispatch_assignment: DispatchAssignment | None = None,
    gate_decision: GateDecision | None = None,
) -> tuple[TelemetryAlert, ...]:
    """Create operational alerts from dispatch and gate outcomes."""

    alerts: list[TelemetryAlert] = []
    if dispatch_assignment is not None and dispatch_assignment.lane in {DispatchLane.HOLD, DispatchLane.BLOCK}:
        alerts.append(
            telemetry_alert(
                alert_key=f"{dispatch_assignment.work_unit.unit_id}-dispatch-{dispatch_assignment.lane.value}",
                boundary=dispatch_assignment.work_unit.boundary,
                severity="warning" if dispatch_assignment.lane is DispatchLane.HOLD else "critical",
                summary=dispatch_assignment.rationale,
                observed_value=dispatch_assignment.reserved_budget,
                threshold=dispatch_assignment.work_unit.cost_profile.budget_share,
                correlation_id=dispatch_assignment.work_unit.correlation_id,
            )
        )
    if gate_decision is not None and gate_decision.outcome in {GateOutcome.HOLD, GateOutcome.BLOCK, GateOutcome.ESCALATE}:
        alerts.append(
            telemetry_alert(
                alert_key=f"{message.context.correlation_id}-{gate_decision.outcome.value}",
                boundary=gate_decision.boundary,
                severity="critical" if gate_decision.outcome is GateOutcome.BLOCK else "warning",
                summary=gate_decision.reason,
                observed_value=float(len(gate_decision.blockers) or 1),
                threshold=0.0,
                correlation_id=message.context.correlation_id,
            )
        )
    return tuple(alerts)


def correlate_operation(
    *,
    control_plane: LoadedControlPlane,
    message: MessageEnvelope,
    dispatch_assignment: DispatchAssignment | None = None,
    gate_decision: GateDecision | None = None,
) -> CorrelatedOperation:
    """Build the correlated operational view for a dispatch and governance flow."""

    signals: list[TelemetrySignal] = [
        TelemetrySignal(
            signal_name=message.name,
            boundary=message.target_boundary,
            correlation_id=message.context.correlation_id,
            severity="warning" if message.integrity_status == "degraded" else "info",
            status="observed",
            metrics={"sequence": message.context.sequence},
            labels={
                "source_boundary": message.source_boundary.value,
                "target_boundary": message.target_boundary.value,
                "message_kind": message.kind,
            },
        )
    ]
    if dispatch_assignment is not None:
        signals.append(dispatch_signal(dispatch_assignment))
    if gate_decision is not None:
        gate_corr = gate_signal(gate_decision)
        signals.append(
            TelemetrySignal(
                signal_name=gate_corr.signal_name,
                boundary=gate_corr.boundary,
                correlation_id=message.context.correlation_id,
                severity=gate_corr.severity,
                status=gate_corr.status,
                metrics=gate_corr.metrics,
                labels=gate_corr.labels,
            )
        )

    alerts = operation_alerts(
        message=message,
        dispatch_assignment=dispatch_assignment,
        gate_decision=gate_decision,
    )
    audit_entries = [audit_entry_for_message(message)]
    audit_entries.extend(audit_entry_for_artifact(artifact) for artifact in control_plane.applied_artifacts)
    if dispatch_assignment is not None:
        audit_entries.append(
            AuditTrailEntry(
                entry_type="dispatch-assignment",
                subject=dispatch_assignment.work_unit.unit_id,
                boundary=dispatch_assignment.work_unit.boundary,
                correlation_id=dispatch_assignment.work_unit.correlation_id,
                payload={
                    "lane": dispatch_assignment.lane.value,
                    "rationale": dispatch_assignment.rationale,
                    "priority_score": dispatch_assignment.priority_score,
                },
            )
        )
    if gate_decision is not None:
        audit_entries.append(
            AuditTrailEntry(
                entry_type="gate-decision",
                subject=gate_decision.gate_name,
                boundary=gate_decision.boundary,
                correlation_id=message.context.correlation_id,
                payload={
                    "outcome": gate_decision.outcome.value,
                    "reason": gate_decision.reason,
                    "blockers": list(gate_decision.blockers),
                },
            )
        )

    snapshot = build_telemetry_snapshot(
        runtime_stage=control_plane.runtime_stage,
        signals=tuple(signals),
        alerts=alerts,
        audit_entries=tuple(audit_entries),
        active_controls=tuple(artifact.artifact_id for artifact in control_plane.applied_artifacts),
    )
    return CorrelatedOperation(
        correlation_id=message.context.correlation_id,
        runtime_stage=control_plane.runtime_stage.value,
        message=message,
        dispatch_assignment=dispatch_assignment,
        gate_decision=gate_decision,
        signals=tuple(signals),
        alerts=alerts,
        audit_entries=tuple(audit_entries),
        snapshot=snapshot,
    )
