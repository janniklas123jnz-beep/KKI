"""Integrated smoke-build path for the build-phase foundation package."""

from __future__ import annotations

from dataclasses import dataclass

from .data_models import CoreState, core_state_for_runtime
from .message_protocols import EventEnvelope, MessageEnvelope, command_message
from .recovery import (
    RecoveryCheckpoint,
    RecoveryOutcome,
    RollbackDirective,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
)
from .runtime_dna import RuntimeDNA, RuntimeStage, runtime_dna_for_profile
from .security import (
    ArtifactKind,
    ArtifactScope,
    ControlArtifact,
    LoadedControlPlane,
    ValidationStep,
    load_control_plane,
)
from .shadow import (
    DryRunEvaluation,
    ShadowPreview,
    evaluate_dry_run,
    shadow_event,
    shadow_preview_for_command,
    shadow_snapshot,
)
from .telemetry import (
    TelemetrySignal,
    TelemetrySnapshot,
    audit_entry_for_message,
    build_telemetry_snapshot,
    telemetry_signal_from_event,
)


@dataclass(frozen=True)
class IntegratedSmokeBuild:
    """End-to-end integrated smoke-build result for the build-phase foundation."""

    runtime_dna: RuntimeDNA
    control_plane: LoadedControlPlane
    orchestration_state: CoreState
    shadow_command: MessageEnvelope
    shadow_preview: ShadowPreview
    dry_run_evaluation: DryRunEvaluation
    shadow_event: EventEnvelope
    recovery_checkpoint: RecoveryCheckpoint
    rollback_directive: RollbackDirective
    recovery_outcome: RecoveryOutcome
    final_snapshot: TelemetrySnapshot

    @property
    def success(self) -> bool:
        return (
            self.dry_run_evaluation.replay_ready
            and self.recovery_outcome.replay_ready
            and self.final_snapshot.highest_severity() != "critical"
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "runtime_dna": self.runtime_dna.to_dict(),
            "control_plane": self.control_plane.to_dict(),
            "orchestration_state": self.orchestration_state.to_dict(),
            "shadow_command": self.shadow_command.to_dict(),
            "shadow_preview": self.shadow_preview.to_dict(),
            "dry_run_evaluation": self.dry_run_evaluation.to_dict(),
            "shadow_event": self.shadow_event.to_dict(),
            "recovery_checkpoint": self.recovery_checkpoint.to_dict(),
            "rollback_directive": self.rollback_directive.to_dict(),
            "recovery_outcome": self.recovery_outcome.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "success": self.success,
        }


def _integrated_control_artifacts(stage: RuntimeStage) -> tuple[ControlArtifact, ...]:
    validations = (
        ValidationStep.STATIC,
        ValidationStep.CONSISTENCY,
        ValidationStep.SHADOW,
    )
    return (
        ControlArtifact(
            artifact_id="runtime-budget",
            kind=ArtifactKind.BASE_CONFIG,
            version="1.0",
            scope=ArtifactScope.GLOBAL,
            rollback_version="0.9",
            payload={"resource_budget": 0.74, "shadow_enabled": True},
        ),
        ControlArtifact(
            artifact_id="pilot-runtime",
            kind=ArtifactKind.BASE_CONFIG,
            version="1.1",
            scope=ArtifactScope.STAGE,
            runtime_stage=stage,
            validations=validations,
            rollback_version="1.0",
            payload={"resource_budget": 0.78, "recovery_reserve": 0.2},
        ),
        ControlArtifact(
            artifact_id="shadow-policy",
            kind=ArtifactKind.POLICY,
            version="2.0",
            scope=ArtifactScope.BOUNDARY,
            runtime_stage=stage,
            boundary="shadow",
            validations=validations,
            evidence_ref="audit-shadow-policy",
            rollback_version="1.9",
            payload={"preview_gate": "strict", "drift_threshold": 0.05},
        ),
        ControlArtifact(
            artifact_id="rollout-policy",
            kind=ArtifactKind.POLICY,
            version="2.1",
            scope=ArtifactScope.BOUNDARY,
            runtime_stage=stage,
            boundary="rollout",
            validations=validations,
            evidence_ref="audit-rollout-policy",
            rollback_version="2.0",
            payload={"promotion_gate": "hold-until-shadow-green"},
        ),
    )


