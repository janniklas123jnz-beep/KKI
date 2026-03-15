"""Integrated operational run across orchestration, shadow, rollout, recovery, and governance."""

from __future__ import annotations

from dataclasses import dataclass

from .governance import HumanDecision, HumanLoopGovernance, govern_recovery_orchestration
from .orchestration import OrchestrationState, WorkPriority, WorkUnit, orchestration_state_for_runtime, work_unit_for_state
from .recovery import RecoveryOrchestration, orchestrate_recovery_for_rollout
from .rollout import RolloutPhase, RolloutState, advance_rollout_state, rollout_state_for_shadow
from .runtime_dna import RuntimeDNA, RuntimeStage, runtime_dna_for_profile
from .security import (
    ArtifactKind,
    ArtifactScope,
    AuthorizationIdentity,
    ControlArtifact,
    IdentityKind,
    LoadedControlPlane,
    RoleName,
    TrustLevel,
    ValidationStep,
    load_control_plane,
)
from .shadow import ShadowCoordination, coordinate_shadow_work
from .telemetry import TelemetrySnapshot, build_telemetry_snapshot


@dataclass(frozen=True)
class IntegratedOperationsRun:
    """End-to-end integrated operational run over the full operative core chain."""

    runtime_dna: RuntimeDNA
    shadow_control_plane: LoadedControlPlane
    rollout_control_plane: LoadedControlPlane
    recovery_control_plane: LoadedControlPlane
    governance_control_plane: LoadedControlPlane
    orchestration_state: OrchestrationState
    work_unit: WorkUnit
    shadow_coordination: ShadowCoordination
    rollout_state: RolloutState
    recovery_orchestration: RecoveryOrchestration
    human_governance: HumanLoopGovernance
    final_snapshot: TelemetrySnapshot

    @property
    def success(self) -> bool:
        return (
            self.shadow_coordination.release_ready
            and self.rollout_state.promotion_ready
            and self.recovery_orchestration.resume_ready
            and self.human_governance.release_authorized
            and self.final_snapshot.highest_severity() != "critical"
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "runtime_dna": self.runtime_dna.to_dict(),
            "shadow_control_plane": self.shadow_control_plane.to_dict(),
            "rollout_control_plane": self.rollout_control_plane.to_dict(),
            "recovery_control_plane": self.recovery_control_plane.to_dict(),
            "governance_control_plane": self.governance_control_plane.to_dict(),
            "orchestration_state": self.orchestration_state.to_dict(),
            "work_unit": self.work_unit.to_dict(),
            "shadow_coordination": self.shadow_coordination.to_dict(),
            "rollout_state": self.rollout_state.to_dict(),
            "recovery_orchestration": self.recovery_orchestration.to_dict(),
            "human_governance": self.human_governance.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "success": self.success,
        }


def _operational_control_artifacts(stage: RuntimeStage) -> tuple[ControlArtifact, ...]:
    validations = (
        ValidationStep.STATIC,
        ValidationStep.CONSISTENCY,
        ValidationStep.SHADOW,
    )
    return (
        ControlArtifact(
            artifact_id="runtime-budget",
            kind=ArtifactKind.BASE_CONFIG,
            version="1.2",
            scope=ArtifactScope.GLOBAL,
            rollback_version="1.1",
            payload={"resource_budget": 0.8, "shadow_enabled": True, "operations_run": True},
        ),
        ControlArtifact(
            artifact_id="pilot-runtime",
            kind=ArtifactKind.BASE_CONFIG,
            version="1.3",
            scope=ArtifactScope.STAGE,
            runtime_stage=stage,
            validations=validations,
            rollback_version="1.2",
            payload={"resource_budget": 0.82, "recovery_reserve": 0.2},
        ),
        ControlArtifact(
            artifact_id="shadow-policy",
            kind=ArtifactKind.POLICY,
            version="2.1",
            scope=ArtifactScope.BOUNDARY,
            runtime_stage=stage,
            boundary="shadow",
            validations=validations,
            evidence_ref="audit-shadow-policy",
            rollback_version="2.0",
            payload={"preview_gate": "strict", "drift_threshold": 0.05},
        ),
        ControlArtifact(
            artifact_id="rollout-policy",
            kind=ArtifactKind.POLICY,
            version="2.2",
            scope=ArtifactScope.BOUNDARY,
            runtime_stage=stage,
            boundary="rollout",
            validations=validations,
            evidence_ref="audit-rollout-policy",
            rollback_version="2.1",
            payload={"promotion_gate": "hold-until-shadow-green"},
        ),
    )


