"""Persistent learning register over tuned policies, evidence, and convergence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .convergence_simulator import ConvergenceSimulator, build_convergence_simulator
from .evidence_ledger import EvidenceLedger, EvidenceLedgerEntry, build_evidence_ledger
from .escalation_router import EscalationRoutePath
from .policy_tuner import PolicyTuneAction, PolicyTuneEntry, PolicyTuner, build_policy_tuner
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class LearningPatternType(str, Enum):
    """Durable learning categories captured from stabilized operations."""

    STABILIZED_INTERVENTION = "stabilized-intervention"
    OPERATING_RECIPE = "operating-recipe"
    RECURRING_PATTERN = "recurring-pattern"


@dataclass(frozen=True)
class LearningRecord:
    """One durable learning artifact derived from policy, evidence, and convergence."""

    record_id: str
    case_id: str
    pattern_type: LearningPatternType
    route_path: EscalationRoutePath
    source_action: PolicyTuneAction
    tuned_threshold: float
    evidence_refs: tuple[str, ...]
    commitment_refs: tuple[str, ...]
    converged_cycle: int
    confidence_score: float
    reusable: bool
    summary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _non_empty(self.record_id, field_name="record_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))
        object.__setattr__(self, "tuned_threshold", _clamp01(self.tuned_threshold))
        object.__setattr__(self, "confidence_score", _clamp01(self.confidence_score))
        object.__setattr__(self, "summary", _non_empty(self.summary, field_name="summary"))
        if self.converged_cycle < 1:
            raise ValueError("converged_cycle must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "record_id": self.record_id,
            "case_id": self.case_id,
            "pattern_type": self.pattern_type.value,
            "route_path": self.route_path.value,
            "source_action": self.source_action.value,
            "tuned_threshold": self.tuned_threshold,
            "evidence_refs": list(self.evidence_refs),
            "commitment_refs": list(self.commitment_refs),
            "converged_cycle": self.converged_cycle,
            "confidence_score": self.confidence_score,
            "reusable": self.reusable,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class LearningRegister:
    """Durable register of stabilized interventions, recipes, and recurring patterns."""

    register_id: str
    policy_tuner: PolicyTuner
    convergence_simulator: ConvergenceSimulator
    evidence_ledger: EvidenceLedger
    records: tuple[LearningRecord, ...]
    register_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_id", _non_empty(self.register_id, field_name="register_id"))

    @property
    def reusable_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.reusable)

    @property
    def intervention_case_ids(self) -> tuple[str, ...]:
        return tuple(
            record.case_id for record in self.records if record.pattern_type is LearningPatternType.STABILIZED_INTERVENTION
        )

    @property
    def recipe_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.pattern_type is LearningPatternType.OPERATING_RECIPE)

    @property
    def recurring_pattern_case_ids(self) -> tuple[str, ...]:
        return tuple(record.case_id for record in self.records if record.pattern_type is LearningPatternType.RECURRING_PATTERN)

    def to_dict(self) -> dict[str, object]:
        return {
            "register_id": self.register_id,
            "policy_tuner": self.policy_tuner.to_dict(),
            "convergence_simulator": self.convergence_simulator.to_dict(),
            "evidence_ledger": self.evidence_ledger.to_dict(),
            "records": [record.to_dict() for record in self.records],
            "register_signal": self.register_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "reusable_case_ids": list(self.reusable_case_ids),
            "intervention_case_ids": list(self.intervention_case_ids),
            "recipe_case_ids": list(self.recipe_case_ids),
            "recurring_pattern_case_ids": list(self.recurring_pattern_case_ids),
        }


def _evidence_entries_by_case(ledger: EvidenceLedger) -> dict[str, tuple[EvidenceLedgerEntry, ...]]:
    return {
        case_id: tuple(entry for entry in ledger.entries if entry.case_id == case_id)
        for case_id in ledger.case_ids
    }


def _pattern_type_for_entry(entry: PolicyTuneEntry) -> LearningPatternType:
    if entry.action is PolicyTuneAction.TIGHTEN:
        return LearningPatternType.STABILIZED_INTERVENTION
    if entry.action is PolicyTuneAction.CALIBRATE:
        return LearningPatternType.OPERATING_RECIPE
    return LearningPatternType.RECURRING_PATTERN


def _confidence_score(
    evidence_entries: tuple[EvidenceLedgerEntry, ...],
    *,
    converged_cycle: int,
    source_action: PolicyTuneAction,
) -> float:
    base = {
        PolicyTuneAction.TIGHTEN: 0.78,
        PolicyTuneAction.CALIBRATE: 0.72,
        PolicyTuneAction.RELAX: 0.68,
    }[source_action]
    evidence_bonus = min(0.18, len(evidence_entries) * 0.02)
    convergence_bonus = min(0.08, 0.02 * converged_cycle)
    return _clamp01(round(base + evidence_bonus + convergence_bonus, 3))


def build_learning_register(
    policy_tuner: PolicyTuner | None = None,
    convergence_simulator: ConvergenceSimulator | None = None,
    evidence_ledger: EvidenceLedger | None = None,
    *,
    register_id: str = "learning-register",
) -> LearningRegister:
    """Build a durable learning register from stabilized policy and evidence flows."""

    resolved_tuner = build_policy_tuner(tuner_id=f"{register_id}-tuner") if policy_tuner is None else policy_tuner
    resolved_simulator = (
        build_convergence_simulator(simulator_id=f"{register_id}-simulator")
        if convergence_simulator is None
        else convergence_simulator
    )
    resolved_ledger = build_evidence_ledger(ledger_id=f"{register_id}-ledger") if evidence_ledger is None else evidence_ledger

    converged_cycle = resolved_simulator.converged_cycle_index or len(resolved_simulator.projections)
    evidence_entries_by_case = _evidence_entries_by_case(resolved_ledger)
    records = tuple(
        LearningRecord(
            record_id=f"{register_id}-{entry.case_id}",
            case_id=entry.case_id,
            pattern_type=_pattern_type_for_entry(entry),
            route_path=entry.route_path,
            source_action=entry.action,
            tuned_threshold=entry.tuned_threshold,
            evidence_refs=tuple(dict.fromkeys(ref for item in evidence_entries_by_case[entry.case_id] for ref in item.audit_refs)),
            commitment_refs=tuple(
                dict.fromkeys(ref for item in evidence_entries_by_case[entry.case_id] for ref in item.commitment_refs)
            ),
            converged_cycle=converged_cycle,
            confidence_score=_confidence_score(
                evidence_entries_by_case[entry.case_id],
                converged_cycle=converged_cycle,
                source_action=entry.action,
            ),
            reusable=entry.case_id in resolved_simulator.final_ready_case_ids,
            summary=(
                f"{entry.case_id} is retained as a { _pattern_type_for_entry(entry).value } "
                f"for {entry.route_path.value} with threshold {entry.tuned_threshold:.2f}."
            ),
        )
        for entry in resolved_tuner.entries
    )
    if not records:
        raise ValueError("learning register requires at least one record")

    severity = "info"
    status = "learning-captured"
    if any(record.pattern_type is LearningPatternType.STABILIZED_INTERVENTION for record in records):
        severity = "warning"
        status = "interventions-captured"
    if all(record.reusable for record in records):
        severity = "info"
        status = "reusable-learning"

    register_signal = TelemetrySignal(
        signal_name="learning-register",
        boundary=resolved_tuner.tuner_signal.boundary,
        correlation_id=register_id,
        severity=severity,
        status=status,
        metrics={
            "record_count": float(len(records)),
            "intervention_count": float(
                len([record for record in records if record.pattern_type is LearningPatternType.STABILIZED_INTERVENTION])
            ),
            "recipe_count": float(len([record for record in records if record.pattern_type is LearningPatternType.OPERATING_RECIPE])),
            "pattern_count": float(len([record for record in records if record.pattern_type is LearningPatternType.RECURRING_PATTERN])),
            "reusable_count": float(len([record for record in records if record.reusable])),
            "avg_confidence": round(sum(record.confidence_score for record in records) / len(records), 3),
        },
        labels={"register_id": register_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_simulator.final_snapshot.runtime_stage,
        signals=(
            register_signal,
            resolved_tuner.tuner_signal,
            resolved_simulator.simulator_signal,
            resolved_ledger.ledger_signal,
            *resolved_simulator.final_snapshot.signals,
        ),
        alerts=resolved_simulator.final_snapshot.alerts,
        audit_entries=resolved_simulator.final_snapshot.audit_entries,
        active_controls=resolved_simulator.final_snapshot.active_controls,
    )
    return LearningRegister(
        register_id=register_id,
        policy_tuner=resolved_tuner,
        convergence_simulator=resolved_simulator,
        evidence_ledger=resolved_ledger,
        records=records,
        register_signal=register_signal,
        final_snapshot=final_snapshot,
    )