def run_integrated_smoke_build(
    *,
    profile: str = "pilot-runtime-dna",
    stage: RuntimeStage = RuntimeStage.PILOT,
    correlation_id: str = "integrated-smoke",
) -> IntegratedSmokeBuild:
    """Execute the canonical integrated smoke-build path across build foundations."""

    runtime_dna = runtime_dna_for_profile(profile, stage=stage)
    artifacts = _integrated_control_artifacts(stage)
    shadow_control_plane = load_control_plane(artifacts, runtime_stage=stage, boundary="shadow")
    rollout_control_plane = load_control_plane(artifacts, runtime_stage=stage, boundary="rollout")
    orchestration_state = core_state_for_runtime(
        runtime_dna,
        module="orchestration",
        status="integrated-smoke",
        budget=0.72,
        labels={"build": "130", "path": "integrated"},
    )
    shadow_command = command_message(
        name="validate-integrated-cutover",
        source_boundary="governance",
        target_boundary="shadow",
        correlation_id=correlation_id,
        payload={"wave": "integrated-smoke", "target_stage": stage.value},
    )
    shadow_preview = shadow_preview_for_command(
        orchestration_state,
        shadow_command,
        shadow_control_plane,
        invariants=("audit-before-cutover", "recovery-before-live"),
    )
    dry_run_evaluation = evaluate_dry_run(
        shadow_preview,
        observed_budget=0.7,
        drift_threshold=0.05,
        summary="Integrated smoke preview remained within accepted drift budget",
    )
    emitted_shadow_event = shadow_event(shadow_preview, dry_run_evaluation)
    rollout_state = core_state_for_runtime(
        runtime_dna,
        module="rollout",
        status="rollback-ready",
        budget=0.69,
        labels={"origin": "integrated-smoke"},
    )
    checkpoint = recovery_checkpoint_for_state(rollout_state, correlation_id=correlation_id)
    directive = rollback_directive_for_checkpoint(
        checkpoint,
        rollout_control_plane,
        reason="integrated smoke safeguard path",
    )
    outcome = recovery_outcome(
        directive,
        checkpoint,
        rollout_control_plane,
        replay_ready=dry_run_evaluation.replay_ready,
        audit_ref=f"audit-{correlation_id}",
        commitment_ref=f"commit-{correlation_id}",
    )
    reported_shadow_signal = telemetry_signal_from_event(emitted_shadow_event, status="reported")
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=stage,
        signals=(dry_run_evaluation.signal, reported_shadow_signal, outcome.signal),
        alerts=((dry_run_evaluation.alert,) if dry_run_evaluation.alert else ()),
        audit_entries=(
            audit_entry_for_message(shadow_command),
            *outcome.snapshot.audit_entries,
        ),
        active_controls=tuple(
            dict.fromkeys(
                [artifact.artifact_id for artifact in shadow_control_plane.applied_artifacts]
                + [artifact.artifact_id for artifact in rollout_control_plane.applied_artifacts]
            )
        ),
    )
    return IntegratedSmokeBuild(
        runtime_dna=runtime_dna,
        control_plane=shadow_control_plane,
        orchestration_state=orchestration_state,
        shadow_command=shadow_command,
        shadow_preview=shadow_preview,
        dry_run_evaluation=dry_run_evaluation,
        shadow_event=emitted_shadow_event,
        recovery_checkpoint=checkpoint,
        rollback_directive=directive,
        recovery_outcome=outcome,
        final_snapshot=final_snapshot,
    )