def run_integrated_operations(
    *,
    profile: str = "pilot-runtime-dna",
    stage: RuntimeStage = RuntimeStage.PILOT,
    correlation_id: str = "integrated-operations",
) -> IntegratedOperationsRun:
    """Execute the canonical integrated operations run across the full operative core chain."""

    runtime_dna = runtime_dna_for_profile(profile, stage=stage)
    artifacts = _operational_control_artifacts(stage)
    shadow_control_plane = load_control_plane(artifacts, runtime_stage=stage, boundary="shadow")
    rollout_control_plane = load_control_plane(artifacts, runtime_stage=stage, boundary="rollout")
    recovery_control_plane = load_control_plane(artifacts, runtime_stage=stage, boundary="recovery")
    governance_control_plane = load_control_plane(artifacts, runtime_stage=stage, boundary="governance")

    orchestration_state = orchestration_state_for_runtime(
        runtime_dna,
        mission_ref="operations-run",
    )
    work_unit = work_unit_for_state(
        orchestration_state,
        title="integrated operations run",
        boundary="rollout",
        correlation_id=correlation_id,
        priority=WorkPriority.HIGH,
        budget_share=0.12,
    )

    shadow_identity = AuthorizationIdentity(
        slug="executor-shadow",
        kind=IdentityKind.MODULE,
        role=RoleName.EXECUTOR,
        trust_level=TrustLevel.VERIFIED,
        boundary_scope=("shadow", "rollout"),
    )
    rollout_identity = AuthorizationIdentity(
        slug="gatekeeper-rollout",
        kind=IdentityKind.OPERATOR,
        role=RoleName.GATEKEEPER,
        trust_level=TrustLevel.VERIFIED,
        boundary_scope=("rollout", "governance"),
    )
    recovery_identity = AuthorizationIdentity(
        slug="supervisor-recovery",
        kind=IdentityKind.SUPERVISOR,
        role=RoleName.SUPERVISOR,
        trust_level=TrustLevel.PRIVILEGED,
        boundary_scope=("recovery", "rollout"),
    )
    governance_identity = AuthorizationIdentity(
        slug="gatekeeper-governance",
        kind=IdentityKind.OPERATOR,
        role=RoleName.GATEKEEPER,
        trust_level=TrustLevel.VERIFIED,
        boundary_scope=("governance", "rollout"),
    )

    shadow_coordination = coordinate_shadow_work(
        orchestration_state,
        work_unit,
        control_plane=shadow_control_plane,
        identity=shadow_identity,
        available_roles=(RoleName.EXECUTOR,),
        observed_budget=0.12,
    )
    rollout_state = rollout_state_for_shadow(
        shadow_coordination,
        control_plane=rollout_control_plane,
        identity=rollout_identity,
        evidence_ref="audit-rollout-policy",
    )
    if rollout_state.phase is RolloutPhase.PROMOTING:
        rollout_state = advance_rollout_state(
            rollout_state,
            phase=RolloutPhase.CANARY,
            labels={"integrated_operations": True},
        )
    recovery_orchestration = orchestrate_recovery_for_rollout(
        rollout_state,
        control_plane=recovery_control_plane,
        identity=recovery_identity,
        evidence_ref=f"audit-{correlation_id}-recovery",
    )
    human_governance = govern_recovery_orchestration(
        recovery_orchestration,
        control_plane=governance_control_plane,
        identity=governance_identity,
        decision=HumanDecision.APPROVE,
        audit_ref=f"audit-{correlation_id}-governance",
    )

    final_snapshot = build_telemetry_snapshot(
        runtime_stage=stage,
        signals=(
            shadow_coordination.release_signal,
            rollout_state.promotion_signal,
            recovery_orchestration.recovery_signal,
            human_governance.governance_signal,
        ),
        alerts=(
            *shadow_coordination.correlation.alerts,
            *rollout_state.correlation.alerts,
            *recovery_orchestration.correlation.alerts,
            *human_governance.correlation.alerts,
        ),
        audit_entries=(
            *shadow_coordination.correlation.audit_entries,
            *rollout_state.correlation.audit_entries,
            *recovery_orchestration.outcome.snapshot.audit_entries,
            *human_governance.correlation.audit_entries,
        ),
        active_controls=tuple(
            dict.fromkeys(
                [artifact.artifact_id for artifact in shadow_control_plane.applied_artifacts]
                + [artifact.artifact_id for artifact in rollout_control_plane.applied_artifacts]
                + [artifact.artifact_id for artifact in recovery_control_plane.applied_artifacts]
                + [artifact.artifact_id for artifact in governance_control_plane.applied_artifacts]
            )
        ),
    )

    return IntegratedOperationsRun(
        runtime_dna=runtime_dna,
        shadow_control_plane=shadow_control_plane,
        rollout_control_plane=rollout_control_plane,
        recovery_control_plane=recovery_control_plane,
        governance_control_plane=governance_control_plane,
        orchestration_state=orchestration_state,
        work_unit=work_unit,
        shadow_coordination=shadow_coordination,
        rollout_state=rollout_state,
        recovery_orchestration=recovery_orchestration,
        human_governance=human_governance,
        final_snapshot=final_snapshot,
    )
