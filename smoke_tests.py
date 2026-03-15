"""Leichte Smoke-Tests fuer zentrale KKI-Skripte."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from kki import (
    ActionName,
    ArtifactKind,
    ArtifactScope,
    AuthorizationIdentity,
    AuditTrailEntry,
    ClaimStatus,
    CorrelatedOperation,
    ControlArtifact,
    CoreState,
    DelegationGrant,
    DeliveryGuarantee,
    DeliveryMode,
    DispatchLane,
    DispatchTriageMode,
    EvidenceRecord,
    EventEnvelope,
    GateDecision,
    GateReadiness,
    GateState,
    GateOutcome,
    HandoffMode,
    IdentityKind,
    IntegratedSmokeBuild,
    LoadedControlPlane,
    MessageEnvelope,
    MessageKind,
    ModuleBoundaryName,
    OperationalPressure,
    OperatingMode,
    OrchestrationStatus,
    PersistenceRecord,
    PreviewMode,
    ShadowCoordination,
    ShadowCoordinationMode,
    ProtocolContext,
    RecoveryCheckpoint,
    RecoveryMode,
    RecoveryOutcome,
    RoleName,
    RolloutPhase,
    RolloutState,
    RollbackDirective,
    RuntimeStage,
    RuntimeThresholds,
    ShadowPreview,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    TransferEnvelope,
    TrustLevel,
    ValidationStep,
    WorkPriority,
    WorkStatus,
    authorize_action,
    authorize_artifact,
    advance_orchestration_state,
    advance_rollout_state,
    advance_work_unit,
    audit_entry_for_artifact,
    audit_entry_for_message,
    build_dispatch_plan,
    build_telemetry_snapshot,
    claim_for_work_unit,
    command_message,
    coordinate_shadow_work,
    correlate_operation,
    core_state_for_runtime,
    evaluate_dry_run,
    evaluate_gate,
    event_message,
    evidence_message,
    load_control_plane,
    module_boundaries,
    module_dependency_graph,
    orchestration_state_for_runtime,
    protocol_context,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
    rollout_state_for_shadow,
    run_integrated_smoke_build,
    runtime_dna_for_profile,
    runtime_dna_from_env,
    handoff_for_work_unit,
    operation_alerts,
    shadow_event,
    shadow_preview_for_command,
    shadow_snapshot,
    telemetry_alert,
    telemetry_signal_from_event,
    transfer_message,
    transfer_envelope_for_state,
    work_unit_for_state,
)

REPO_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


class SmokeTests(unittest.TestCase):
    def run_script(
        self,
        script_name: str,
        output_dir: Path,
        seed: int = 42,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "KKI_SEED": str(seed),
                "KKI_TEST_MODE": "1",
                "KKI_TEST_ROUNDS": "6",
                "KKI_TEST_INTERACTIONS": "8",
                "KKI_TEST_INVASION_ROUND": "3",
                "KKI_OUTPUT_DIR": str(output_dir),
                "MPLBACKEND": "Agg",
                "PYTHONUNBUFFERED": "1",
            }
        )
        if extra_env:
            env.update(extra_env)
        result = subprocess.run(
            [PYTHON, script_name],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        return result

    def assert_successful_run(self, result: subprocess.CompletedProcess[str]) -> None:
        if result.returncode != 0:
            self.fail(
                f"Skript schlug fehl ({result.returncode}).\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_runtime_dna_foundation_profile(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        exported = dna.to_dict()

        self.assertEqual(exported["identity"]["stage"], "shadow")
        self.assertIn("telemetry", exported["enabled_hooks"])
        self.assertIn("audit-before-cutover", exported["invariants"])
        self.assertGreater(exported["thresholds"]["resource_budget"], exported["thresholds"]["recovery_reserve"])

    def test_runtime_dna_env_overrides(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "KKI_RUNTIME_PROFILE": "pilot-runtime-dna",
                "KKI_RUNTIME_STAGE": "pilot",
                "KKI_RUNTIME_RESOURCE_BUDGET": "0.81",
                "KKI_RUNTIME_RECOVERY_RESERVE": "0.21",
                "KKI_RUNTIME_ENABLE_SHADOW": "false",
                "KKI_RUNTIME_OWNER": "copilot",
            },
            clear=False,
        ):
            dna = runtime_dna_from_env()

        self.assertEqual(dna.identity.profile, "pilot-runtime-dna")
        self.assertEqual(dna.identity.stage, RuntimeStage.PILOT)
        self.assertAlmostEqual(dna.thresholds.resource_budget, 0.81)
        self.assertAlmostEqual(dna.thresholds.recovery_reserve, 0.21)
        self.assertFalse(dna.hooks.shadow)
        self.assertEqual(dna.metadata["owner"], "copilot")

    def test_runtime_thresholds_reject_invalid_reserve(self) -> None:
        with self.assertRaises(ValueError):
            RuntimeThresholds(resource_budget=0.2, recovery_reserve=0.2)

    def test_kki_module_boundaries_are_importable(self) -> None:
        boundaries = module_boundaries()

        self.assertEqual(boundaries[0].name, ModuleBoundaryName.ORCHESTRATION)
        self.assertEqual(boundaries[-1].name, ModuleBoundaryName.GOVERNANCE)
        self.assertTrue(all(boundary.package.startswith("kki.") for boundary in boundaries))

    def test_kki_module_dependency_graph_is_stable(self) -> None:
        graph = module_dependency_graph()

        self.assertEqual(graph["orchestration"], ())
        self.assertEqual(graph["telemetry"], ("orchestration",))
        self.assertEqual(graph["shadow"], ("telemetry", "security"))
        self.assertEqual(graph["governance"], ("security", "rollout", "recovery"))

    def test_kki_core_state_snapshot_is_canonical(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(
            dna,
            module=ModuleBoundaryName.ORCHESTRATION,
            status="ready",
            budget=0.61,
            labels={"owner": "build-phase"},
        )

        self.assertIsInstance(state, CoreState)
        exported = state.to_dict()
        self.assertEqual(exported["module_boundary"], "orchestration")
        self.assertEqual(exported["runtime_stage"], "shadow")
        self.assertEqual(exported["labels"]["owner"], "build-phase")

    def test_kki_transfer_envelope_wraps_state(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="orchestration", status="promoting", budget=0.7)
        envelope = transfer_envelope_for_state(
            state,
            target_boundary="rollout",
            correlation_id="corr-123",
            causation_id="cause-1",
            sequence=2,
        )

        self.assertIsInstance(envelope, TransferEnvelope)
        exported = envelope.to_dict()
        self.assertEqual(exported["target_boundary"], "rollout")
        self.assertEqual(exported["payload_type"], "core-state")
        self.assertEqual(exported["payload"]["status"], "promoting")
        self.assertEqual(exported["sequence"], 2)

    def test_kki_persistence_record_rejects_invalid_retention(self) -> None:
        with self.assertRaises(ValueError):
            PersistenceRecord(
                record_type="snapshot",
                boundary=ModuleBoundaryName.RECOVERY,
                schema_version="1.0",
                retention_class="permanent",
                payload={"restart": True},
            )

    def test_kki_evidence_record_is_exportable(self) -> None:
        evidence = EvidenceRecord(
            evidence_type="approval",
            subject="cutover-gate",
            correlation_id="corr-9",
            audit_ref="audit-42",
            commitment_ref="commit-7",
            payload={"decision": "approved"},
        )

        exported = evidence.to_dict()
        self.assertEqual(exported["audit_ref"], "audit-42")
        self.assertEqual(exported["commitment_ref"], "commit-7")
        self.assertEqual(exported["payload"]["decision"], "approved")

    def test_kki_orchestration_state_tracks_health_markers(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-131",
            status=OrchestrationStatus.ACTIVE,
            budget_available=0.78,
            budget_reserved=0.22,
            pressure=OperationalPressure(0.44, 0.41, 0.28, 0.18),
            open_risks=("drift-watch",),
            labels={"wave": "131"},
        )

        exported = state.to_dict()
        self.assertEqual(exported["status"], "active")
        self.assertEqual(exported["health_status"], "healthy")
        self.assertIn("pressure:elevated", exported["health_markers"])
        self.assertEqual(exported["dispatch_budget"], 0.56)
        self.assertTrue(state.recovery_ready)

    def test_kki_orchestration_state_detects_blocked_recovery(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-131",
            status=OrchestrationStatus.DEGRADED,
            budget_available=0.72,
            budget_reserved=0.14,
            pressure=OperationalPressure(0.78, 0.72, 0.67, 0.58),
            gates=GateReadiness(recovery=GateState.BLOCKED, blockers=("reserve breach",)),
            open_risks=("drift", "queue-backlog", "operator-gate"),
        )

        self.assertFalse(state.recovery_ready)
        self.assertEqual(state.health_status(), "gated")
        self.assertIn("gates:blocked", state.health_markers())
        self.assertIn("risks-hot", state.health_markers())

    def test_kki_orchestration_state_validates_transitions(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        staged = orchestration_state_for_runtime(dna, mission_ref="mission-131")
        active = advance_orchestration_state(
            staged,
            status=OrchestrationStatus.ACTIVE,
            pressure=OperationalPressure(0.31, 0.22, 0.18, 0.12),
            labels={"handoff": "accepted"},
        )

        self.assertEqual(active.status, OrchestrationStatus.ACTIVE)
        self.assertEqual(active.labels["handoff"], "accepted")
        self.assertEqual(active.health_status(), "healthy")

        with self.assertRaises(ValueError):
            advance_orchestration_state(active, status=OrchestrationStatus.BOOTSTRAPPING)

    def test_kki_orchestration_state_exports_core_state(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-131",
            status=OrchestrationStatus.THROTTLED,
            budget_available=0.75,
            budget_reserved=0.19,
            pressure=OperationalPressure(0.64, 0.57, 0.33, 0.21),
        )
        core_state = state.to_core_state()
        exported = core_state.to_dict()

        self.assertEqual(exported["module_boundary"], "orchestration")
        self.assertEqual(exported["status"], "throttled")
        self.assertEqual(exported["labels"]["pressure_level"], "elevated")
        self.assertEqual(exported["labels"]["health_status"], "degraded")

    def test_kki_work_unit_is_built_from_orchestration_state(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-132",
            status=OrchestrationStatus.ACTIVE,
            budget_available=0.79,
            budget_reserved=0.21,
            pressure=OperationalPressure(0.54, 0.48, 0.29, 0.22),
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow preview dispatch",
            boundary="shadow",
            correlation_id="corr-wu",
            priority=WorkPriority.HIGH,
            required_capabilities=("preview", "drift-check"),
        )

        exported = work_unit.to_dict()
        self.assertEqual(exported["boundary"], "shadow")
        self.assertEqual(exported["priority"], "high")
        self.assertEqual(exported["status"], "planned")
        self.assertTrue(exported["ready_for_claim"])
        self.assertEqual(exported["labels"]["pressure_level"], "elevated")

    def test_kki_claim_uses_handoff_target_boundary(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(dna, mission_ref="mission-132")
        work_unit = work_unit_for_state(
            state,
            title="rollout evaluation",
            boundary="shadow",
            correlation_id="corr-claim",
        )
        handoff = handoff_for_work_unit(
            work_unit,
            target_boundary="rollout",
            reason="promotion review path",
            mode=HandoffMode.SHADOW,
            retry_budget=2,
        )
        transferred = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            handoff_ref=handoff.handoff_id,
            labels={"handoff_mode": handoff.mode.value},
        )
        claim = claim_for_work_unit(
            transferred,
            owner_ref="rollout-planner",
            boundary="rollout",
            handoff=handoff,
        )

        self.assertEqual(claim.status, ClaimStatus.ACTIVE)
        self.assertEqual(claim.boundary, ModuleBoundaryName.ROLLOUT)
        self.assertEqual(claim.handoff_ref, handoff.handoff_id)

    def test_kki_work_unit_transition_rejects_invalid_reset(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = orchestration_state_for_runtime(dna, mission_ref="mission-132")
        work_unit = work_unit_for_state(
            state,
            title="telemetry stitching",
            boundary="telemetry",
            correlation_id="corr-transition",
        )
        claimed = advance_work_unit(work_unit, status=WorkStatus.CLAIMED)
        active = advance_work_unit(claimed, status=WorkStatus.IN_PROGRESS, attempt=1)

        self.assertEqual(active.status, WorkStatus.IN_PROGRESS)
        self.assertEqual(active.attempt, 1)

        with self.assertRaises(ValueError):
            advance_work_unit(active, status=WorkStatus.PLANNED)

    def test_kki_handoff_contract_preserves_retry_metadata(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-132",
            status=OrchestrationStatus.THROTTLED,
            pressure=OperationalPressure(0.55, 0.62, 0.31, 0.47),
        )
        work_unit = work_unit_for_state(
            state,
            title="recovery staging",
            boundary="shadow",
            correlation_id="corr-handoff",
            priority=WorkPriority.CRITICAL,
            max_retries=3,
        )
        handoff = handoff_for_work_unit(
            work_unit,
            target_boundary="recovery",
            reason="critical drift escalation",
            mode=HandoffMode.RECOVERY,
            causation_id="shadow-drift",
        )

        exported = handoff.to_dict()
        self.assertEqual(exported["target_boundary"], "recovery")
        self.assertEqual(exported["retry_budget"], 3)
        self.assertEqual(exported["mode"], "recovery")
        self.assertEqual(exported["causation_id"], "shadow-drift")

    def test_kki_dispatch_plan_admits_high_priority_within_budget(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            status=OrchestrationStatus.ACTIVE,
            budget_available=0.8,
            budget_reserved=0.22,
            pressure=OperationalPressure(0.41, 0.58, 0.24, 0.19),
        )
        work_units = (
            work_unit_for_state(
                state,
                title="shadow verify",
                boundary="shadow",
                correlation_id="dispatch-1",
                priority=WorkPriority.HIGH,
                budget_share=0.18,
            ),
            work_unit_for_state(
                state,
                title="telemetry aggregate",
                boundary="telemetry",
                correlation_id="dispatch-2",
                priority=WorkPriority.NORMAL,
                budget_share=0.16,
            ),
            work_unit_for_state(
                state,
                title="recovery hold",
                boundary="recovery",
                correlation_id="dispatch-3",
                priority=WorkPriority.CRITICAL,
                budget_share=0.2,
            ),
        )

        plan = build_dispatch_plan(
            state,
            work_units,
            available_roles=(RoleName.EXECUTOR, RoleName.SUPERVISOR),
            max_parallel=2,
        )

        self.assertEqual(plan.triage_mode, DispatchTriageMode.BACKLOG)
        self.assertEqual(len(plan.admitted_unit_ids), 2)
        self.assertIn(work_units[2].unit_id, plan.admitted_unit_ids)
        self.assertLessEqual(plan.consumed_budget, plan.effective_budget)

    def test_kki_dispatch_plan_holds_work_when_dispatch_guarded(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
            pressure=OperationalPressure(0.52, 0.44, 0.2, 0.18),
        )
        normal_work = work_unit_for_state(
            state,
            title="normal rollout sync",
            boundary="rollout",
            correlation_id="dispatch-guarded",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )

        plan = build_dispatch_plan(state, (normal_work,))

        self.assertEqual(plan.assignments[0].lane, DispatchLane.HOLD)
        self.assertIn(normal_work.unit_id, plan.held_unit_ids)

    def test_kki_dispatch_plan_blocks_when_gate_blocked(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            gates=GateReadiness(dispatch=GateState.BLOCKED, blockers=("operator stop",)),
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow replay",
            boundary="shadow",
            correlation_id="dispatch-blocked",
            priority=WorkPriority.HIGH,
        )

        plan = build_dispatch_plan(state, (work_unit,))

        self.assertEqual(plan.assignments[0].lane, DispatchLane.BLOCK)
        self.assertEqual(plan.assignments[0].rationale, "dispatch gate is blocked")

    def test_kki_dispatch_plan_protects_reserve_gap(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = orchestration_state_for_runtime(
            dna,
            mission_ref="mission-133",
            status=OrchestrationStatus.DEGRADED,
            budget_available=0.76,
            budget_reserved=0.12,
            pressure=OperationalPressure(0.67, 0.48, 0.41, 0.54),
        )
        work_units = (
            work_unit_for_state(
                state,
                title="recovery checkpoint sync",
                boundary="recovery",
                correlation_id="dispatch-gap-1",
                priority=WorkPriority.CRITICAL,
                budget_share=0.22,
            ),
            work_unit_for_state(
                state,
                title="shadow backlog cleanup",
                boundary="shadow",
                correlation_id="dispatch-gap-2",
                priority=WorkPriority.NORMAL,
                budget_share=0.18,
                recovery_weight=0.18,
            ),
        )

        plan = build_dispatch_plan(state, work_units, max_parallel=2)

        self.assertEqual(plan.triage_mode, DispatchTriageMode.RECOVERY_PRIORITY)
        self.assertEqual(plan.assignments[0].lane, DispatchLane.ADMIT)
        self.assertEqual(plan.assignments[1].lane, DispatchLane.HOLD)
        self.assertLess(plan.effective_budget, plan.dispatch_budget)

    def test_kki_gate_decision_approves_admitted_rollout(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        state = orchestration_state_for_runtime(runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT), mission_ref="mission-134")
        work_unit = work_unit_for_state(
            state,
            title="rollout promotion",
            boundary="rollout",
            correlation_id="gate-rollout",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,), available_roles=(RoleName.EXECUTOR,))
        message = command_message(
            name="approve-promotion",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="gate-rollout",
            payload={"target": "pilot-wave"},
        )

        decision = evaluate_gate(
            identity,
            boundary="rollout",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            evidence_ref="audit-rollout-policy",
        )

        self.assertIsInstance(decision, GateDecision)
        self.assertEqual(decision.outcome, GateOutcome.GO)
        self.assertTrue(decision.evidence_required)

    def test_kki_gate_decision_holds_dispatch_hold_assignment(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-134",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow preview",
            boundary="shadow",
            correlation_id="gate-hold",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,))
        message = command_message(
            name="run-shadow-preview",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="gate-hold",
            payload={"preview": True},
        )

        decision = evaluate_gate(
            identity,
            boundary="shadow",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
        )

        self.assertEqual(decision.outcome, GateOutcome.HOLD)
        self.assertIn("dispatch planner requested hold", decision.reason)

    def test_kki_gate_decision_blocks_on_scope_denial(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW, boundary="recovery")
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        message = command_message(
            name="start-recovery",
            source_boundary="shadow",
            target_boundary="recovery",
            correlation_id="gate-block",
            payload={"rollback": True},
        )

        decision = evaluate_gate(
            identity,
            boundary="recovery",
            control_plane=control_plane,
            message=message,
            operating_mode=OperatingMode.RECOVERY,
            evidence_ref="audit-recovery",
        )

        self.assertEqual(decision.outcome, GateOutcome.BLOCK)
        self.assertIn("identity scope", decision.blockers[0])

    def test_kki_gate_decision_escalates_emergency_override(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        identity = AuthorizationIdentity(
            slug="supervisor-emergency",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.EMERGENCY,
            boundary_scope=("recovery", "security"),
        )
        message = command_message(
            name="emergency-recovery",
            source_boundary="governance",
            target_boundary="recovery",
            correlation_id="gate-escalate",
            payload={"override": "restart"},
        )

        decision = evaluate_gate(
            identity,
            boundary="recovery",
            control_plane=control_plane,
            message=message,
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override",
        )

        self.assertEqual(decision.outcome, GateOutcome.ESCALATE)
        self.assertTrue(decision.evidence_required)
        self.assertTrue(decision.escalation_required)

    def test_kki_correlate_operation_builds_snapshot(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-135",
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow correlate",
            boundary="shadow",
            correlation_id="corr-135",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,), available_roles=(RoleName.EXECUTOR,))
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        message = command_message(
            name="run-shadow-preview",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="corr-135",
            payload={"preview": True},
        )
        gate = evaluate_gate(
            identity,
            boundary="shadow",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
        )

        correlated = correlate_operation(
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            gate_decision=gate,
        )

        self.assertIsInstance(correlated, CorrelatedOperation)
        self.assertEqual(correlated.snapshot.highest_severity(), "info")
        self.assertEqual(len(correlated.signals), 3)
        self.assertIn("shadow-policy", correlated.snapshot.active_controls)

    def test_kki_operation_alerts_raise_for_blocked_gate(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW, boundary="recovery")
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow",),
        )
        message = command_message(
            name="start-recovery",
            source_boundary="shadow",
            target_boundary="recovery",
            correlation_id="corr-135-block",
            payload={"rollback": True},
        )
        gate = evaluate_gate(
            identity,
            boundary="recovery",
            control_plane=control_plane,
            message=message,
            operating_mode=OperatingMode.RECOVERY,
            evidence_ref="audit-recovery",
        )

        alerts = operation_alerts(message=message, gate_decision=gate)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].severity, "critical")

    def test_kki_correlate_operation_keeps_dispatch_audit(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-135",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="rollout hold",
            boundary="rollout",
            correlation_id="corr-135-hold",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,))
        message = command_message(
            name="approve-rollout",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-135-hold",
            payload={"target": "wave"},
        )

        correlated = correlate_operation(
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
        )

        entry_types = [entry.entry_type for entry in correlated.audit_entries]
        self.assertIn("dispatch-assignment", entry_types)
        self.assertEqual(correlated.alerts[0].severity, "warning")

    def test_kki_correlate_operation_gate_alerts_raise_snapshot_severity(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-135",
            status=OrchestrationStatus.THROTTLED,
            gates=GateReadiness(dispatch=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="rollout pending",
            boundary="rollout",
            correlation_id="corr-135-rollout",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        dispatch_plan = build_dispatch_plan(state, (work_unit,))
        identity = AuthorizationIdentity(
            slug="gatekeeper-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("rollout", "governance"),
        )
        message = command_message(
            name="approve-promotion",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-135-rollout",
            payload={"target": "pilot-wave"},
        )
        gate = evaluate_gate(
            identity,
            boundary="rollout",
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            evidence_ref="audit-rollout-policy",
        )

        correlated = correlate_operation(
            control_plane=control_plane,
            message=message,
            dispatch_assignment=dispatch_plan.assignments[0],
            gate_decision=gate,
        )

        self.assertEqual(gate.outcome, GateOutcome.HOLD)
        self.assertEqual(correlated.snapshot.highest_severity(), "warning")

    def test_kki_shadow_coordination_builds_release_ready_preview(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
        )
        work_unit = work_unit_for_state(
            state,
            title="shadow preview",
            boundary="rollout",
            correlation_id="corr-136-preview",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )

        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )

        self.assertIsInstance(coordination, ShadowCoordination)
        self.assertEqual(coordination.mode, ShadowCoordinationMode.PREVIEW)
        self.assertTrue(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "release-ready")
        self.assertEqual(coordination.correlation.snapshot.highest_severity(), "info")

    def test_kki_shadow_coordination_switches_to_parallel_mode(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="parallel validation",
            boundary="rollout",
            correlation_id="corr-136-parallel",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )

        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )

        self.assertEqual(coordination.mode, ShadowCoordinationMode.PARALLEL)
        self.assertFalse(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "parallel-required")

    def test_kki_shadow_coordination_clears_replay_for_handoff_work(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
        )
        work_unit = work_unit_for_state(
            state,
            title="replay validation",
            boundary="rollout",
            correlation_id="corr-136-replay",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-replay",
        )
        identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )

        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )

        self.assertEqual(coordination.mode, ShadowCoordinationMode.REPLAY)
        self.assertTrue(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "replay-cleared")
        self.assertEqual(coordination.preview.mode, PreviewMode.DRY_RUN)

    def test_kki_shadow_coordination_blocks_release_when_gate_denies(self) -> None:
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-136",
        )
        work_unit = work_unit_for_state(
            state,
            title="blocked shadow run",
            boundary="rollout",
            correlation_id="corr-136-blocked",
            priority=WorkPriority.HIGH,
            budget_share=0.14,
        )
        identity = AuthorizationIdentity(
            slug="observer-shadow",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("shadow",),
        )

        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=control_plane,
            identity=identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )

        self.assertFalse(coordination.release_ready)
        self.assertEqual(coordination.release_signal.status, "blocked")
        self.assertEqual(coordination.release_signal.severity, "critical")
        self.assertEqual(coordination.gate_decision.outcome, GateOutcome.BLOCK)

    def test_kki_rollout_state_promotes_release_ready_shadow(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
        )
        work_unit = work_unit_for_state(
            state,
            title="promote release",
            boundary="rollout",
            correlation_id="corr-137-promote",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
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
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )

        self.assertIsInstance(rollout_state, RolloutState)
        self.assertEqual(rollout_state.phase, RolloutPhase.PROMOTING)
        self.assertTrue(rollout_state.promotion_ready)
        self.assertEqual(rollout_state.promotion_signal.status, "promoting")
        self.assertEqual(rollout_state.to_core_state().module_boundary, ModuleBoundaryName.ROLLOUT)

    def test_kki_rollout_state_stages_parallel_shadow_release(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="parallel rollout staging",
            boundary="rollout",
            correlation_id="corr-137-stage",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
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
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )

        self.assertEqual(coordination.release_signal.status, "parallel-required")
        self.assertEqual(rollout_state.phase, RolloutPhase.STAGED)
        self.assertFalse(rollout_state.promotion_ready)

    def test_kki_rollout_state_moves_replay_release_into_canary(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
            ControlArtifact(
                artifact_id="rollout-policy",
                kind=ArtifactKind.POLICY,
                version="2.1",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="rollout",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-rollout-policy",
                payload={"promotion_gate": "hold-until-shadow-green"},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
        )
        work_unit = work_unit_for_state(
            state,
            title="replay release",
            boundary="rollout",
            correlation_id="corr-137-canary",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-rollout-replay",
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
        coordination = coordinate_shadow_work(
            state,
            replay_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=rollout_identity,
            evidence_ref="audit-rollout-policy",
        )
        active_state = advance_rollout_state(rollout_state, phase=RolloutPhase.ACTIVE)

        self.assertEqual(rollout_state.phase, RolloutPhase.CANARY)
        self.assertEqual(active_state.phase, RolloutPhase.ACTIVE)
        self.assertTrue(active_state.promotion_ready)

    def test_kki_rollout_state_marks_blocked_promotion_as_rollback_ready(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-policy",
                payload={"preview_gate": "strict", "drift_threshold": 0.05},
            ),
        )
        shadow_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-137",
        )
        work_unit = work_unit_for_state(
            state,
            title="blocked promotion",
            boundary="rollout",
            correlation_id="corr-137-blocked",
            priority=WorkPriority.HIGH,
            budget_share=0.15,
        )
        shadow_identity = AuthorizationIdentity(
            slug="executor-shadow",
            kind=IdentityKind.MODULE,
            role=RoleName.EXECUTOR,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("shadow", "rollout"),
        )
        denied_rollout_identity = AuthorizationIdentity(
            slug="observer-rollout",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("rollout",),
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=shadow_identity,
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.15,
        )

        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=denied_rollout_identity,
        )

        self.assertEqual(rollout_state.phase, RolloutPhase.ROLLBACK_READY)
        self.assertTrue(rollout_state.rollback_required)
        self.assertEqual(rollout_state.promotion_signal.severity, "critical")

    def test_kki_protocol_context_defaults_idempotency(self) -> None:
        context = protocol_context("corr-001", sequence=3)

        self.assertIsInstance(context, ProtocolContext)
        self.assertEqual(context.correlation_id, "corr-001")
        self.assertTrue(context.idempotency_key.startswith("msg-"))
        self.assertEqual(context.sequence, 3)

    def test_kki_command_message_is_acknowledged(self) -> None:
        message = command_message(
            name="approve-rollout",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-cmd",
            payload={"decision": "approve"},
        )

        self.assertIsInstance(message, MessageEnvelope)
        self.assertEqual(message.kind, MessageKind.COMMAND)
        self.assertEqual(message.delivery_mode, DeliveryMode.SYNC)
        self.assertEqual(message.delivery_guarantee, DeliveryGuarantee.ACKNOWLEDGED)

    def test_kki_event_message_is_replayable(self) -> None:
        event = event_message(
            name="shadow-drift-detected",
            event_class="shadow",
            severity="warning",
            source_boundary="shadow",
            target_boundary="telemetry",
            correlation_id="corr-evt",
            payload={"delta": 0.12},
        )

        self.assertIsInstance(event, EventEnvelope)
        self.assertEqual(event.message.kind, MessageKind.EVENT)
        self.assertEqual(event.message.delivery_mode, DeliveryMode.ASYNC)
        self.assertEqual(event.message.delivery_guarantee, DeliveryGuarantee.REPLAYABLE)
        self.assertTrue(event.replayable)

    def test_kki_transfer_message_wraps_transfer_envelope(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="handoff", budget=0.54)
        envelope = transfer_envelope_for_state(
            state,
            target_boundary="recovery",
            correlation_id="corr-transfer",
            sequence=4,
        )
        message = transfer_message(envelope, name="state-handoff")

        self.assertEqual(message.kind, MessageKind.TRANSFER)
        self.assertEqual(message.delivery_guarantee, DeliveryGuarantee.REPLAYABLE)
        self.assertEqual(message.context.sequence, 4)
        self.assertEqual(message.payload["payload"]["status"], "handoff")

    def test_kki_evidence_message_is_proof_bound(self) -> None:
        evidence = EvidenceRecord(
            evidence_type="recovery-approval",
            subject="restart-sequence",
            correlation_id="corr-proof",
            audit_ref="audit-proof",
            payload={"approved": True},
        )
        message = evidence_message(
            evidence,
            source_boundary="governance",
            target_boundary="telemetry",
        )

        self.assertEqual(message.kind, MessageKind.EVIDENCE)
        self.assertEqual(message.delivery_guarantee, DeliveryGuarantee.PROOF_BOUND)
        self.assertEqual(message.integrity_status, "attested")

    def test_kki_observer_identity_can_observe_events(self) -> None:
        identity = AuthorizationIdentity(
            slug="observer-1",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("telemetry",),
        )
        event = event_message(
            name="telemetry-pulse",
            event_class="telemetry",
            severity="info",
            source_boundary="telemetry",
            target_boundary="governance",
            correlation_id="corr-observe",
            payload={"heartbeat": True},
        )

        decision = authorize_action(
            identity,
            action=ActionName.OBSERVE,
            boundary="telemetry",
            message=event.message,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.permission_source, "role-policy")

    def test_kki_gatekeeper_quarantine_requires_evidence(self) -> None:
        identity = AuthorizationIdentity(
            slug="gatekeeper-1",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("security", "shadow", "rollout"),
        )

        denied = authorize_action(
            identity,
            action="quarantine",
            boundary="security",
        )
        allowed = authorize_action(
            identity,
            action="quarantine",
            boundary="security",
            evidence_ref="audit-quarantine-1",
        )

        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)
        self.assertTrue(allowed.requires_evidence)

    def test_kki_supervisor_override_requires_commitment(self) -> None:
        identity = AuthorizationIdentity(
            slug="supervisor-1",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.EMERGENCY,
            boundary_scope=("security", "governance", "recovery"),
        )

        denied = authorize_action(
            identity,
            action="override",
            boundary="governance",
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override-1",
        )
        allowed = authorize_action(
            identity,
            action="override",
            boundary="governance",
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override-1",
            commitment_ref="commit-override-1",
        )

        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)
        self.assertTrue(allowed.escalation_required)

    def test_kki_delegation_is_bounded_and_time_limited(self) -> None:
        identity = AuthorizationIdentity(
            slug="runtime-cell-1",
            kind=IdentityKind.RUNTIME,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.VERIFIED,
            boundary_scope=("orchestration",),
        )
        delegation = DelegationGrant(
            grantor_slug="operator-1",
            delegate_slug="runtime-cell-1",
            action=ActionName.EXECUTE,
            boundaries=("orchestration",),
            operating_modes=(OperatingMode.NORMAL,),
            message_kinds=(MessageKind.COMMAND,),
            expires_at="2099-01-01T00:00:00+00:00",
            justification="temporary rollout assist",
        )

        decision = authorize_action(
            identity,
            action="execute",
            boundary="orchestration",
            delegation=delegation,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.permission_source, "delegation")

    def test_kki_delegation_does_not_grant_critical_override(self) -> None:
        identity = AuthorizationIdentity(
            slug="operator-2",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.EMERGENCY,
            boundary_scope=("governance",),
        )
        delegation = DelegationGrant(
            grantor_slug="supervisor-2",
            delegate_slug="operator-2",
            action=ActionName.OVERRIDE,
            boundaries=("governance",),
            operating_modes=(OperatingMode.EMERGENCY,),
            message_kinds=(MessageKind.COMMAND,),
            expires_at="2099-01-01T00:00:00+00:00",
            justification="should remain disallowed",
        )

        decision = authorize_action(
            identity,
            action="override",
            boundary="governance",
            operating_mode=OperatingMode.EMERGENCY,
            evidence_ref="audit-override-2",
            commitment_ref="commit-override-2",
            delegation=delegation,
        )

        self.assertFalse(decision.allowed)

    def test_kki_control_plane_loads_scoped_artifacts(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="base-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.0",
                scope=ArtifactScope.GLOBAL,
                payload={"budget": 0.7, "telemetry": True},
            ),
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.1",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.76},
            ),
            ControlArtifact(
                artifact_id="security-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="security",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-policy-1",
                payload={"quarantine_mode": "strict"},
            ),
        )

        loaded = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="security")

        self.assertIsInstance(loaded, LoadedControlPlane)
        self.assertEqual(loaded.effective_payload["budget"], 0.76)
        self.assertEqual(loaded.effective_payload["quarantine_mode"], "strict")
        self.assertEqual(len(loaded.applied_artifacts), 3)

    def test_kki_policy_artifacts_require_evidence(self) -> None:
        with self.assertRaises(ValueError):
            ControlArtifact(
                artifact_id="security-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                boundary="security",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY),
                payload={"quarantine_mode": "strict"},
            )

    def test_kki_emergency_override_requires_rollback(self) -> None:
        with self.assertRaises(ValueError):
            ControlArtifact(
                artifact_id="emergency-stop",
                kind=ArtifactKind.EMERGENCY_OVERRIDE,
                version="3.0",
                scope=ArtifactScope.ROLE,
                runtime_stage=RuntimeStage.PRODUCTION,
                boundary="governance",
                role_scope="supervisor",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-stop-1",
                commitment_ref="commit-stop-1",
                payload={"stop_rollout": True},
            )

    def test_kki_policy_distribution_uses_gatekeeper_approval(self) -> None:
        identity = AuthorizationIdentity(
            slug="gatekeeper-2",
            kind=IdentityKind.OPERATOR,
            role=RoleName.GATEKEEPER,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("security",),
        )
        artifact = ControlArtifact(
            artifact_id="security-policy",
            kind=ArtifactKind.POLICY,
            version="2.1",
            scope=ArtifactScope.BOUNDARY,
            boundary="security",
            validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY),
            evidence_ref="audit-policy-2",
            payload={"quarantine_mode": "strict"},
        )

        decision = authorize_artifact(identity, artifact)

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.action, ActionName.APPROVE)

    def test_kki_loader_rejects_inconsistent_distribution_versions(self) -> None:
        artifacts = (
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.0",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.74},
            ),
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.1",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.76},
            ),
        )

        with self.assertRaises(ValueError):
            load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT)

    def test_kki_telemetry_signal_projects_event(self) -> None:
        event = event_message(
            name="policy-drift",
            event_class="telemetry",
            severity="warning",
            source_boundary="telemetry",
            target_boundary="governance",
            correlation_id="corr-telemetry",
            payload={"drift": 0.18},
        )

        signal = telemetry_signal_from_event(
            event,
            metrics={"drift_ratio": 0.18},
            labels={"dashboard": "ops"},
        )

        self.assertIsInstance(signal, TelemetrySignal)
        self.assertEqual(signal.boundary, ModuleBoundaryName.TELEMETRY)
        self.assertEqual(signal.metrics["drift_ratio"], 0.18)
        self.assertEqual(signal.labels["event_class"], "telemetry")

    def test_kki_telemetry_alert_tracks_thresholds(self) -> None:
        alert = telemetry_alert(
            alert_key="policy-drift-warning",
            boundary="security",
            severity="warning",
            summary="Policy drift exceeds warning budget",
            observed_value=0.18,
            threshold=0.1,
            correlation_id="corr-alert",
        )

        self.assertIsInstance(alert, TelemetryAlert)
        self.assertEqual(alert.status, "open")
        self.assertEqual(alert.boundary, ModuleBoundaryName.SECURITY)

    def test_kki_audit_entry_is_created_from_message(self) -> None:
        message = command_message(
            name="promote-artifact",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-audit-msg",
            payload={"artifact": "pilot-runtime"},
        )

        entry = audit_entry_for_message(message)

        self.assertIsInstance(entry, AuditTrailEntry)
        self.assertEqual(entry.subject, "promote-artifact")
        self.assertEqual(entry.payload["delivery_guarantee"], "acknowledged")

    def test_kki_audit_entry_is_created_from_artifact(self) -> None:
        artifact = ControlArtifact(
            artifact_id="security-policy",
            kind=ArtifactKind.POLICY,
            version="2.2",
            scope=ArtifactScope.BOUNDARY,
            boundary="security",
            validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY),
            evidence_ref="audit-policy-22",
            payload={"quarantine_mode": "strict"},
        )

        entry = audit_entry_for_artifact(artifact)

        self.assertEqual(entry.entry_type, "control-artifact")
        self.assertEqual(entry.payload["artifact_kind"], "policy")
        self.assertEqual(entry.evidence_ref, "audit-policy-22")

    def test_kki_telemetry_snapshot_aggregates_views(self) -> None:
        signal = TelemetrySignal(
            signal_name="policy-drift",
            boundary=ModuleBoundaryName.TELEMETRY,
            correlation_id="corr-snapshot",
            severity="warning",
            status="observed",
            metrics={"drift_ratio": 0.15},
        )
        alert = TelemetryAlert(
            alert_key="policy-drift-warning",
            boundary=ModuleBoundaryName.SECURITY,
            severity="warning",
            summary="Policy drift exceeds warning budget",
            observed_value=0.15,
            threshold=0.1,
            correlation_id="corr-snapshot",
        )
        snapshot = build_telemetry_snapshot(
            runtime_stage=RuntimeStage.PILOT,
            signals=(signal,),
            alerts=(alert,),
            active_controls=("pilot-runtime", "security-policy"),
        )

        self.assertIsInstance(snapshot, TelemetrySnapshot)
        self.assertEqual(snapshot.highest_severity(), "warning")
        self.assertEqual(snapshot.status_counts()["observed"], 1)
        self.assertIn("security-policy", snapshot.to_dict()["active_controls"])

    def test_kki_shadow_preview_tracks_controls_and_invariants(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="orchestration", status="ready", budget=0.72)
        control_plane = load_control_plane(
            (
                ControlArtifact(
                    artifact_id="pilot-runtime",
                    kind=ArtifactKind.BASE_CONFIG,
                    version="1.1",
                    scope=ArtifactScope.STAGE,
                    runtime_stage=RuntimeStage.PILOT,
                    validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                    payload={"budget": 0.76},
                ),
            ),
            runtime_stage=RuntimeStage.PILOT,
        )
        command = command_message(
            name="promote-shadow-build",
            source_boundary="governance",
            target_boundary="rollout",
            correlation_id="corr-shadow-1",
            payload={"wave": "pilot"},
        )

        preview = shadow_preview_for_command(
            state,
            command,
            control_plane,
            mode=PreviewMode.SHADOW,
            invariants=("no-live-cutover",),
        )

        self.assertIsInstance(preview, ShadowPreview)
        self.assertEqual(preview.control_versions, ("1.1",))
        self.assertIn("no-live-cutover", preview.invariants)

    def test_kki_dry_run_evaluation_emits_warning_on_drift(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="ready", budget=0.6)
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW)
        command = command_message(
            name="replay-state",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="corr-shadow-2",
            payload={"replay": True},
        )
        preview = shadow_preview_for_command(state, command, control_plane, mode=PreviewMode.DRY_RUN)

        evaluation = evaluate_dry_run(preview, observed_budget=0.78, drift_threshold=0.1)

        self.assertEqual(evaluation.status, "drift")
        self.assertFalse(evaluation.replay_ready)
        self.assertIsNotNone(evaluation.alert)

    def test_kki_shadow_snapshot_builds_drilldown_view(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="orchestration", status="ready", budget=0.7)
        artifacts = (
            ControlArtifact(
                artifact_id="pilot-runtime",
                kind=ArtifactKind.BASE_CONFIG,
                version="1.1",
                scope=ArtifactScope.STAGE,
                runtime_stage=RuntimeStage.PILOT,
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                payload={"budget": 0.76},
            ),
            ControlArtifact(
                artifact_id="shadow-policy",
                kind=ArtifactKind.POLICY,
                version="2.0",
                scope=ArtifactScope.BOUNDARY,
                runtime_stage=RuntimeStage.PILOT,
                boundary="shadow",
                validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                evidence_ref="audit-shadow-1",
                payload={"dry_run_mode": "strict"},
            ),
        )
        control_plane = load_control_plane(artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        command = command_message(
            name="validate-cutover",
            source_boundary="governance",
            target_boundary="shadow",
            correlation_id="corr-shadow-3",
            payload={"cutover": "candidate"},
        )
        preview = shadow_preview_for_command(state, command, control_plane)
        evaluation = evaluate_dry_run(preview, observed_budget=0.68, drift_threshold=0.05)

        snapshot = shadow_snapshot(preview, evaluation, control_plane)

        self.assertIsInstance(snapshot, TelemetrySnapshot)
        self.assertIn("shadow-policy", snapshot.to_dict()["active_controls"])
        self.assertGreaterEqual(len(snapshot.audit_entries), 2)

    def test_kki_shadow_event_emits_shadow_classification(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="preview", budget=0.64)
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW)
        command = command_message(
            name="preview-rollout",
            source_boundary="orchestration",
            target_boundary="shadow",
            correlation_id="corr-shadow-4",
            payload={"wave": "preview"},
        )
        preview = shadow_preview_for_command(state, command, control_plane)
        evaluation = evaluate_dry_run(preview, observed_budget=0.63, drift_threshold=0.05)

        event = shadow_event(preview, evaluation)

        self.assertIsInstance(event, EventEnvelope)
        self.assertEqual(event.event_class, "shadow")
        self.assertEqual(event.message.target_boundary, ModuleBoundaryName.TELEMETRY)

    def test_kki_recovery_checkpoint_captures_state_and_transfer(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="orchestration", status="degraded", budget=0.52)

        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-1")

        self.assertIsInstance(checkpoint, RecoveryCheckpoint)
        self.assertEqual(checkpoint.persistence_record.retention_class, "restart")
        self.assertEqual(checkpoint.transfer_envelope.target_boundary, ModuleBoundaryName.RECOVERY)

    def test_kki_rollback_directive_uses_control_plane_chain(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="rollout", status="rollback", budget=0.48)
        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-2")
        control_plane = load_control_plane(
            (
                ControlArtifact(
                    artifact_id="pilot-runtime",
                    kind=ArtifactKind.BASE_CONFIG,
                    version="1.1",
                    scope=ArtifactScope.STAGE,
                    runtime_stage=RuntimeStage.PILOT,
                    validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                    rollback_version="1.0",
                    payload={"budget": 0.76},
                ),
            ),
            runtime_stage=RuntimeStage.PILOT,
        )

        directive = rollback_directive_for_checkpoint(checkpoint, control_plane, reason="shadow drift")

        self.assertIsInstance(directive, RollbackDirective)
        self.assertEqual(directive.mode, RecoveryMode.ROLLBACK)
        self.assertEqual(directive.rollback_chain, ("pilot-runtime:1.0",))

    def test_kki_rollback_directive_falls_back_without_versions(self) -> None:
        dna = runtime_dna_for_profile("balanced-runtime-dna", stage=RuntimeStage.SHADOW)
        state = core_state_for_runtime(dna, module="shadow", status="blocked", budget=0.44)
        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-3")
        control_plane = load_control_plane((), runtime_stage=RuntimeStage.SHADOW)

        directive = rollback_directive_for_checkpoint(
            checkpoint,
            control_plane,
            reason="missing preview guarantees",
            mode=RecoveryMode.RESTART,
        )

        self.assertEqual(directive.rollback_chain, ("state-only-recovery",))
        self.assertEqual(directive.mode, RecoveryMode.RESTART)

    def test_kki_recovery_outcome_binds_evidence_and_snapshot(self) -> None:
        dna = runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT)
        state = core_state_for_runtime(dna, module="rollout", status="rollback", budget=0.46)
        checkpoint = recovery_checkpoint_for_state(state, correlation_id="corr-recovery-4")
        control_plane = load_control_plane(
            (
                ControlArtifact(
                    artifact_id="rollout-policy",
                    kind=ArtifactKind.POLICY,
                    version="2.0",
                    scope=ArtifactScope.BOUNDARY,
                    runtime_stage=RuntimeStage.PILOT,
                    boundary="rollout",
                    validations=(ValidationStep.STATIC, ValidationStep.CONSISTENCY, ValidationStep.SHADOW),
                    evidence_ref="audit-rollout-2",
                    rollback_version="1.9",
                    payload={"cutover_gate": "hold"},
                ),
            ),
            runtime_stage=RuntimeStage.PILOT,
            boundary="rollout",
        )
        directive = rollback_directive_for_checkpoint(checkpoint, control_plane, reason="pilot drift")

        outcome = recovery_outcome(
            directive,
            checkpoint,
            control_plane,
            replay_ready=True,
            audit_ref="audit-recovery-4",
            commitment_ref="commit-recovery-4",
        )

        self.assertIsInstance(outcome, RecoveryOutcome)
        self.assertEqual(outcome.status, "reentry-ready")
        self.assertEqual(outcome.evidence.commitment_ref, "commit-recovery-4")
        self.assertIn("rollout-policy", outcome.snapshot.to_dict()["active_controls"])

    def test_kki_integrated_smoke_build_runs_end_to_end(self) -> None:
        smoke = run_integrated_smoke_build(correlation_id="corr-integrated-1")

        self.assertIsInstance(smoke, IntegratedSmokeBuild)
        self.assertTrue(smoke.success)
        self.assertEqual(smoke.shadow_event.event_class, "shadow")
        self.assertEqual(smoke.recovery_outcome.status, "reentry-ready")

    def test_kki_integrated_smoke_build_keeps_controls_and_audit_visible(self) -> None:
        smoke = run_integrated_smoke_build(correlation_id="corr-integrated-2")
        exported = smoke.to_dict()

        self.assertIn("shadow-policy", exported["final_snapshot"]["active_controls"])
        self.assertIn("rollout-policy", exported["final_snapshot"]["active_controls"])
        self.assertGreaterEqual(len(exported["final_snapshot"]["audit_entries"]), 3)
        self.assertEqual(exported["final_snapshot"]["highest_severity"], "info")

    def test_kooperation_test_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            first_result = self.run_script("kooperation_test.py", output_dir, seed=123)
            second_result = self.run_script("kooperation_test.py", output_dir, seed=123)

        self.assert_successful_run(first_result)
        self.assert_successful_run(second_result)
        self.assertEqual(first_result.stdout, second_result.stdout)
        self.assertIn("Seed: 123 (KKI_SEED)", first_result.stdout)

    def test_kooperation_visual_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("kooperation_visual.py", output_dir, seed=99)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_kooperation_graph.png").exists())
            self.assertIn("Graph gespeichert:", result.stdout)

    def test_schwarm_simulation_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("schwarm_simulation.py", output_dir, seed=7)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_schwarm_simulation.png").exists())
            self.assertIn("ERGEBNISSE", result.stdout)

    def test_commitment_protokoll_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("commitment_protokoll.py", output_dir, seed=11)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_commitment_protokoll.png").exists())
            self.assertIn("COMMITMENT-PROTOKOLL", result.stdout)

    def test_schwarm_polarisierung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("schwarm_polarisierung.py", output_dir, seed=17)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_polarisierung.png").exists())
            self.assertIn("Polarisierungs-Index", result.stdout)

    def test_schwarm_polarisierung_adaptiv_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_polarisierung.py",
                output_dir,
                seed=19,
                extra_env={
                    "KKI_REWIRING_ENABLED": "true",
                    "KKI_REWIRE_REP_THRESHOLD": "0.30",
                    "KKI_REWIRE_PROXIMITY_WEIGHT": "0.35",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_polarisierung.png").exists())
            self.assertIn("Adaptives Rewiring: aktiv", result.stdout)

    def test_schwarm_parameterstudie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script("schwarm_parameterstudie.py", output_dir, seed=23)
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_netzwerk_parameterstudie.png").exists())
            self.assertIn("Beste Konfiguration", result.stdout)

    def test_schwarm_adaptive_netzwerke_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_adaptive_netzwerke.py",
                output_dir,
                seed=29,
                extra_env={"KKI_ADAPTIVE_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_adaptive_netzwerke.png").exists())
            self.assertIn("Beste adaptive Konfiguration", result.stdout)

    def test_schwarm_invasive_netzwerke_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_invasive_netzwerke.py",
                output_dir,
                seed=31,
                extra_env={"KKI_INVASION_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_invasive_netzwerke.png").exists())
            self.assertIn("Beste adaptive Abwehr", result.stdout)

    def test_schwarm_commitment_resilienz_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_commitment_resilienz.py",
                output_dir,
                seed=37,
                extra_env={"KKI_COMMITMENT_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_commitment_resilienz.png").exists())
            self.assertIn("Beste adaptive Commitment-Abwehr", result.stdout)

    def test_schwarm_vertrauens_benchmark_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_vertrauens_benchmark.py",
                output_dir,
                seed=41,
                extra_env={"KKI_BENCHMARK_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_vertrauens_benchmark.png").exists())
            self.assertIn("Beste Vertrauensstrategie", result.stdout)

    def test_schwarm_grossstudie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_grossstudie.py",
                output_dir,
                seed=43,
                extra_env={"KKI_MEGASTUDY_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_grossstudie.png").exists())
            self.assertIn("Staerkster adaptiver Vorteil", result.stdout)

    def test_schwarm_anti_polarisierung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_anti_polarisierung.py",
                output_dir,
                seed=47,
                extra_env={"KKI_ANTI_POL_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_anti_polarisierung.png").exists())
            self.assertIn("Beste Anti-Polarisierungsstrategie", result.stdout)

    def test_schwarm_gekoppelte_abwehr_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gekoppelte_abwehr.py",
                output_dir,
                seed=53,
                extra_env={"KKI_COUPLED_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gekoppelte_abwehr.png").exists())
            self.assertIn("Beste gekoppelte Abwehrarchitektur", result.stdout)

    def test_schwarm_rollenspezialisierung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenspezialisierung.py",
                output_dir,
                seed=59,
                extra_env={"KKI_ROLLENSPEZ_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenspezialisierung.png").exists())
            self.assertIn("Bestes Rollenprofil", result.stdout)

    def test_schwarm_rollenlernen_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenlernen.py",
                output_dir,
                seed=61,
                extra_env={"KKI_ROLLENLERNEN_REPETITIONS": "1"},
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenlernen.png").exists())
            self.assertIn("Bestes Lernprofil", result.stdout)

    def test_schwarm_rollenwechsel_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenwechsel.py",
                output_dir,
                seed=67,
                extra_env={
                    "KKI_ROLLENWECHSEL_REPETITIONS": "1",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenwechsel.png").exists())
            self.assertIn("Bestes Rollenwechselprofil", result.stdout)

    def test_schwarm_missionsziele_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_missionsziele.py",
                output_dir,
                seed=71,
                extra_env={
                    "KKI_MISSION_REPETITIONS": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_missionsziele.png").exists())
            self.assertIn("Beste Missionsarchitektur", result.stdout)

    def test_schwarm_missionskonflikte_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_missionskonflikte.py",
                output_dir,
                seed=73,
                extra_env={
                    "KKI_MISSION_ARBITRATION_REPETITIONS": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_missionskonflikte.png").exists())
            self.assertIn("Beste Konflikt-Architektur", result.stdout)

    def test_schwarm_arbeitsketten_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_arbeitsketten.py",
                output_dir,
                seed=79,
                extra_env={
                    "KKI_WORKFLOW_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_arbeitsketten.png").exists())
            self.assertIn("Beste Workflow-Architektur", result.stdout)

    def test_schwarm_arbeitszellen_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_arbeitszellen.py",
                output_dir,
                seed=83,
                extra_env={
                    "KKI_WORKFLOW_CELL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_arbeitszellen.png").exists())
            self.assertIn("Beste Zellarchitektur", result.stdout)

    def test_schwarm_arbeitszellen_parallel_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_arbeitszellen_parallel.py",
                output_dir,
                seed=89,
                extra_env={
                    "KKI_PARALLEL_CELLS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_arbeitszellen_parallel.png").exists())
            self.assertIn("Beste Ressourcenarchitektur", result.stdout)

    def test_schwarm_faehigkeitscluster_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_faehigkeitscluster.py",
                output_dir,
                seed=97,
                extra_env={
                    "KKI_CAPABILITY_CLUSTER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_faehigkeitscluster.png").exists())
            self.assertIn("Beste Clusterarchitektur", result.stdout)

    def test_schwarm_engpassmanagement_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_engpassmanagement.py",
                output_dir,
                seed=101,
                extra_env={
                    "KKI_BOTTLENECK_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_engpassmanagement.png").exists())
            self.assertIn("Bestes Engpassprofil", result.stdout)

    def test_schwarm_meta_koordination_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_meta_koordination.py",
                output_dir,
                seed=103,
                extra_env={
                    "KKI_META_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_meta_koordination.png").exists())
            self.assertIn("Beste Meta-Architektur", result.stdout)





    def test_schwarm_integrationsstudie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_integrationsstudie.py",
                output_dir,
                seed=131,
                extra_env={
                    "KKI_INTEGRATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_integrationsstudie.png").exists())
            self.assertIn("Beste Gesamtarchitektur", result.stdout)

    def test_schwarm_wiederanlauf_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_wiederanlauf.py",
                output_dir,
                seed=127,
                extra_env={
                    "KKI_RESTART_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_wiederanlauf.png").exists())
            self.assertIn("Beste Wiederanlauf-Architektur", result.stdout)

    def test_schwarm_fehlerisolation_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_fehlerisolation.py",
                output_dir,
                seed=113,
                extra_env={
                    "KKI_ISOLATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_fehlerisolation.png").exists())
            self.assertIn("Beste Isolationsarchitektur", result.stdout)

    def test_schwarm_spezialfaehigkeiten_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_spezialfaehigkeiten.py",
                output_dir,
                seed=109,
                extra_env={
                    "KKI_SKILL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_spezialfaehigkeiten.png").exists())
            self.assertIn("Beste Lernarchitektur", result.stdout)

    def test_schwarm_manipulationsresistenz_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_manipulationsresistenz.py",
                output_dir,
                seed=107,
                extra_env={
                    "KKI_MANIPULATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_manipulationsresistenz.png").exists())
            self.assertIn("Beste Abwehrarchitektur", result.stdout)

    def test_schwarm_interaktionsmodelle_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_interaktionsmodelle.py",
                output_dir,
                seed=139,
                extra_env={
                    "KKI_INTERACTION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_interaktionsmodelle.png").exists())
            self.assertIn("Bestes Interaktionsmodell", result.stdout)

    def test_schwarm_modellwechsel_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_modellwechsel.py",
                output_dir,
                seed=149,
                extra_env={
                    "KKI_MODEL_SWITCH_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_modellwechsel.png").exists())
            self.assertIn("Bestes Modellwechselprofil", result.stdout)

    def test_schwarm_beziehungsgedaechtnis_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_beziehungsgedaechtnis.py",
                output_dir,
                seed=151,
                extra_env={
                    "KKI_RELATIONSHIP_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_beziehungsgedaechtnis.png").exists())
            self.assertIn("Bestes Beziehungsgedaechtnisprofil", result.stdout)

    def test_schwarm_gruppenbildung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenbildung.py",
                output_dir,
                seed=157,
                extra_env={
                    "KKI_GROUP_FORMATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenbildung.png").exists())
            self.assertIn("Beste Gruppenarchitektur", result.stdout)

    def test_schwarm_gruppenidentitaet_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenidentitaet.py",
                output_dir,
                seed=163,
                extra_env={
                    "KKI_GROUP_IDENTITY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenidentitaet.png").exists())
            self.assertIn("Beste Identitaetsarchitektur", result.stdout)

    def test_schwarm_gruppentalente_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppentalente.py",
                output_dir,
                seed=167,
                extra_env={
                    "KKI_GROUP_TALENT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppentalente.png").exists())
            self.assertIn("Bestes Gruppentalentprofil", result.stdout)

    def test_schwarm_gruppenhandoff_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenhandoff.py",
                output_dir,
                seed=173,
                extra_env={
                    "KKI_GROUP_HANDOFF_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenhandoff.png").exists())
            self.assertIn("Bestes Gruppenhandoff-Profil", result.stdout)

    def test_schwarm_faehigkeitsarbitration_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_faehigkeitsarbitration.py",
                output_dir,
                seed=179,
                extra_env={
                    "KKI_CAPABILITY_ARBITRATION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_faehigkeitsarbitration.png").exists())
            self.assertIn("Beste Faehigkeitsarbitration", result.stdout)

    def test_schwarm_gruppenrobustheit_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenrobustheit.py",
                output_dir,
                seed=181,
                extra_env={
                    "KKI_GROUP_ROBUSTNESS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenrobustheit.png").exists())
            self.assertIn("Beste Gruppenrobustheit", result.stdout)

    def test_schwarm_vorbauphase_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_vorbauphase.py",
                output_dir,
                seed=191,
                extra_env={
                    "KKI_PREBUILD_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_vorbauphase.png").exists())
            self.assertIn("Beste Vor-Bauphasen-Architektur", result.stdout)

    def test_schwarm_dna_schema_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_dna_schema.py",
                output_dir,
                seed=193,
                extra_env={
                    "KKI_DNA_SCHEMA_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_dna_schema.png").exists())
            self.assertIn("Beste DNA-Schema-Architektur", result.stdout)

    def test_schwarm_overlay_module_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_overlay_module.py",
                output_dir,
                seed=197,
                extra_env={
                    "KKI_OVERLAY_MODULE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_overlay_module.png").exists())
            self.assertIn("Bestes Overlay-Modulprofil", result.stdout)

    def test_schwarm_gruppenbootstrap_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_gruppenbootstrap.py",
                output_dir,
                seed=199,
                extra_env={
                    "KKI_GROUP_BOOTSTRAP_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_gruppenbootstrap.png").exists())
            self.assertIn("Bestes Bootstrap-Profil", result.stdout)

    def test_schwarm_protokollstack_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_protokollstack.py",
                output_dir,
                seed=211,
                extra_env={
                    "KKI_PROTOCOL_STACK_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_protokollstack.png").exists())
            self.assertIn("Bester Protokollstack", result.stdout)

    def test_schwarm_handoff_vertraege_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_handoff_vertraege.py",
                output_dir,
                seed=223,
                extra_env={
                    "KKI_HANDOFF_CONTRACT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_handoff_vertraege.png").exists())
            self.assertIn("Bester Handoff-Vertrag", result.stdout)

    def test_schwarm_governance_layer_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_governance_layer.py",
                output_dir,
                seed=227,
                extra_env={
                    "KKI_GOVERNANCE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_governance_layer.png").exists())
            self.assertIn("Bester Governance-Layer", result.stdout)

    def test_schwarm_werkzeugbindung_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_werkzeugbindung.py",
                output_dir,
                seed=229,
                extra_env={
                    "KKI_TOOL_BINDING_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_werkzeugbindung.png").exists())
            self.assertIn("Beste Werkzeugbindung", result.stdout)

    def test_schwarm_laufzeitsupervision_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_laufzeitsupervision.py",
                output_dir,
                seed=233,
                extra_env={
                    "KKI_RUNTIME_SUPERVISION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_laufzeitsupervision.png").exists())
            self.assertIn("Beste Laufzeitsupervision", result.stdout)

    def test_schwarm_bauphasen_stresstest_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_stresstest.py",
                output_dir,
                seed=239,
                extra_env={
                    "KKI_BUILD_STRESS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_stresstest.png").exists())
            self.assertIn("Bester Bauphasen-Stack", result.stdout)

    def test_schwarm_bauphasen_blueprint_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_blueprint.py",
                output_dir,
                seed=241,
                extra_env={
                    "KKI_BLUEPRINT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_blueprint.png").exists())
            self.assertIn("Bester Bauphasen-Blueprint", result.stdout)

    def test_schwarm_runtime_dna_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_runtime_dna.py",
                output_dir,
                seed=251,
                extra_env={
                    "KKI_RUNTIME_DNA_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_runtime_dna.png").exists())
            self.assertIn("Beste Runtime-DNA", result.stdout)

    def test_schwarm_rollenassembler_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollenassembler.py",
                output_dir,
                seed=257,
                extra_env={
                    "KKI_ROLE_ASSEMBLER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollenassembler.png").exists())
            self.assertIn("Bester Rollen-Assembler", result.stdout)

    def test_schwarm_werkzeugrouting_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_werkzeugrouting.py",
                output_dir,
                seed=263,
                extra_env={
                    "KKI_TOOL_ROUTING_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_werkzeugrouting.png").exists())
            self.assertIn("Bester Capability-Broker", result.stdout)

    def test_schwarm_wissensspeicher_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_wissensspeicher.py",
                output_dir,
                seed=269,
                extra_env={
                    "KKI_MEMORY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_wissensspeicher.png").exists())
            self.assertIn("Bester Wissensspeicher", result.stdout)

    def test_schwarm_freigabe_workflow_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_freigabe_workflow.py",
                output_dir,
                seed=271,
                extra_env={
                    "KKI_APPROVAL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_freigabe_workflow.png").exists())
            self.assertIn("Bester Freigabe-Workflow", result.stdout)

    def test_schwarm_supervisor_eingriffe_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_supervisor_eingriffe.py",
                output_dir,
                seed=277,
                extra_env={
                    "KKI_SUPERVISOR_ACTION_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_supervisor_eingriffe.png").exists())
            self.assertIn("Bester Supervisor-Eingriff", result.stdout)

    def test_schwarm_resilienzbudget_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_resilienzbudget.py",
                output_dir,
                seed=281,
                extra_env={
                    "KKI_RESILIENCE_BUDGET_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_resilienzbudget.png").exists())
            self.assertIn("Bestes Resilienzbudget", result.stdout)

    def test_schwarm_sandbox_zellen_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_sandbox_zellen.py",
                output_dir,
                seed=307,
                extra_env={
                    "KKI_SANDBOX_CELL_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_sandbox_zellen.png").exists())
            self.assertIn("Beste Sandbox-Zellstruktur", result.stdout)

    def test_schwarm_missions_dry_run_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_missions_dry_run.py",
                output_dir,
                seed=331,
                extra_env={
                    "KKI_MISSION_DRY_RUN_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_missions_dry_run.png").exists())
            self.assertIn("Bester Missions-Dry-Run", result.stdout)

    def test_schwarm_bauphasen_pilot_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_pilot.py",
                output_dir,
                seed=359,
                extra_env={
                    "KKI_PILOT_ARCH_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_pilot.png").exists())
            self.assertIn("Beste Bauphasen-Pilotarchitektur", result.stdout)

    def test_schwarm_instanziierungspipeline_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_instanziierungspipeline.py",
                output_dir,
                seed=383,
                extra_env={
                    "KKI_INSTANTIATION_PIPELINE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_instanziierungspipeline.png").exists())
            self.assertIn("Beste Instanziierungs-Pipeline", result.stdout)

    def test_schwarm_wissensbus_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_wissensbus.py",
                output_dir,
                seed=401,
                extra_env={
                    "KKI_KNOWLEDGE_BUS_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_wissensbus.png").exists())
            self.assertIn("Bester Wissensbus", result.stdout)

    def test_schwarm_werkzeugadapter_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_werkzeugadapter.py",
                output_dir,
                seed=419,
                extra_env={
                    "KKI_TOOL_ADAPTER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_werkzeugadapter.png").exists())
            self.assertIn("Bester Werkzeug-Adapter", result.stdout)

    def test_schwarm_rollout_protokolle_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_rollout_protokolle.py",
                output_dir,
                seed=433,
                extra_env={
                    "KKI_ROLLOUT_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_rollout_protokolle.png").exists())
            self.assertIn("Bestes Rollout-Protokoll", result.stdout)

    def test_schwarm_zustandstransfer_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_zustandstransfer.py",
                output_dir,
                seed=449,
                extra_env={
                    "KKI_STATE_TRANSFER_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_zustandstransfer.png").exists())
            self.assertIn("Bester Zustandstransfer", result.stdout)

    def test_schwarm_ressourcen_orchestrator_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_ressourcen_orchestrator.py",
                output_dir,
                seed=461,
                extra_env={
                    "KKI_RESOURCE_ORCHESTRATOR_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_ressourcen_orchestrator.png").exists())
            self.assertIn("Bester Ressourcen-Orchestrator", result.stdout)

    def test_schwarm_audit_telemetrie_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_audit_telemetrie.py",
                output_dir,
                seed=467,
                extra_env={
                    "KKI_AUDIT_TELEMETRY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_audit_telemetrie.png").exists())
            self.assertIn("Beste Audit-Telemetrie", result.stdout)

    def test_schwarm_sicherheits_policies_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_sicherheits_policies.py",
                output_dir,
                seed=479,
                extra_env={
                    "KKI_SECURITY_POLICY_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_sicherheits_policies.png").exists())
            self.assertIn("Beste Sicherheitskette", result.stdout)

    def test_schwarm_schattenbetrieb_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_schattenbetrieb.py",
                output_dir,
                seed=491,
                extra_env={
                    "KKI_SHADOW_MODE_REPETITIONS": "1",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_schattenbetrieb.png").exists())
            self.assertIn("Bester Schattenbetrieb", result.stdout)

    def test_schwarm_bauphasen_rollout_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kki-smoke-") as tmpdir:
            output_dir = Path(tmpdir)
            result = self.run_script(
                "schwarm_bauphasen_rollout.py",
                output_dir,
                seed=503,
                extra_env={
                    "KKI_BUILD_ROLLOUT_FAST": "1",
                    "KKI_BUILD_ROLLOUT_REPETITIONS": "1",
                    "KKI_BUILD_ROLLOUT_AGENT_COUNT": "12",
                    "KKI_WORKFLOW_STAGE_MIN_TENURE": "1",
                    "KKI_MISSION_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_INTERVAL": "2",
                    "KKI_ROLE_SWITCH_MIN_TENURE": "2",
                    "KKI_INJECTION_ATTACK_ROUND": "3",
                    "KKI_FAILURE_ROUND": "4",
                },
            )
            self.assert_successful_run(result)
            self.assertTrue((output_dir / "kki_bauphasen_rollout.png").exists())
            self.assertIn("Bester Bauphasen-Rollout", result.stdout)


if __name__ == "__main__":
    unittest.main()
