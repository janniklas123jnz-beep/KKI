"""Federated coordination across multiple steward contexts and domains."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .autonomy_governor import AutonomyDecision, AutonomyGovernor, build_autonomy_governor
from .intervention_simulator import (
    InterventionSimulation,
    InterventionSimulationStatus,
    InterventionSimulator,
    build_intervention_simulator,
)
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class FederationDomain(str, Enum):
    """Cross-domain operating contexts inside the federated steward model."""

    RESILIENCE = "resilience"
    GOVERNANCE = "governance"
    AUTONOMY = "autonomy"


class FederationAlignmentStatus(str, Enum):
    """Alignment state of one federated domain cell."""

    ESCALATED = "escalated"
    HANDOFF_REQUIRED = "handoff-required"
    ALIGNED = "aligned"


class FederationHandoffPriority(str, Enum):
    """Priority for a cross-domain coordination handoff."""

    CRITICAL = "critical"
    PLANNED = "planned"


@dataclass(frozen=True)
class FederationCell:
    """One federated operating cell coordinating a group of cases."""

    cell_id: str
    domain: FederationDomain
    sequence: int
    case_ids: tuple[str, ...]
    alignment_status: FederationAlignmentStatus
    control_tags: tuple[str, ...]
    coordination_actions: tuple[str, ...]
    shared_risk_score: float
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "cell_id", _non_empty(self.cell_id, field_name="cell_id"))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        object.__setattr__(self, "shared_risk_score", _clamp01(self.shared_risk_score))
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "cell_id": self.cell_id,
            "domain": self.domain.value,
            "sequence": self.sequence,
            "case_ids": list(self.case_ids),
            "alignment_status": self.alignment_status.value,
            "control_tags": list(self.control_tags),
            "coordination_actions": list(self.coordination_actions),
            "shared_risk_score": self.shared_risk_score,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class FederationHandoff:
    """Tracked handoff between federated domain cells."""

    handoff_id: str
    source_domain: FederationDomain
    target_domain: FederationDomain
    case_ids: tuple[str, ...]
    priority: FederationHandoffPriority
    reason: str
    control_tags: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "handoff_id", _non_empty(self.handoff_id, field_name="handoff_id"))
        object.__setattr__(self, "reason", _non_empty(self.reason, field_name="reason"))
        if not self.case_ids:
            raise ValueError("case_ids must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "handoff_id": self.handoff_id,
            "source_domain": self.source_domain.value,
            "target_domain": self.target_domain.value,
            "case_ids": list(self.case_ids),
            "priority": self.priority.value,
            "reason": self.reason,
            "control_tags": list(self.control_tags),
        }


@dataclass(frozen=True)
class FederationCoordination:
    """Federated coordination across resilience, governance, and autonomy cells."""

    coordination_id: str
    intervention_simulator: InterventionSimulator
    autonomy_governor: AutonomyGovernor
    cells: tuple[FederationCell, ...]
    handoffs: tuple[FederationHandoff, ...]
    coordination_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordination_id", _non_empty(self.coordination_id, field_name="coordination_id"))

    @property
    def escalated_domains(self) -> tuple[FederationDomain, ...]:
        return tuple(cell.domain for cell in self.cells if cell.alignment_status is FederationAlignmentStatus.ESCALATED)

    @property
    def handoff_domains(self) -> tuple[FederationDomain, ...]:
        return tuple(cell.domain for cell in self.cells if cell.alignment_status is FederationAlignmentStatus.HANDOFF_REQUIRED)

    @property
    def aligned_domains(self) -> tuple[FederationDomain, ...]:
        return tuple(cell.domain for cell in self.cells if cell.alignment_status is FederationAlignmentStatus.ALIGNED)

    def to_dict(self) -> dict[str, object]:
        return {
            "coordination_id": self.coordination_id,
            "intervention_simulator": self.intervention_simulator.to_dict(),
            "autonomy_governor": self.autonomy_governor.to_dict(),
            "cells": [cell.to_dict() for cell in self.cells],
            "handoffs": [handoff.to_dict() for handoff in self.handoffs],
            "coordination_signal": self.coordination_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "escalated_domains": [domain.value for domain in self.escalated_domains],
            "handoff_domains": [domain.value for domain in self.handoff_domains],
            "aligned_domains": [domain.value for domain in self.aligned_domains],
        }


def _domain_for_simulation(simulation: InterventionSimulation) -> FederationDomain:
    if simulation.projected_status in {
        InterventionSimulationStatus.AT_RISK,
        InterventionSimulationStatus.ROLLBACK_RECOMMENDED,
    }:
        return FederationDomain.RESILIENCE
    if simulation.autonomy_decision is AutonomyDecision.GOVERNANCE_REQUIRED:
        return FederationDomain.GOVERNANCE
    return FederationDomain.AUTONOMY


def _alignment_for_domain(
    domain: FederationDomain,
    simulations: tuple[InterventionSimulation, ...],
) -> FederationAlignmentStatus:
    if domain is FederationDomain.RESILIENCE:
        if any(item.projected_status is InterventionSimulationStatus.ROLLBACK_RECOMMENDED for item in simulations):
            return FederationAlignmentStatus.ESCALATED
        return FederationAlignmentStatus.HANDOFF_REQUIRED
    if domain is FederationDomain.GOVERNANCE:
        return FederationAlignmentStatus.HANDOFF_REQUIRED
    return FederationAlignmentStatus.ALIGNED


def _coordination_actions(
    domain: FederationDomain,
    status: FederationAlignmentStatus,
) -> tuple[str, ...]:
    if domain is FederationDomain.RESILIENCE:
        if status is FederationAlignmentStatus.ESCALATED:
            return ("rollback-sync", "manual-recovery-bridge", "exception-broadcast")
        return ("recovery-bridge", "follow-up-sync", "shared-watch")
    if domain is FederationDomain.GOVERNANCE:
        return ("approval-sync", "change-window-link", "policy-confirmation")
    return ("telemetry-sync", "bounded-autonomy-window", "cross-domain-watch")


def _build_cells(
    coordination_id: str,
    simulations: tuple[InterventionSimulation, ...],
) -> tuple[FederationCell, ...]:
    domain_order = (
        FederationDomain.RESILIENCE,
        FederationDomain.GOVERNANCE,
        FederationDomain.AUTONOMY,
    )
    cells: list[FederationCell] = []
    for sequence, domain in enumerate(domain_order, start=1):
        domain_simulations = tuple(item for item in simulations if _domain_for_simulation(item) is domain)
        if not domain_simulations:
            continue
        alignment = _alignment_for_domain(domain, domain_simulations)
        cells.append(
            FederationCell(
                cell_id=f"{coordination_id}-{domain.value}",
                domain=domain,
                sequence=sequence,
                case_ids=tuple(item.case_id for item in domain_simulations),
                alignment_status=alignment,
                control_tags=tuple(dict.fromkeys(tag for item in domain_simulations for tag in item.control_tags)),
                coordination_actions=_coordination_actions(domain, alignment),
                shared_risk_score=round(
                    sum(item.projected_risk_score for item in domain_simulations) / len(domain_simulations),
                    3,
                ),
                summary=f"{domain.value} cell coordinates {len(domain_simulations)} federated intervention case(s).",
            )
        )
    return tuple(cells)


def _build_handoffs(
    coordination_id: str,
    cells: tuple[FederationCell, ...],
) -> tuple[FederationHandoff, ...]:
    cell_by_domain = {cell.domain: cell for cell in cells}
    handoffs: list[FederationHandoff] = []
    resilience_cell = cell_by_domain.get(FederationDomain.RESILIENCE)
    governance_cell = cell_by_domain.get(FederationDomain.GOVERNANCE)
    autonomy_cell = cell_by_domain.get(FederationDomain.AUTONOMY)
    if resilience_cell is not None and governance_cell is not None:
        handoffs.append(
            FederationHandoff(
                handoff_id=f"{coordination_id}-resilience-to-governance",
                source_domain=FederationDomain.RESILIENCE,
                target_domain=FederationDomain.GOVERNANCE,
                case_ids=resilience_cell.case_ids,
                priority=FederationHandoffPriority.CRITICAL,
                reason="Critical and unresolved cases must stay visible in governance review windows.",
                control_tags=("exception-broadcast", "approval-sync"),
            )
        )
    if governance_cell is not None and autonomy_cell is not None:
        handoffs.append(
            FederationHandoff(
                handoff_id=f"{coordination_id}-governance-to-autonomy",
                source_domain=FederationDomain.GOVERNANCE,
                target_domain=FederationDomain.AUTONOMY,
                case_ids=autonomy_cell.case_ids,
                priority=FederationHandoffPriority.PLANNED,
                reason="Approved routine playbooks are handed into the bounded autonomy window.",
                control_tags=("change-window-link", "bounded-autonomy-window"),
            )
        )
    return tuple(handoffs)


def build_federation_coordination(
    intervention_simulator: InterventionSimulator | None = None,
    autonomy_governor: AutonomyGovernor | None = None,
    *,
    coordination_id: str = "federation-coordination",
) -> FederationCoordination:
    """Build federated coordination across multiple steward contexts."""

    resolved_simulator = (
        build_intervention_simulator(simulator_id=f"{coordination_id}-simulator")
        if intervention_simulator is None
        else intervention_simulator
    )
    resolved_governor = (
        resolved_simulator.autonomy_governor
        if autonomy_governor is None
        else autonomy_governor
    )
    cells = _build_cells(coordination_id, resolved_simulator.simulations)
    if not cells:
        raise ValueError("federation coordination requires at least one cell")
    handoffs = _build_handoffs(coordination_id, cells)

    severity = "info"
    status = "federated-aligned"
    if any(cell.alignment_status is FederationAlignmentStatus.ESCALATED for cell in cells):
        severity = "critical"
        status = "federated-escalation"
    elif any(cell.alignment_status is FederationAlignmentStatus.HANDOFF_REQUIRED for cell in cells):
        severity = "warning"
        status = "federated-handoff"

    coordination_signal = TelemetrySignal(
        signal_name="federation-coordination",
        boundary=resolved_governor.governor_signal.boundary,
        correlation_id=coordination_id,
        severity=severity,
        status=status,
        metrics={
            "cell_count": float(len(cells)),
            "handoff_count": float(len(handoffs)),
            "escalated_domain_count": float(
                len([cell for cell in cells if cell.alignment_status is FederationAlignmentStatus.ESCALATED])
            ),
            "aligned_domain_count": float(
                len([cell for cell in cells if cell.alignment_status is FederationAlignmentStatus.ALIGNED])
            ),
        },
        labels={"coordination_id": coordination_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_simulator.final_snapshot.runtime_stage,
        signals=(
            coordination_signal,
            resolved_simulator.simulator_signal,
            resolved_governor.governor_signal,
            *resolved_simulator.final_snapshot.signals,
        ),
        alerts=resolved_simulator.final_snapshot.alerts,
        audit_entries=resolved_simulator.final_snapshot.audit_entries,
        active_controls=resolved_simulator.final_snapshot.active_controls,
    )
    return FederationCoordination(
        coordination_id=coordination_id,
        intervention_simulator=resolved_simulator,
        autonomy_governor=resolved_governor,
        cells=cells,
        handoffs=handoffs,
        coordination_signal=coordination_signal,
        final_snapshot=final_snapshot,
    )
