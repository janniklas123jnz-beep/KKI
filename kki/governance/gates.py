"""Executable gate and policy decisions for operational build-phase flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.message_protocols import MessageEnvelope, MessageKind
from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.orchestration.dispatch import DispatchAssignment, DispatchLane
from kki.security.authorization import (
    ActionName,
    AuthorizationDecision,
    AuthorizationIdentity,
    OperatingMode,
    authorize_action,
)
from kki.security.config_loader import LoadedControlPlane


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


class GateOutcome(str, Enum):
    """Resolved operational gate outcome."""

    GO = "go"
    HOLD = "hold"
    BLOCK = "block"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class GateDecision:
    """Explicit gate result combining policy, authorization, and dispatch context."""

    gate_name: str
    outcome: GateOutcome
    boundary: ModuleBoundaryName
    action: ActionName
    operating_mode: OperatingMode
    reason: str
    authorization: AuthorizationDecision
    evidence_required: bool
    commitment_required: bool
    escalation_required: bool
    active_controls: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_name", _non_empty(self.gate_name, field_name="gate_name"))
        object.__setattr__(self, "reason", _non_empty(self.reason, field_name="reason"))
        module_boundary(self.boundary)
        cleaned_controls = tuple(control.strip() for control in self.active_controls if control.strip())
        cleaned_blockers = tuple(blocker.strip() for blocker in self.blockers if blocker.strip())
        object.__setattr__(self, "active_controls", cleaned_controls)
        object.__setattr__(self, "blockers", cleaned_blockers)
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))
        if self.outcome is GateOutcome.BLOCK and not cleaned_blockers:
            raise ValueError("blocked gate decisions require blockers")

    def to_dict(self) -> dict[str, object]:
        return {
            "gate_name": self.gate_name,
            "outcome": self.outcome.value,
            "boundary": self.boundary.value,
            "action": self.action.value,
            "operating_mode": self.operating_mode.value,
            "reason": self.reason,
            "authorization": self.authorization.to_dict(),
            "evidence_required": self.evidence_required,
            "commitment_required": self.commitment_required,
            "escalation_required": self.escalation_required,
            "active_controls": list(self.active_controls),
            "blockers": list(self.blockers),
            "labels": dict(self.labels),
        }


def _resolve_action(boundary: ModuleBoundaryName) -> ActionName:
    if boundary is ModuleBoundaryName.RECOVERY:
        return ActionName.RECOVER
    if boundary in {ModuleBoundaryName.ROLLOUT, ModuleBoundaryName.GOVERNANCE, ModuleBoundaryName.SECURITY}:
        return ActionName.APPROVE
    return ActionName.EXECUTE


def _gate_name(boundary: ModuleBoundaryName) -> str:
    return f"{boundary.value}-gate"


def _critical_controls(control_plane: LoadedControlPlane) -> tuple[str, ...]:
    return tuple(
        artifact.artifact_id
        for artifact in control_plane.applied_artifacts
        if artifact.critical or artifact.kind.value in {"policy", "emergency-override"}
    )


def evaluate_gate(
    identity: AuthorizationIdentity,
    *,
    boundary: ModuleBoundaryName | str,
    control_plane: LoadedControlPlane,
    message: MessageEnvelope,
    action: ActionName | str | None = None,
    dispatch_assignment: DispatchAssignment | None = None,
    operating_mode: OperatingMode | str = OperatingMode.NORMAL,
    evidence_ref: str | None = None,
    commitment_ref: str | None = None,
) -> GateDecision:
    """Evaluate a concrete Go/No-Go decision for an operational boundary."""

    boundary_name = boundary if isinstance(boundary, ModuleBoundaryName) else ModuleBoundaryName(boundary)
    mode = operating_mode if isinstance(operating_mode, OperatingMode) else OperatingMode(operating_mode)
    resolved_action = action if isinstance(action, ActionName) else ActionName(action) if action is not None else _resolve_action(boundary_name)
    authorization = authorize_action(
        identity,
        action=resolved_action,
        boundary=boundary_name,
        operating_mode=mode,
        message=message,
        evidence_ref=evidence_ref,
        commitment_ref=commitment_ref,
    )

    critical_controls = _critical_controls(control_plane)
    blockers: list[str] = []
    outcome = GateOutcome.GO
    reason = "gate approved"

    if not authorization.allowed:
        outcome = GateOutcome.BLOCK
        blockers.append(authorization.reason)
        reason = "authorization denied for gate"
    elif dispatch_assignment is not None and dispatch_assignment.lane is DispatchLane.BLOCK:
        outcome = GateOutcome.BLOCK
        blockers.append(dispatch_assignment.rationale)
        reason = "dispatch planner blocked this work unit"
    elif dispatch_assignment is not None and dispatch_assignment.lane in {DispatchLane.HOLD, DispatchLane.DEFER}:
        outcome = GateOutcome.HOLD
        blockers.append(dispatch_assignment.rationale)
        reason = "dispatch planner requested hold before execution"
    elif message.integrity_status == "degraded":
        outcome = GateOutcome.HOLD
        blockers.append("message integrity is degraded")
        reason = "gate requires verified or attested message integrity"
    elif boundary_name is ModuleBoundaryName.ROLLOUT and control_plane.effective_payload.get("promotion_gate") == "hold-until-shadow-green":
        if dispatch_assignment is not None and dispatch_assignment.lane is not DispatchLane.ADMIT:
            outcome = GateOutcome.HOLD
            blockers.append("rollout policy requires admitted shadow-green work before promotion")
            reason = "policy holds rollout until admitted shadow-green execution"
    elif boundary_name is ModuleBoundaryName.SHADOW and control_plane.effective_payload.get("preview_gate") == "strict":
        if message.kind != MessageKind.COMMAND:
            outcome = GateOutcome.BLOCK
            blockers.append("strict shadow preview accepts command messages only")
            reason = "shadow policy rejected non-command preview request"

    if authorization.escalation_required:
        outcome = GateOutcome.ESCALATE if outcome is GateOutcome.GO else outcome
        if outcome is GateOutcome.ESCALATE:
            reason = "gate requires escalation before execution"

    return GateDecision(
        gate_name=_gate_name(boundary_name),
        outcome=outcome,
        boundary=boundary_name,
        action=resolved_action,
        operating_mode=mode,
        reason=reason,
        authorization=authorization,
        evidence_required=authorization.requires_evidence,
        commitment_required=authorization.requires_commitment,
        escalation_required=authorization.escalation_required or outcome is GateOutcome.ESCALATE,
        active_controls=critical_controls,
        blockers=tuple(blockers),
        labels={
            "message_name": message.name,
            "message_kind": message.kind,
            "dispatch_lane": dispatch_assignment.lane.value if dispatch_assignment else None,
        },
    )
