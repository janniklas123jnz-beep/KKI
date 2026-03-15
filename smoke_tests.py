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
    BenchmarkCase,
    BenchmarkHarness,
    BenchmarkReleaseMode,
    CapacityLane,
    CapacityPlanEntry,
    CapacityPlanner,
    CapacityWindow,
    ChangeWindow,
    ChangeWindowEntry,
    ChangeWindowStatus,
    ClaimStatus,
    ContinuousReadinessCycle,
    ContinuousReadinessIteration,
    ContinuousReadinessStatus,
    ConvergenceProjection,
    ConvergenceSimulator,
    ConvergenceStatus,
    CorrelatedOperation,
    CockpitEntry,
    CockpitStatus,
    ControlArtifact,
    CoreState,
    DelegationGrant,
    DeliveryGuarantee,
    DeliveryMode,
    DriftMonitor,
    DriftObservation,
    DriftSeverity,
    DispatchLane,
    DispatchTriageMode,
    EscalationDirective,
    EscalationPath,
    EscalationPlan,
    EscalationRoute,
    EscalationRoutePath,
    EscalationRouter,
    EvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceLedgerSource,
    EvidenceRecord,
    EventEnvelope,
    GateDecision,
    GateReadiness,
    GateState,
    GateOutcome,
    Guardrail,
    GuardrailDomain,
    GuardrailPolicyMode,
    GuardrailPortfolio,
    GovernanceAgenda,
    GovernanceAgendaItem,
    GovernanceAgendaStatus,
    HandoffMode,
    HumanDecision,
    HumanLoopGovernance,
    IdentityKind,
    ImprovementExecutionMode,
    ImprovementOrchestrator,
    ImprovementPriority,
    ImprovementWave,
    IncidentCause,
    IncidentReport,
    IncidentSeverity,
    IntegratedOperationsRun,
    IntegratedSmokeBuild,
    LearningPatternType,
    LearningRecord,
    LearningRegister,
    LoadedControlPlane,
    MissionPolicy,
    MissionProfile,
    MissionScenario,
    MessageEnvelope,
    MessageKind,
    ModuleBoundaryName,
    OperationalPressure,
    OperationsRunLedger,
    OperationsCockpit,
    OperationsWave,
    OperatingMode,
    OperationsIncident,
    OrchestrationStatus,
    PortfolioAction,
    PortfolioOptimizer,
    PortfolioPriority,
    PortfolioRecommendation,
    PolicyTuneAction,
    PolicyTuneEntry,
    PolicyTuner,
    PersistenceRecord,
    PreviewMode,
    ShadowCoordination,
    ShadowCoordinationMode,
    ProtocolContext,
    ReadinessCadence,
    ReadinessCadenceEntry,
    ReadinessCadenceStatus,
    ReadinessCadenceTrigger,
    ReadinessCadenceWindow,
    RecoveryCheckpoint,
    RecoveryDrill,
    RecoveryDrillStatus,
    RecoveryDrillSuite,
    ReadinessFinding,
    ReadinessFindingSeverity,
    ReadinessReview,
    RemediationCampaign,
    RemediationCampaignStage,
    RemediationCampaignStageType,
    RemediationCampaignStatus,
    RecoveryDisposition,
    RecoveryMode,
    RecoveryOrchestration,
    RecoveryOutcome,
    ReleaseCampaign,
    ReleaseCampaignStage,
    ReleaseCampaignStageType,
    ReleaseCampaignStatus,
    ReviewActionItem,
    ReviewActionPlan,
    ReviewActionPriority,
    ReviewActionType,
    RiskImpact,
    RiskLikelihood,
    RiskMitigationStatus,
    RiskRecord,
    RiskRegister,
    ReplayMode,
    RoleName,
    RolloutPhase,
    RolloutState,
    RollbackDirective,
    RunLedgerEntry,
    RuntimeScorecard,
    RuntimeScorecardEntry,
    RuntimeStage,
    RuntimeThresholds,
    ScenarioReplayItem,
    ScenarioReplayResult,
    ScenarioReplaySuite,
    ShadowPreview,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    TransferEnvelope,
    TrustLevel,
    ValidationStep,
    WaveBudgetPolicy,
    WorkPriority,
    WorkStatus,
    authorize_action,
    authorize_artifact,
    advance_orchestration_state,
    advance_rollout_state,
    advance_work_unit,
    audit_entry_for_artifact,
    audit_entry_for_message,
    benchmark_case_matrix,
    build_capacity_planner,
    build_continuous_readiness_cycle,
    build_convergence_simulator,
    build_dispatch_plan,
    build_drift_monitor,
    build_escalation_router,
    build_evidence_ledger,
    build_governance_agenda,
    build_guardrail_portfolio,
    build_improvement_orchestrator,
    build_learning_register,
    build_operations_cockpit,
    build_portfolio_optimizer,
    build_policy_tuner,
    build_readiness_cadence,
    build_remediation_campaign,
    build_readiness_review,
    build_recovery_drill_suite,
    build_release_campaign,
    build_review_action_plan,
    build_risk_register,
    build_scenario_replay,
    build_runtime_scorecard,
    build_telemetry_snapshot,
    claim_for_work_unit,
    coordinate_escalations,
    command_message,
    coordinate_shadow_work,
    correlate_operation,
    core_state_for_runtime,
    detect_incidents,
    evaluate_dry_run,
    evaluate_gate,
    event_message,
    evidence_message,
    govern_recovery_orchestration,
    load_control_plane,
    ledger_for_wave,
    module_boundaries,
    module_dependency_graph,
    mission_profile_catalog,
    mission_profile_for_name,
    orchestration_state_for_runtime,
    orchestrate_recovery_for_rollout,
    protocol_context,
    recovery_checkpoint_for_state,
    recovery_outcome,
    rollback_directive_for_checkpoint,
    rollout_state_for_shadow,
    run_benchmark_harness,
    run_integrated_smoke_build,
    run_integrated_operations,
    run_operations_wave,
    runtime_dna_for_profile,
    runtime_dna_from_env,
    handoff_for_work_unit,
    operation_alerts,
    open_change_window,
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

    def test_kki_recovery_orchestration_rolls_back_blocked_rollout(self) -> None:
        shadow_artifacts = (
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
        shadow_plane = load_control_plane(shadow_artifacts, runtime_stage=RuntimeStage.PILOT, boundary="shadow")
        rollout_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="rollout")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
        )
        work_unit = work_unit_for_state(
            state,
            title="rollback blocked rollout",
            boundary="rollout",
            correlation_id="corr-138-rollback",
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
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
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

        orchestration = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-rollback",
        )

        self.assertIsInstance(orchestration, RecoveryOrchestration)
        self.assertEqual(orchestration.mode, RecoveryMode.ROLLBACK)
        self.assertEqual(orchestration.disposition, RecoveryDisposition.CONTAIN)
        self.assertEqual(orchestration.outcome.status, "rollback-active")
        self.assertFalse(orchestration.resume_ready)

    def test_kki_recovery_orchestration_restarts_held_rollout(self) -> None:
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
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="restart held rollout",
            boundary="rollout",
            correlation_id="corr-138-restart",
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
        recovery_identity = AuthorizationIdentity(
            slug="supervisor-recovery",
            kind=IdentityKind.SUPERVISOR,
            role=RoleName.SUPERVISOR,
            trust_level=TrustLevel.PRIVILEGED,
            boundary_scope=("recovery", "rollout"),
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
        held_state = advance_rollout_state(rollout_state, phase=RolloutPhase.HELD, blockers=("manual hold",))

        orchestration = orchestrate_recovery_for_rollout(
            held_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-restart",
        )

        self.assertEqual(orchestration.mode, RecoveryMode.RESTART)
        self.assertEqual(orchestration.disposition, RecoveryDisposition.RESTART)
        self.assertEqual(orchestration.outcome.status, "restart-active")
        self.assertFalse(orchestration.resume_ready)

    def test_kki_recovery_orchestration_prepares_reentry_for_canary(self) -> None:
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
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
        )
        work_unit = work_unit_for_state(
            state,
            title="reentry canary",
            boundary="rollout",
            correlation_id="corr-138-reentry",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-reentry",
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

        orchestration = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-reentry",
        )

        self.assertEqual(orchestration.mode, RecoveryMode.REENTRY)
        self.assertEqual(orchestration.disposition, RecoveryDisposition.RESUME)
        self.assertEqual(orchestration.outcome.status, "reentry-ready")
        self.assertTrue(orchestration.resume_ready)

    def test_kki_recovery_orchestration_blocks_resume_without_recovery_authority(self) -> None:
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
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-138",
        )
        work_unit = work_unit_for_state(
            state,
            title="blocked resume",
            boundary="rollout",
            correlation_id="corr-138-blocked",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-blocked-resume",
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
        denied_recovery_identity = AuthorizationIdentity(
            slug="observer-recovery",
            kind=IdentityKind.OPERATOR,
            role=RoleName.OBSERVER,
            trust_level=TrustLevel.RESTRICTED,
            boundary_scope=("recovery",),
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

        orchestration = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=denied_recovery_identity,
            evidence_ref="audit-recovery-blocked",
        )

        self.assertEqual(orchestration.gate_decision.outcome, GateOutcome.BLOCK)
        self.assertFalse(orchestration.resume_ready)
        self.assertEqual(orchestration.recovery_signal.severity, "info")

    def test_kki_human_governance_approves_reentry_release(self) -> None:
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
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
        )
        work_unit = work_unit_for_state(
            state,
            title="govern reentry",
            boundary="rollout",
            correlation_id="corr-139-approve",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        replay_unit = advance_work_unit(
            work_unit,
            status=WorkStatus.HANDED_OFF,
            attempt=1,
            handoff_ref="handoff-govern-approve",
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
        recovery = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-approve",
        )

        governance = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=governance_identity,
            decision=HumanDecision.APPROVE,
            audit_ref="audit-governance-approve",
        )

        self.assertIsInstance(governance, HumanLoopGovernance)
        self.assertEqual(governance.gate_decision.outcome, GateOutcome.GO)
        self.assertTrue(governance.release_authorized)
        self.assertEqual(governance.governance_signal.status, "authorized")

    def test_kki_human_governance_holds_restart_path(self) -> None:
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
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="govern hold",
            boundary="rollout",
            correlation_id="corr-139-hold",
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
        held_state = advance_rollout_state(rollout_state, phase=RolloutPhase.HELD, blockers=("manual hold",))
        recovery = orchestrate_recovery_for_rollout(
            held_state,
            control_plane=recovery_plane,
            identity=recovery_identity,
            evidence_ref="audit-recovery-hold",
        )

        governance = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=governance_identity,
            decision=HumanDecision.HOLD,
            audit_ref="audit-governance-hold",
        )

        self.assertFalse(governance.release_authorized)
        self.assertEqual(governance.governance_signal.status, "held")
        self.assertEqual(governance.governance_signal.severity, "warning")

    def test_kki_human_governance_escalates_when_requested(self) -> None:
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
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
            gates=GateReadiness(shadow=GateState.GUARDED),
        )
        work_unit = work_unit_for_state(
            state,
            title="govern escalate",
            boundary="rollout",
            correlation_id="corr-139-escalate",
            priority=WorkPriority.NORMAL,
            budget_share=0.14,
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=shadow_plane,
            identity=AuthorizationIdentity(
                slug="executor-shadow",
                kind=IdentityKind.MODULE,
                role=RoleName.EXECUTOR,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("shadow", "rollout"),
            ),
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.14,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=rollout_plane,
            identity=AuthorizationIdentity(
                slug="gatekeeper-rollout",
                kind=IdentityKind.OPERATOR,
                role=RoleName.GATEKEEPER,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("rollout", "governance"),
            ),
            evidence_ref="audit-rollout-policy",
        )
        held_state = advance_rollout_state(rollout_state, phase=RolloutPhase.HELD, blockers=("manual escalation",))
        recovery = orchestrate_recovery_for_rollout(
            held_state,
            control_plane=recovery_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-recovery",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.PRIVILEGED,
                boundary_scope=("recovery", "rollout"),
            ),
            evidence_ref="audit-recovery-escalate",
        )
        governance = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=AuthorizationIdentity(
                slug="gatekeeper-governance",
                kind=IdentityKind.OPERATOR,
                role=RoleName.GATEKEEPER,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("governance", "rollout"),
            ),
            decision=HumanDecision.ESCALATE,
            audit_ref="audit-governance-escalate",
        )

        self.assertFalse(governance.release_authorized)
        self.assertEqual(governance.governance_signal.status, "escalated")
        self.assertEqual(governance.governance_signal.severity, "warning")

    def test_kki_human_governance_override_requires_commitment(self) -> None:
        governance_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="governance")
        recovery_plane = load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="recovery")
        state = orchestration_state_for_runtime(
            runtime_dna_for_profile("pilot-runtime-dna", stage=RuntimeStage.PILOT),
            mission_ref="mission-139",
        )
        work_unit = work_unit_for_state(
            state,
            title="override path",
            boundary="rollout",
            correlation_id="corr-139-override",
            priority=WorkPriority.HIGH,
            budget_share=0.12,
        )
        coordination = coordinate_shadow_work(
            state,
            work_unit,
            control_plane=load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="shadow"),
            identity=AuthorizationIdentity(
                slug="executor-shadow",
                kind=IdentityKind.MODULE,
                role=RoleName.EXECUTOR,
                trust_level=TrustLevel.VERIFIED,
                boundary_scope=("shadow", "rollout"),
            ),
            available_roles=(RoleName.EXECUTOR,),
            observed_budget=0.12,
        )
        rollout_state = rollout_state_for_shadow(
            coordination,
            control_plane=load_control_plane((), runtime_stage=RuntimeStage.PILOT, boundary="rollout"),
            identity=AuthorizationIdentity(
                slug="observer-rollout",
                kind=IdentityKind.OPERATOR,
                role=RoleName.OBSERVER,
                trust_level=TrustLevel.RESTRICTED,
                boundary_scope=("rollout",),
            ),
        )
        recovery = orchestrate_recovery_for_rollout(
            rollout_state,
            control_plane=recovery_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-recovery",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.PRIVILEGED,
                boundary_scope=("recovery", "rollout"),
            ),
            evidence_ref="audit-recovery-override",
        )
        denied = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-governance",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.EMERGENCY,
                boundary_scope=("governance", "recovery"),
            ),
            decision=HumanDecision.OVERRIDE,
            audit_ref="audit-governance-override",
        )
        allowed = govern_recovery_orchestration(
            recovery,
            control_plane=governance_plane,
            identity=AuthorizationIdentity(
                slug="supervisor-governance",
                kind=IdentityKind.SUPERVISOR,
                role=RoleName.SUPERVISOR,
                trust_level=TrustLevel.EMERGENCY,
                boundary_scope=("governance", "recovery"),
            ),
            decision=HumanDecision.OVERRIDE,
            audit_ref="audit-governance-override",
            commitment_ref="commit-override",
        )

        self.assertEqual(denied.gate_decision.outcome, GateOutcome.BLOCK)
        self.assertFalse(denied.release_authorized)
        self.assertEqual(allowed.gate_decision.outcome, GateOutcome.ESCALATE)
        self.assertTrue(allowed.release_authorized)
        self.assertEqual(allowed.governance_signal.status, "authorized-override")

    def test_kki_integrated_operations_run_succeeds(self) -> None:
        run = run_integrated_operations(correlation_id="corr-140-ops")

        self.assertIsInstance(run, IntegratedOperationsRun)
        self.assertTrue(run.success)
        self.assertTrue(run.shadow_coordination.release_ready)
        self.assertTrue(run.rollout_state.promotion_ready)
        self.assertTrue(run.recovery_orchestration.resume_ready)
        self.assertTrue(run.human_governance.release_authorized)

    def test_kki_integrated_operations_run_exposes_full_chain(self) -> None:
        run = run_integrated_operations(correlation_id="corr-140-chain")

        self.assertEqual(run.work_unit.correlation_id, "corr-140-chain")
        self.assertEqual(run.shadow_coordination.work_unit.unit_id, run.work_unit.unit_id)
        self.assertEqual(run.rollout_state.work_unit_id, run.work_unit.unit_id)
        self.assertEqual(run.recovery_orchestration.rollout_state.work_unit_id, run.work_unit.unit_id)
        self.assertEqual(run.human_governance.subject_ref, run.recovery_orchestration.orchestration_id)

    def test_kki_integrated_operations_snapshot_contains_all_signals(self) -> None:
        run = run_integrated_operations(correlation_id="corr-140-snapshot")

        signal_names = [signal.signal_name for signal in run.final_snapshot.signals]
        self.assertIn("shadow-release", signal_names)
        self.assertIn("rollout-phase", signal_names)
        self.assertIn("recovery-orchestration", signal_names)
        self.assertIn("human-governance", signal_names)
        self.assertEqual(run.final_snapshot.highest_severity(), "info")

    def test_kki_integrated_operations_run_serializes_success(self) -> None:
        payload = run_integrated_operations(correlation_id="corr-140-dict").to_dict()

        self.assertTrue(payload["success"])
        self.assertEqual(payload["mission_profile"]["mission_ref"], "operations-run")
        self.assertEqual(payload["shadow_coordination"]["work_unit"]["correlation_id"], "corr-140-dict")
        self.assertEqual(payload["human_governance"]["decision"], "approve")

    def test_kki_mission_profile_preset_is_typed(self) -> None:
        mission = mission_profile_for_name("pilot-cutover")

        self.assertIsInstance(mission, MissionProfile)
        self.assertEqual(mission.scenario, MissionScenario.CUTOVER)
        self.assertEqual(mission.runtime_stage, RuntimeStage.PILOT)
        self.assertEqual(mission.policy.promotion_gate, "hold-until-shadow-green")
        self.assertEqual(mission.available_roles, (RoleName.EXECUTOR,))

    def test_kki_mission_profile_catalog_lists_presets(self) -> None:
        self.assertEqual(
            mission_profile_catalog(),
            ("pilot-cutover", "shadow-hardening", "recovery-drill"),
        )

    def test_kki_integrated_operations_run_accepts_named_mission_profile(self) -> None:
        run = run_integrated_operations(mission="pilot-cutover", correlation_id="corr-141-pilot")

        self.assertEqual(run.mission_profile.mission_ref, "pilot-cutover")
        self.assertEqual(run.orchestration_state.mission_ref, "pilot-cutover")
        self.assertEqual(run.runtime_dna.identity.profile, "pilot-runtime-dna")
        self.assertEqual(run.shadow_control_plane.effective_payload["mission_ref"], "pilot-cutover")
        self.assertEqual(run.work_unit.labels["mission_scenario"], "cutover")

    def test_kki_integrated_operations_run_uses_custom_mission_profile(self) -> None:
        run = run_integrated_operations(
            mission=MissionProfile(
                mission_ref="custom-hardening",
                title="custom hardening run",
                scenario=MissionScenario.HARDENING,
                runtime_stage=RuntimeStage.SHADOW,
                runtime_profile="resilient-runtime-dna",
                target_boundary=ModuleBoundaryName.ROLLOUT,
                work_priority=WorkPriority.CRITICAL,
                budget_share=0.14,
                observed_budget=0.13,
                policy=MissionPolicy(
                    resource_budget=0.81,
                    recovery_reserve=0.22,
                    drift_threshold=0.02,
                    promotion_gate="strict-shadow-window",
                ),
                labels={"campaign": "custom"},
            ),
            correlation_id="corr-141-custom",
        )

        self.assertEqual(run.mission_profile.mission_ref, "custom-hardening")
        self.assertEqual(run.runtime_dna.identity.stage, RuntimeStage.SHADOW)
        self.assertEqual(run.work_unit.priority, WorkPriority.CRITICAL)
        self.assertEqual(run.shadow_control_plane.effective_payload["drift_threshold"], 0.02)
        self.assertEqual(run.rollout_control_plane.effective_payload["promotion_gate"], "strict-shadow-window")

    def test_kki_operations_wave_executes_admitted_runs(self) -> None:
        wave = run_operations_wave(
            (
                "pilot-cutover",
                MissionProfile(
                    mission_ref="pilot-hardening",
                    title="pilot hardening pass",
                    scenario=MissionScenario.HARDENING,
                    runtime_stage=RuntimeStage.PILOT,
                    runtime_profile="pilot-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    work_priority=WorkPriority.HIGH,
                    budget_share=0.11,
                    observed_budget=0.1,
                    labels={"campaign": "pilot"},
                ),
            ),
            wave_id="wave-142-pilot",
        )

        self.assertIsInstance(wave, OperationsWave)
        self.assertEqual(len(wave.admitted_mission_refs), 2)
        self.assertEqual(wave.wave_signal.status, "executed")
        self.assertTrue(wave.success)

    def test_kki_operations_wave_holds_work_when_budget_exhausted(self) -> None:
        wave = run_operations_wave(
            (
                MissionProfile(
                    mission_ref="pilot-critical",
                    title="pilot critical cutover",
                    scenario=MissionScenario.CUTOVER,
                    runtime_stage=RuntimeStage.PILOT,
                    runtime_profile="pilot-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    work_priority=WorkPriority.CRITICAL,
                    budget_share=0.14,
                    observed_budget=0.14,
                ),
                MissionProfile(
                    mission_ref="pilot-normal",
                    title="pilot normal rollout",
                    scenario=MissionScenario.ROUTINE,
                    runtime_stage=RuntimeStage.PILOT,
                    runtime_profile="pilot-runtime-dna",
                    target_boundary=ModuleBoundaryName.ROLLOUT,
                    work_priority=WorkPriority.NORMAL,
                    budget_share=0.13,
                    observed_budget=0.12,
                ),
            ),
            wave_id="wave-142-budget",
            budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
        )

        self.assertEqual(wave.admitted_mission_refs, ("pilot-critical",))
        self.assertEqual(wave.held_mission_refs, ("pilot-normal",))
        self.assertEqual(wave.wave_signal.status, "partial")

    def test_kki_operations_wave_rejects_mixed_runtime_stages(self) -> None:
        with self.assertRaises(ValueError):
            run_operations_wave(("pilot-cutover", "shadow-hardening"), wave_id="wave-142-mixed")

    def test_kki_operations_wave_snapshot_contains_wave_signal(self) -> None:
        wave = run_operations_wave(("pilot-cutover",), wave_id="wave-142-signal")

        signal_names = [signal.signal_name for signal in wave.final_snapshot.signals]
        self.assertIn("operations-wave", signal_names)
        self.assertIn("shadow-release", signal_names)
        self.assertEqual(wave.wave_signal.status, "executed")
        self.assertTrue(wave.to_dict()["success"])

    def test_kki_run_ledger_compiles_entries_for_wave(self) -> None:
        ledger = ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-143-ledger"))

        self.assertIsInstance(ledger, OperationsRunLedger)
        self.assertEqual(len(ledger.entries), 1)
        self.assertIsInstance(ledger.entries[0], RunLedgerEntry)
        self.assertEqual(ledger.executed_mission_refs, ("pilot-cutover",))

    def test_kki_run_ledger_preserves_held_wave_entries(self) -> None:
        ledger = ledger_for_wave(
            run_operations_wave(
                (
                    MissionProfile(
                        mission_ref="ledger-critical",
                        title="ledger critical",
                        scenario=MissionScenario.CUTOVER,
                        runtime_stage=RuntimeStage.PILOT,
                        runtime_profile="pilot-runtime-dna",
                        target_boundary=ModuleBoundaryName.ROLLOUT,
                        work_priority=WorkPriority.CRITICAL,
                        budget_share=0.14,
                    ),
                    MissionProfile(
                        mission_ref="ledger-held",
                        title="ledger held",
                        scenario=MissionScenario.ROUTINE,
                        runtime_stage=RuntimeStage.PILOT,
                        runtime_profile="pilot-runtime-dna",
                        target_boundary=ModuleBoundaryName.ROLLOUT,
                        work_priority=WorkPriority.NORMAL,
                        budget_share=0.13,
                    ),
                ),
                wave_id="wave-143-held",
                budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
            )
        )

        self.assertEqual(ledger.executed_mission_refs, ("ledger-critical",))
        self.assertEqual(ledger.held_mission_refs, ("ledger-held",))
        held_entry = next(entry for entry in ledger.entries if entry.mission_ref == "ledger-held")
        self.assertFalse(held_entry.executed)
        self.assertEqual(held_entry.governance_status, "not-executed")

    def test_kki_run_ledger_snapshot_contains_ledger_signal(self) -> None:
        ledger = ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-143-signal"))

        signal_names = [signal.signal_name for signal in ledger.final_snapshot.signals]
        self.assertIn("run-ledger", signal_names)
        self.assertIn("operations-wave", signal_names)
        self.assertEqual(ledger.wave_signal.status, "compiled")

    def test_kki_run_ledger_serializes_status_counts(self) -> None:
        payload = ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-143-dict")).to_dict()

        self.assertEqual(payload["status_counts"]["admit"], 1)
        self.assertEqual(payload["entries"][0]["mission_ref"], "pilot-cutover")

    def test_kki_incident_report_is_clear_for_clean_wave(self) -> None:
        report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-144-clear")))

        self.assertIsInstance(report, IncidentReport)
        self.assertEqual(report.incidents, ())
        self.assertEqual(report.incident_signal.status, "clear")
        self.assertEqual(report.escalation_mission_refs, ())

    def test_kki_incident_report_detects_dispatch_hold(self) -> None:
        report = detect_incidents(
            ledger_for_wave(
                run_operations_wave(
                    (
                        MissionProfile(
                            mission_ref="incident-critical",
                            title="incident critical",
                            scenario=MissionScenario.CUTOVER,
                            runtime_stage=RuntimeStage.PILOT,
                            runtime_profile="pilot-runtime-dna",
                            target_boundary=ModuleBoundaryName.ROLLOUT,
                            work_priority=WorkPriority.CRITICAL,
                            budget_share=0.14,
                        ),
                        MissionProfile(
                            mission_ref="incident-held",
                            title="incident held",
                            scenario=MissionScenario.ROUTINE,
                            runtime_stage=RuntimeStage.PILOT,
                            runtime_profile="pilot-runtime-dna",
                            target_boundary=ModuleBoundaryName.ROLLOUT,
                            work_priority=WorkPriority.NORMAL,
                            budget_share=0.13,
                        ),
                    ),
                    wave_id="wave-144-held",
                    budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
                )
            )
        )

        self.assertEqual(len(report.incidents), 1)
        self.assertEqual(report.incidents[0].cause, IncidentCause.DISPATCH)
        self.assertEqual(report.incidents[0].severity, IncidentSeverity.WARNING)
        self.assertEqual(report.escalation_mission_refs, ("incident-held",))

    def test_kki_incident_report_detects_governance_escalation(self) -> None:
        report = detect_incidents(
            ledger_for_wave(
                run_operations_wave(
                    (
                        MissionProfile(
                            mission_ref="incident-governance",
                            title="incident governance",
                            scenario=MissionScenario.CUTOVER,
                            runtime_stage=RuntimeStage.PILOT,
                            runtime_profile="pilot-runtime-dna",
                            target_boundary=ModuleBoundaryName.ROLLOUT,
                            governance_decision=HumanDecision.ESCALATE,
                        ),
                    ),
                    wave_id="wave-144-governance",
                )
            )
        )

        self.assertEqual(len(report.incidents), 1)
        self.assertEqual(report.incidents[0].cause, IncidentCause.GOVERNANCE)
        self.assertEqual(report.incident_signal.status, "attention-required")

    def test_kki_incident_report_serializes_critical_entries(self) -> None:
        manual_report = IncidentReport(
            wave_id="wave-144-manual",
            ledger=ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-144-base")),
            incidents=(
                OperationsIncident(
                    incident_id="incident-wave-144-manual-critical",
                    wave_id="wave-144-manual",
                    severity=IncidentSeverity.CRITICAL,
                    cause=IncidentCause.RECOVERY,
                    summary="manual critical recovery incident",
                    mission_refs=("pilot-cutover",),
                    trigger_statuses=("rollback-active",),
                    escalation_required=True,
                ),
            ),
            incident_signal=TelemetrySignal(
                signal_name="incident-report",
                boundary=ModuleBoundaryName.TELEMETRY,
                correlation_id="wave-144-manual",
                severity="critical",
                status="critical-incidents",
            ),
            final_snapshot=build_telemetry_snapshot(
                runtime_stage=RuntimeStage.PILOT,
                signals=(
                    TelemetrySignal(
                        signal_name="incident-report",
                        boundary=ModuleBoundaryName.TELEMETRY,
                        correlation_id="wave-144-manual",
                        severity="critical",
                        status="critical-incidents",
                    ),
                ),
            ),
        ).to_dict()

        self.assertEqual(manual_report["critical_incidents"][0]["cause"], "recovery")
        self.assertEqual(manual_report["escalation_mission_refs"], ["pilot-cutover"])

    def test_kki_escalation_plan_is_clear_without_incidents(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-145-clear")))
        )

        self.assertIsInstance(plan, EscalationPlan)
        self.assertEqual(plan.directives, ())
        self.assertEqual(plan.escalation_signal.status, "clear")

    def test_kki_escalation_plan_replans_dispatch_holds(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(
                ledger_for_wave(
                    run_operations_wave(
                        (
                            MissionProfile(
                                mission_ref="escalation-critical",
                                title="escalation critical",
                                scenario=MissionScenario.CUTOVER,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                work_priority=WorkPriority.CRITICAL,
                                budget_share=0.14,
                            ),
                            MissionProfile(
                                mission_ref="escalation-held",
                                title="escalation held",
                                scenario=MissionScenario.ROUTINE,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                work_priority=WorkPriority.NORMAL,
                                budget_share=0.13,
                            ),
                        ),
                        wave_id="wave-145-dispatch",
                        budget_policy=WaveBudgetPolicy(total_budget=0.3, reserve_floor=0.12, max_parallel=2),
                    )
                )
            )
        )

        self.assertEqual(len(plan.directives), 1)
        self.assertIsInstance(plan.directives[0], EscalationDirective)
        self.assertEqual(plan.directives[0].path, EscalationPath.DISPATCH_REPLAN)
        self.assertEqual(plan.blocked_release_refs, ("escalation-held",))

    def test_kki_escalation_plan_routes_governance_review(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(
                ledger_for_wave(
                    run_operations_wave(
                        (
                            MissionProfile(
                                mission_ref="escalation-governance",
                                title="escalation governance",
                                scenario=MissionScenario.CUTOVER,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                governance_decision=HumanDecision.ESCALATE,
                            ),
                        ),
                        wave_id="wave-145-governance",
                    )
                )
            )
        )

        self.assertEqual(plan.directives[0].path, EscalationPath.GOVERNANCE_REVIEW)
        self.assertEqual(plan.governance_review_refs, ("escalation-governance",))
        self.assertEqual(plan.escalation_signal.status, "response-required")

    def test_kki_escalation_plan_contains_critical_recovery_response(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-145-base")))
        critical_report = IncidentReport(
            wave_id=base_report.wave_id,
            ledger=base_report.ledger,
            incidents=(
                OperationsIncident(
                    incident_id="incident-wave-145-critical-recovery",
                    wave_id=base_report.wave_id,
                    severity=IncidentSeverity.CRITICAL,
                    cause=IncidentCause.RECOVERY,
                    summary="critical recovery rollback incident",
                    mission_refs=("pilot-cutover",),
                    trigger_statuses=("rollback-active",),
                    escalation_required=True,
                ),
            ),
            incident_signal=TelemetrySignal(
                signal_name="incident-report",
                boundary=ModuleBoundaryName.TELEMETRY,
                correlation_id=base_report.wave_id,
                severity="critical",
                status="critical-incidents",
            ),
            final_snapshot=base_report.final_snapshot,
        )
        plan = coordinate_escalations(critical_report)

        self.assertEqual(plan.directives[0].path, EscalationPath.ROLLBACK_CONTAINMENT)
        self.assertEqual(plan.directives[0].recovery_disposition, RecoveryDisposition.CONTAIN)
        self.assertEqual(plan.escalation_signal.status, "critical-response")

    def test_kki_change_window_opens_for_clean_plan(self) -> None:
        window = open_change_window(
            (
                coordinate_escalations(
                    detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-146-open")))
                ),
            ),
            window_id="window-146-open",
        )

        self.assertIsInstance(window, ChangeWindow)
        self.assertIsInstance(window.entries[0], ChangeWindowEntry)
        self.assertEqual(window.status, ChangeWindowStatus.OPEN)
        self.assertEqual(window.allowed_promotions, ("pilot-cutover",))

    def test_kki_change_window_guards_governance_review(self) -> None:
        plan = coordinate_escalations(
            detect_incidents(
                ledger_for_wave(
                    run_operations_wave(
                        (
                            MissionProfile(
                                mission_ref="window-governance",
                                title="window governance",
                                scenario=MissionScenario.CUTOVER,
                                runtime_stage=RuntimeStage.PILOT,
                                runtime_profile="pilot-runtime-dna",
                                target_boundary=ModuleBoundaryName.ROLLOUT,
                                governance_decision=HumanDecision.ESCALATE,
                            ),
                        ),
                        wave_id="wave-146-guarded",
                    )
                )
            )
        )
        window = open_change_window((plan,), window_id="window-146-guarded")

        self.assertEqual(window.status, ChangeWindowStatus.GUARDED)
        self.assertEqual(window.blocked_refs, ("window-governance",))

    def test_kki_change_window_sets_recovery_only_mode(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-146-recovery")))
        recovery_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-146-restart",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.WARNING,
                        cause=IncidentCause.RECOVERY,
                        summary="restart recovery path",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("restart-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="warning",
                    status="attention-required",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((recovery_plan,), window_id="window-146-recovery")

        self.assertEqual(window.status, ChangeWindowStatus.RECOVERY_ONLY)
        self.assertEqual(window.recovery_only_refs, ("pilot-cutover",))

    def test_kki_change_window_blocks_critical_containment(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-146-blocked")))
        critical_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-146-critical",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.CRITICAL,
                        cause=IncidentCause.RECOVERY,
                        summary="critical rollback containment",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("rollback-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="critical",
                    status="critical-incidents",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((critical_plan,), window_id="window-146-blocked")

        self.assertEqual(window.status, ChangeWindowStatus.BLOCKED)
        self.assertEqual(window.blocked_refs, ("pilot-cutover",))

    def test_kki_release_campaign_builds_ready_promotion_path(self) -> None:
        window = open_change_window(
            (
                coordinate_escalations(
                    detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-147-ready")))
                ),
            ),
            window_id="window-147-ready",
        )
        campaign = build_release_campaign((window,), campaign_id="campaign-147-ready")

        self.assertIsInstance(campaign, ReleaseCampaign)
        self.assertIsInstance(campaign.stages[0], ReleaseCampaignStage)
        self.assertEqual(campaign.status, ReleaseCampaignStatus.READY)
        self.assertEqual(campaign.promotion_refs, ("pilot-cutover",))
        self.assertIn(ReleaseCampaignStageType.PROMOTION_WAVE, {stage.stage_type for stage in campaign.stages})

    def test_kki_release_campaign_routes_governance_review_stage(self) -> None:
        window = open_change_window(
            (
                coordinate_escalations(
                    detect_incidents(
                        ledger_for_wave(
                            run_operations_wave(
                                (
                                    MissionProfile(
                                        mission_ref="campaign-governance",
                                        title="campaign governance",
                                        scenario=MissionScenario.CUTOVER,
                                        runtime_stage=RuntimeStage.PILOT,
                                        runtime_profile="pilot-runtime-dna",
                                        target_boundary=ModuleBoundaryName.ROLLOUT,
                                        governance_decision=HumanDecision.ESCALATE,
                                    ),
                                ),
                                wave_id="wave-147-guarded",
                            )
                        )
                    )
                ),
            ),
            window_id="window-147-guarded",
        )
        campaign = build_release_campaign((window,), campaign_id="campaign-147-guarded")

        self.assertEqual(campaign.status, ReleaseCampaignStatus.GUARDED)
        self.assertEqual(campaign.governance_review_refs, ("campaign-governance",))
        self.assertIn(ReleaseCampaignStageType.GOVERNANCE_REVIEW, {stage.stage_type for stage in campaign.stages})

    def test_kki_release_campaign_preserves_recovery_only_stage(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-147-recovery")))
        recovery_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-147-restart",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.WARNING,
                        cause=IncidentCause.RECOVERY,
                        summary="restart recovery path",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("restart-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="warning",
                    status="attention-required",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((recovery_plan,), window_id="window-147-recovery")
        campaign = build_release_campaign((window,), campaign_id="campaign-147-recovery")

        self.assertEqual(campaign.status, ReleaseCampaignStatus.RECOVERY_ONLY)
        self.assertEqual(campaign.recovery_only_refs, ("pilot-cutover",))
        self.assertNotIn(ReleaseCampaignStageType.PROMOTION_WAVE, {stage.stage_type for stage in campaign.stages})
        self.assertIn(ReleaseCampaignStageType.RECOVERY_WAVE, {stage.stage_type for stage in campaign.stages})

    def test_kki_release_campaign_blocks_containment_stage(self) -> None:
        base_report = detect_incidents(ledger_for_wave(run_operations_wave(("pilot-cutover",), wave_id="wave-147-blocked")))
        critical_plan = coordinate_escalations(
            IncidentReport(
                wave_id=base_report.wave_id,
                ledger=base_report.ledger,
                incidents=(
                    OperationsIncident(
                        incident_id="incident-wave-147-critical",
                        wave_id=base_report.wave_id,
                        severity=IncidentSeverity.CRITICAL,
                        cause=IncidentCause.RECOVERY,
                        summary="critical rollback containment",
                        mission_refs=("pilot-cutover",),
                        trigger_statuses=("rollback-active",),
                        escalation_required=True,
                    ),
                ),
                incident_signal=TelemetrySignal(
                    signal_name="incident-report",
                    boundary=ModuleBoundaryName.TELEMETRY,
                    correlation_id=base_report.wave_id,
                    severity="critical",
                    status="critical-incidents",
                ),
                final_snapshot=base_report.final_snapshot,
            )
        )
        window = open_change_window((critical_plan,), window_id="window-147-blocked")
        campaign = build_release_campaign((window,), campaign_id="campaign-147-blocked")

        self.assertEqual(campaign.status, ReleaseCampaignStatus.BLOCKED)
        self.assertEqual(campaign.blocked_refs, ("pilot-cutover",))
        self.assertIn(ReleaseCampaignStageType.CONTAINMENT, {stage.stage_type for stage in campaign.stages})

    def test_kki_benchmark_case_matrix_exposes_canonical_cases(self) -> None:
        cases = benchmark_case_matrix()

        self.assertEqual(len(cases), 4)
        self.assertIsInstance(cases[0], BenchmarkCase)
        self.assertEqual(
            tuple(case.case_id for case in cases),
            ("pilot-ready", "shadow-guarded", "recovery-resume", "pilot-containment"),
        )

    def test_kki_benchmark_harness_runs_ready_case(self) -> None:
        case = BenchmarkCase(
            case_id="benchmark-ready",
            title="benchmark ready",
            missions=(mission_profile_for_name("pilot-cutover"),),
            release_mode=BenchmarkReleaseMode.READY,
        )
        harness = run_benchmark_harness((case,), harness_id="harness-148-ready")

        self.assertIsInstance(harness, BenchmarkHarness)
        self.assertEqual(harness.results[0].status, ReleaseCampaignStatus.READY)
        self.assertEqual(harness.results[0].release_campaign.promotion_refs, ("pilot-cutover",))
        self.assertEqual(harness.ready_case_ids, ("benchmark-ready",))

    def test_kki_benchmark_harness_runs_recovery_case(self) -> None:
        case = BenchmarkCase(
            case_id="benchmark-recovery",
            title="benchmark recovery",
            missions=(mission_profile_for_name("recovery-drill"),),
            release_mode=BenchmarkReleaseMode.RECOVERY_ONLY,
        )
        harness = run_benchmark_harness((case,), harness_id="harness-148-recovery")

        self.assertEqual(harness.results[0].status, ReleaseCampaignStatus.RECOVERY_ONLY)
        self.assertEqual(harness.results[0].release_campaign.recovery_only_refs, ("recovery-drill",))
        self.assertEqual(harness.recovery_case_ids, ("benchmark-recovery",))

    def test_kki_benchmark_harness_aggregates_matrix_statuses(self) -> None:
        harness = run_benchmark_harness(harness_id="harness-148-matrix")

        self.assertEqual(harness.harness_signal.status, "blocked")
        self.assertEqual(harness.ready_case_ids, ("pilot-ready",))
        self.assertEqual(harness.guarded_case_ids, ("shadow-guarded",))
        self.assertEqual(harness.recovery_case_ids, ("recovery-resume",))
        self.assertEqual(harness.blocked_case_ids, ("pilot-containment",))

    def test_kki_runtime_scorecard_scores_ready_case(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="scorecard-ready",
                    title="scorecard ready",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.READY,
                ),
            ),
            harness_id="harness-149-ready",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-149-ready")

        self.assertIsInstance(scorecard, RuntimeScorecard)
        self.assertIsInstance(scorecard.entries[0], RuntimeScorecardEntry)
        self.assertEqual(scorecard.scorecard_signal.status, "healthy")
        self.assertGreater(scorecard.entries[0].overall_score, 0.8)
        self.assertEqual(scorecard.healthy_case_ids, ("scorecard-ready",))

    def test_kki_runtime_scorecard_marks_guarded_case_for_attention(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="scorecard-guarded",
                    title="scorecard guarded",
                    missions=(benchmark_case_matrix()[1].missions[0],),
                    release_mode=BenchmarkReleaseMode.GUARDED,
                ),
            ),
            harness_id="harness-149-guarded",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-149-guarded")

        self.assertEqual(scorecard.scorecard_signal.status, "attention-required")
        self.assertLess(scorecard.entries[0].governance_score, scorecard.entries[0].success_score)
        self.assertEqual(scorecard.attention_case_ids, ("scorecard-guarded",))

    def test_kki_runtime_scorecard_marks_blocked_case_critical(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="scorecard-blocked",
                    title="scorecard blocked",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.BLOCKED,
                ),
            ),
            harness_id="harness-149-blocked",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-149-blocked")

        self.assertEqual(scorecard.scorecard_signal.status, "critical-review")
        self.assertLess(scorecard.entries[0].overall_score, 0.4)
        self.assertEqual(scorecard.attention_case_ids, ("scorecard-blocked",))

    def test_kki_runtime_scorecard_aggregates_matrix_scores(self) -> None:
        scorecard = build_runtime_scorecard(scorecard_id="scorecard-149-matrix")

        self.assertEqual(scorecard.scorecard_signal.status, "critical-review")
        self.assertEqual(scorecard.healthy_case_ids, ("pilot-ready",))
        self.assertEqual(scorecard.attention_case_ids, ("shadow-guarded", "recovery-resume", "pilot-containment"))
        self.assertGreater(scorecard.average_overall_score, 0.4)

    def test_kki_readiness_review_marks_ready_case_release_ready(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="review-ready",
                    title="review ready",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.READY,
                ),
            ),
            harness_id="harness-150-ready",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-150-ready")
        review = build_readiness_review(scorecard, review_id="review-150-ready")

        self.assertIsInstance(review, ReadinessReview)
        self.assertEqual(review.review_signal.status, "ready")
        self.assertTrue(review.release_ready)
        self.assertEqual(review.healthy_case_ids, ("review-ready",))

    def test_kki_readiness_review_routes_guarded_case_to_review(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="review-guarded",
                    title="review guarded",
                    missions=(benchmark_case_matrix()[1].missions[0],),
                    release_mode=BenchmarkReleaseMode.GUARDED,
                ),
            ),
            harness_id="harness-150-guarded",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-150-guarded")
        review = build_readiness_review(scorecard, review_id="review-150-guarded")

        self.assertEqual(review.review_signal.status, "review-required")
        self.assertEqual(review.attention_case_ids, ("review-guarded",))
        self.assertTrue(any(finding.severity is ReadinessFindingSeverity.WARNING for finding in review.findings))

    def test_kki_readiness_review_marks_blocked_case_not_ready(self) -> None:
        harness = run_benchmark_harness(
            (
                BenchmarkCase(
                    case_id="review-blocked",
                    title="review blocked",
                    missions=(mission_profile_for_name("pilot-cutover"),),
                    release_mode=BenchmarkReleaseMode.BLOCKED,
                ),
            ),
            harness_id="harness-150-blocked",
        )
        scorecard = build_runtime_scorecard(harness, scorecard_id="scorecard-150-blocked")
        review = build_readiness_review(scorecard, review_id="review-150-blocked")

        self.assertEqual(review.review_signal.status, "not-ready")
        self.assertFalse(review.release_ready)
        self.assertEqual(review.blocked_case_ids, ("review-blocked",))
        self.assertIsInstance(review.findings[0], ReadinessFinding)
        self.assertEqual(review.findings[0].severity, ReadinessFindingSeverity.CRITICAL)

    def test_kki_readiness_review_aggregates_default_chain(self) -> None:
        review = build_readiness_review(review_id="review-150-matrix")

        self.assertEqual(review.review_signal.status, "not-ready")
        self.assertEqual(review.healthy_case_ids, ("pilot-ready",))
        self.assertEqual(review.blocked_case_ids, ("pilot-containment",))
        self.assertFalse(review.release_ready)

    def test_kki_review_action_plan_creates_monitoring_for_ready_case(self) -> None:
        review = build_readiness_review(
            build_runtime_scorecard(
                run_benchmark_harness(
                    (
                        BenchmarkCase(
                            case_id="action-ready",
                            title="action ready",
                            missions=(mission_profile_for_name("pilot-cutover"),),
                            release_mode=BenchmarkReleaseMode.READY,
                        ),
                    ),
                    harness_id="harness-151-ready",
                ),
                scorecard_id="scorecard-151-ready",
            ),
            review_id="review-151-ready",
        )
        plan = build_review_action_plan(review, plan_id="plan-151-ready")

        self.assertIsInstance(plan, ReviewActionPlan)
        self.assertIsInstance(plan.actions[0], ReviewActionItem)
        self.assertEqual(plan.plan_signal.status, "planned")
        self.assertEqual(plan.actions[0].priority, ReviewActionPriority.LOW)
        self.assertEqual(plan.actions[0].action_type, ReviewActionType.MONITOR)

    def test_kki_review_action_plan_routes_governance_findings(self) -> None:
        review = build_readiness_review(
            build_runtime_scorecard(
                run_benchmark_harness(
                    (
                        BenchmarkCase(
                            case_id="action-guarded",
                            title="action guarded",
                            missions=(benchmark_case_matrix()[1].missions[0],),
                            release_mode=BenchmarkReleaseMode.GUARDED,
                        ),
                    ),
                    harness_id="harness-151-guarded",
                ),
                scorecard_id="scorecard-151-guarded",
            ),
            review_id="review-151-guarded",
        )
        plan = build_review_action_plan(review, plan_id="plan-151-guarded")

        self.assertEqual(plan.plan_signal.status, "priority-actions")
        self.assertEqual(plan.actions[0].owner, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(plan.actions[0].target_status, "governance-reviewed")

    def test_kki_review_action_plan_routes_critical_remediation(self) -> None:
        review = build_readiness_review(
            build_runtime_scorecard(
                run_benchmark_harness(
                    (
                        BenchmarkCase(
                            case_id="action-blocked",
                            title="action blocked",
                            missions=(mission_profile_for_name("pilot-cutover"),),
                            release_mode=BenchmarkReleaseMode.BLOCKED,
                        ),
                    ),
                    harness_id="harness-151-blocked",
                ),
                scorecard_id="scorecard-151-blocked",
            ),
            review_id="review-151-blocked",
        )
        plan = build_review_action_plan(review, plan_id="plan-151-blocked")

        self.assertEqual(plan.plan_signal.status, "critical-actions")
        self.assertEqual(plan.critical_case_ids, ("action-blocked",))
        self.assertEqual(plan.blocked_case_ids, ("action-blocked",))
        self.assertEqual(plan.actions[0].owner, ModuleBoundaryName.RECOVERY)

    def test_kki_review_action_plan_aggregates_default_review(self) -> None:
        plan = build_review_action_plan(plan_id="plan-151-matrix")

        self.assertEqual(plan.plan_signal.status, "critical-actions")
        self.assertEqual(plan.critical_case_ids, ("pilot-containment",))
        self.assertIn(ModuleBoundaryName.GOVERNANCE, plan.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, plan.owner_boundaries)

    def test_kki_risk_register_observes_healthy_case(self) -> None:
        plan = build_review_action_plan(
            build_readiness_review(
                build_runtime_scorecard(
                    run_benchmark_harness(
                        (
                            BenchmarkCase(
                                case_id="risk-ready",
                                title="risk ready",
                                missions=(mission_profile_for_name("pilot-cutover"),),
                                release_mode=BenchmarkReleaseMode.READY,
                            ),
                        ),
                        harness_id="harness-152-ready",
                    ),
                    scorecard_id="scorecard-152-ready",
                ),
                review_id="review-152-ready",
            ),
            plan_id="plan-152-ready",
        )
        register = build_risk_register(plan, register_id="register-152-ready")

        self.assertIsInstance(register, RiskRegister)
        self.assertIsInstance(register.risks[0], RiskRecord)
        self.assertEqual(register.register_signal.status, "observed")
        self.assertEqual(register.risks[0].mitigation_status, RiskMitigationStatus.OBSERVE)
        self.assertEqual(register.risks[0].likelihood, RiskLikelihood.LOW)

    def test_kki_risk_register_tracks_governance_risk(self) -> None:
        plan = build_review_action_plan(plan_id="plan-152-guarded")
        governance_only_plan = ReviewActionPlan(
            plan_id=plan.plan_id,
            review=plan.review,
            actions=(next(action for action in plan.actions if action.case_id == "shadow-guarded"),),
            plan_signal=plan.plan_signal,
            final_snapshot=plan.final_snapshot,
        )
        register = build_risk_register(governance_only_plan, register_id="register-152-guarded")

        self.assertEqual(register.register_signal.status, "active-risks")
        self.assertEqual(register.risks[0].owner, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(register.risks[0].impact, RiskImpact.HIGH)
        self.assertEqual(register.active_case_ids, ("shadow-guarded",))

    def test_kki_risk_register_tracks_blocking_risk(self) -> None:
        plan = build_review_action_plan(plan_id="plan-152-blocked")
        blocked_only_plan = ReviewActionPlan(
            plan_id=plan.plan_id,
            review=plan.review,
            actions=(next(action for action in plan.actions if action.case_id == "pilot-containment"),),
            plan_signal=plan.plan_signal,
            final_snapshot=plan.final_snapshot,
        )
        register = build_risk_register(blocked_only_plan, register_id="register-152-blocked")

        self.assertEqual(register.register_signal.status, "blocking-risks")
        self.assertEqual(register.blocking_case_ids, ("pilot-containment",))
        self.assertEqual(register.risks[0].impact, RiskImpact.CRITICAL)
        self.assertEqual(register.risks[0].mitigation_status, RiskMitigationStatus.BLOCKING)

    def test_kki_risk_register_aggregates_default_plan(self) -> None:
        register = build_risk_register(register_id="register-152-matrix")

        self.assertEqual(register.register_signal.status, "blocking-risks")
        self.assertIn("pilot-containment", register.blocking_case_ids)
        self.assertIn(ModuleBoundaryName.GOVERNANCE, register.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, register.owner_boundaries)

    def test_kki_guardrail_portfolio_monitors_healthy_case(self) -> None:
        portfolio = build_guardrail_portfolio(
            build_risk_register(
                build_review_action_plan(
                    build_readiness_review(
                        build_runtime_scorecard(
                            run_benchmark_harness(
                                (
                                    BenchmarkCase(
                                        case_id="guardrail-ready",
                                        title="guardrail ready",
                                        missions=(mission_profile_for_name("pilot-cutover"),),
                                        release_mode=BenchmarkReleaseMode.READY,
                                    ),
                                ),
                                harness_id="harness-153-ready",
                            ),
                            scorecard_id="scorecard-153-ready",
                        ),
                        review_id="review-153-ready",
                    ),
                    plan_id="plan-153-ready",
                ),
                register_id="register-153-ready",
            ),
            portfolio_id="portfolio-153-ready",
        )

        self.assertIsInstance(portfolio, GuardrailPortfolio)
        self.assertIsInstance(portfolio.guardrails[0], Guardrail)
        self.assertEqual(portfolio.portfolio_signal.status, "monitoring")
        self.assertEqual(portfolio.guardrails[0].policy_mode, GuardrailPolicyMode.MONITOR)
        self.assertEqual(portfolio.guardrails[0].domain, GuardrailDomain.TELEMETRY)

    def test_kki_guardrail_portfolio_holds_governance_case(self) -> None:
        portfolio = build_guardrail_portfolio(portfolio_id="portfolio-153-guarded")
        governance_guardrail = next(guardrail for guardrail in portfolio.guardrails if guardrail.case_id == "shadow-guarded")

        self.assertEqual(portfolio.portfolio_signal.status, "containment-guardrails")
        self.assertEqual(governance_guardrail.domain, GuardrailDomain.GOVERNANCE)
        self.assertEqual(governance_guardrail.policy_mode, GuardrailPolicyMode.HOLD)

    def test_kki_guardrail_portfolio_contains_blocking_case(self) -> None:
        portfolio = build_guardrail_portfolio(portfolio_id="portfolio-153-blocked")
        blocking_guardrail = next(guardrail for guardrail in portfolio.guardrails if guardrail.case_id == "pilot-containment")

        self.assertEqual(blocking_guardrail.policy_mode, GuardrailPolicyMode.CONTAIN)
        self.assertEqual(blocking_guardrail.domain, GuardrailDomain.RECOVERY)
        self.assertEqual(portfolio.blocking_case_ids, ("pilot-containment",))

    def test_kki_guardrail_portfolio_aggregates_domains(self) -> None:
        portfolio = build_guardrail_portfolio(portfolio_id="portfolio-153-matrix")

        self.assertIn(GuardrailDomain.GOVERNANCE, portfolio.domains)
        self.assertIn(GuardrailDomain.RECOVERY, portfolio.domains)
        self.assertIn(ModuleBoundaryName.GOVERNANCE, portfolio.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, portfolio.owner_boundaries)

    def test_kki_scenario_replay_replays_guarded_case(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-guarded")
        guarded_item = next(item for item in suite.items if item.source_case_id == "shadow-guarded")

        self.assertIsInstance(suite, ScenarioReplaySuite)
        self.assertIsInstance(guarded_item, ScenarioReplayItem)
        self.assertEqual(guarded_item.replay_mode, ReplayMode.GUARDED)
        self.assertIn("shadow-guarded", suite.replayed_case_ids)

    def test_kki_scenario_replay_contains_blocked_case(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-blocked")
        blocked_result = next(result for result in suite.results if result.item.source_case_id == "pilot-containment")

        self.assertIsInstance(blocked_result, ScenarioReplayResult)
        self.assertEqual(blocked_result.item.replay_mode, ReplayMode.CONTAINED)
        self.assertEqual(blocked_result.result.status, ReleaseCampaignStatus.BLOCKED)
        self.assertEqual(suite.blocked_case_ids, ("pilot-containment",))

    def test_kki_scenario_replay_can_include_ready_case(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-ready", include_ready=True)
        ready_result = next(result for result in suite.results if result.item.source_case_id == "pilot-ready")

        self.assertEqual(ready_result.item.replay_mode, ReplayMode.OBSERVED)
        self.assertTrue(ready_result.stable)

    def test_kki_scenario_replay_aggregates_attention_cases(self) -> None:
        suite = build_scenario_replay(replay_id="replay-154-matrix")

        self.assertEqual(suite.replay_signal.status, "blocked-replays")
        self.assertEqual(suite.replayed_case_ids, ("shadow-guarded", "recovery-resume", "pilot-containment"))
        self.assertEqual(suite.blocked_case_ids, ("pilot-containment",))

    def test_kki_drift_monitor_tracks_stable_ready_case(self) -> None:
        replay_suite = build_scenario_replay(replay_id="replay-155-ready", include_ready=True)
        ready_only_suite = ScenarioReplaySuite(
            replay_id=replay_suite.replay_id,
            source_harness=replay_suite.source_harness,
            guardrail_portfolio=replay_suite.guardrail_portfolio,
            items=(next(item for item in replay_suite.items if item.source_case_id == "pilot-ready"),),
            results=(next(result for result in replay_suite.results if result.item.source_case_id == "pilot-ready"),),
            replay_signal=replay_suite.replay_signal,
            final_snapshot=replay_suite.final_snapshot,
        )
        monitor = build_drift_monitor(replay_suite=ready_only_suite, monitor_id="drift-155-ready")
        observation = monitor.observations[0]

        self.assertIsInstance(monitor, DriftMonitor)
        self.assertIsInstance(observation, DriftObservation)
        self.assertTrue(observation.stable)
        self.assertEqual(observation.severity, DriftSeverity.STABLE)

    def test_kki_drift_monitor_detects_governance_violation(self) -> None:
        monitor = build_drift_monitor(monitor_id="drift-155-governance")
        observation = next(item for item in monitor.observations if item.case_id == "shadow-guarded")

        self.assertIn("shadow-guarded", monitor.violating_case_ids)
        self.assertEqual(observation.severity, DriftSeverity.CRITICAL)
        self.assertTrue(any("governance_score" in violation for violation in observation.guardrail_violations))

    def test_kki_drift_monitor_detects_blocked_case_violation(self) -> None:
        monitor = build_drift_monitor(monitor_id="drift-155-blocked")
        observation = next(item for item in monitor.observations if item.case_id == "pilot-containment")

        self.assertEqual(observation.replay_status, ReleaseCampaignStatus.BLOCKED)
        self.assertIn("pilot-containment", monitor.violating_case_ids)
        self.assertEqual(observation.severity, DriftSeverity.CRITICAL)

    def test_kki_drift_monitor_aggregates_recovery_and_governance(self) -> None:
        monitor = build_drift_monitor(monitor_id="drift-155-matrix")

        self.assertEqual(monitor.drift_signal.status, "guardrail-violations")
        self.assertIn("shadow-guarded", monitor.governance_drift_case_ids)
        self.assertIn("pilot-containment", monitor.violating_case_ids)

    def test_kki_improvement_orchestrator_prioritizes_blocked_case(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-critical")
        blocked_wave = next(wave for wave in orchestrator.waves if wave.case_id == "pilot-containment")

        self.assertIsInstance(orchestrator, ImprovementOrchestrator)
        self.assertIsInstance(blocked_wave, ImprovementWave)
        self.assertEqual(blocked_wave.priority, ImprovementPriority.CRITICAL)
        self.assertEqual(blocked_wave.execution_mode, ImprovementExecutionMode.CONTAINED)
        self.assertIn("pilot-containment", orchestrator.blocked_case_ids)

    def test_kki_improvement_orchestrator_governs_shadow_case(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-governed")
        governance_wave = next(wave for wave in orchestrator.waves if wave.case_id == "shadow-guarded")

        self.assertEqual(governance_wave.owner, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(governance_wave.execution_mode, ImprovementExecutionMode.GOVERNED)
        self.assertEqual(governance_wave.priority, ImprovementPriority.HIGH)

    def test_kki_improvement_orchestrator_normalizes_budgets(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-budget")
        total_budget = sum(wave.budget_share for wave in orchestrator.waves)
        blocked_wave = next(wave for wave in orchestrator.waves if wave.case_id == "pilot-containment")
        healthy_wave = next(wave for wave in orchestrator.waves if wave.case_id == "pilot-ready")

        self.assertAlmostEqual(total_budget, 1.0, places=6)
        self.assertGreater(blocked_wave.budget_share, healthy_wave.budget_share)

    def test_kki_improvement_orchestrator_aggregates_waves(self) -> None:
        orchestrator = build_improvement_orchestrator(orchestrator_id="orchestrator-156-matrix")

        self.assertEqual(orchestrator.orchestration_signal.status, "critical-waves")
        self.assertIn(ModuleBoundaryName.GOVERNANCE, orchestrator.owner_boundaries)
        self.assertIn(ModuleBoundaryName.RECOVERY, orchestrator.owner_boundaries)

    def test_kki_remediation_campaign_contains_blocked_case(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-blocked")
        blocked_stage = next(
            stage for stage in campaign.stages if stage.case_id == "pilot-containment" and stage.stage_type is RemediationCampaignStageType.CONTAINMENT
        )

        self.assertIsInstance(campaign, RemediationCampaign)
        self.assertIsInstance(blocked_stage, RemediationCampaignStage)
        self.assertEqual(campaign.status, RemediationCampaignStatus.BLOCKED)
        self.assertEqual(blocked_stage.status, RemediationCampaignStatus.BLOCKED)
        self.assertIn("pilot-containment", campaign.blocked_case_ids)

    def test_kki_remediation_campaign_governs_shadow_case(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-governed")
        governance_stage = next(
            stage
            for stage in campaign.stages
            if stage.case_id == "shadow-guarded" and stage.stage_type is RemediationCampaignStageType.GOVERNANCE_APPROVAL
        )

        self.assertEqual(governance_stage.status, RemediationCampaignStatus.GUARDED)
        self.assertTrue(governance_stage.governance_refs)
        self.assertIn("shadow-guarded", campaign.governance_case_ids)

    def test_kki_remediation_campaign_tracks_recovery_case(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-recovery")
        recovery_stage = next(
            stage
            for stage in campaign.stages
            if stage.case_id == "recovery-resume" and stage.stage_type is RemediationCampaignStageType.RECOVERY_SAFEGUARD
        )

        self.assertEqual(recovery_stage.status, RemediationCampaignStatus.RECOVERY_ONLY)
        self.assertTrue(recovery_stage.safeguard_refs)
        self.assertIn("recovery-resume", campaign.recovery_case_ids)

    def test_kki_remediation_campaign_aggregates_commitments(self) -> None:
        campaign = build_remediation_campaign(campaign_id="campaign-157-matrix")

        self.assertTrue(campaign.commitment_refs)
        self.assertGreaterEqual(len(campaign.evidence_records), len(campaign.stages))
        self.assertEqual(campaign.campaign_signal.status, "blocked")

    def test_kki_operations_cockpit_tracks_healthy_case(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-healthy")
        ready_entry = next(entry for entry in cockpit.entries if entry.case_id == "pilot-ready")

        self.assertIsInstance(cockpit, OperationsCockpit)
        self.assertIsInstance(ready_entry, CockpitEntry)
        self.assertEqual(ready_entry.status, CockpitStatus.HEALTHY)
        self.assertIn("pilot-ready", cockpit.healthy_case_ids)

    def test_kki_operations_cockpit_surfaces_governed_case(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-attention")
        guarded_entry = next(entry for entry in cockpit.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(guarded_entry.status, CockpitStatus.ATTENTION)
        self.assertEqual(guarded_entry.remediation_status, RemediationCampaignStatus.GUARDED.value)
        self.assertIn("shadow-guarded", cockpit.attention_case_ids)

    def test_kki_operations_cockpit_surfaces_critical_case(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-critical")
        blocked_entry = next(entry for entry in cockpit.entries if entry.case_id == "pilot-containment")

        self.assertEqual(blocked_entry.status, CockpitStatus.CRITICAL)
        self.assertTrue(blocked_entry.blocked_release)
        self.assertIn("pilot-containment", cockpit.critical_case_ids)

    def test_kki_operations_cockpit_aggregates_status_counts(self) -> None:
        cockpit = build_operations_cockpit(cockpit_id="cockpit-158-matrix")

        self.assertEqual(cockpit.cockpit_signal.status, "critical")
        self.assertIn("pilot-ready", cockpit.healthy_case_ids)
        self.assertIn("shadow-guarded", cockpit.attention_case_ids)
        self.assertIn("pilot-containment", cockpit.critical_case_ids)

    def test_kki_portfolio_optimizer_prioritizes_blocked_case(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-critical")
        blocked_recommendation = next(rec for rec in optimizer.recommendations if rec.case_id == "pilot-containment")

        self.assertIsInstance(optimizer, PortfolioOptimizer)
        self.assertIsInstance(blocked_recommendation, PortfolioRecommendation)
        self.assertEqual(blocked_recommendation.priority, PortfolioPriority.CRITICAL)
        self.assertEqual(blocked_recommendation.action, PortfolioAction.CONTAIN)
        self.assertIn("pilot-containment", optimizer.critical_case_ids)

    def test_kki_portfolio_optimizer_recommends_governance_approval(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-governed")
        governance_recommendation = next(rec for rec in optimizer.recommendations if rec.case_id == "shadow-guarded")

        self.assertEqual(governance_recommendation.priority, PortfolioPriority.HIGH)
        self.assertEqual(governance_recommendation.action, PortfolioAction.APPROVE)
        self.assertEqual(governance_recommendation.owner, ModuleBoundaryName.GOVERNANCE)

    def test_kki_portfolio_optimizer_recommends_release_candidate(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-release")
        ready_recommendation = next(rec for rec in optimizer.recommendations if rec.case_id == "pilot-ready")

        self.assertEqual(ready_recommendation.action, PortfolioAction.ADVANCE)
        self.assertTrue(ready_recommendation.release_candidate)
        self.assertIn("pilot-ready", optimizer.release_candidate_ids)

    def test_kki_portfolio_optimizer_aggregates_priority_queue(self) -> None:
        optimizer = build_portfolio_optimizer(optimizer_id="optimizer-159-matrix")

        self.assertEqual(optimizer.optimizer_signal.status, "critical-priorities")
        self.assertEqual(optimizer.recommendations[0].case_id, "pilot-containment")
        self.assertGreaterEqual(optimizer.recommendations[0].net_value, 0.0)

    def test_kki_continuous_readiness_marks_release_candidate_ready(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-ready")
        ready_iteration = next(iteration for iteration in cycle.iterations if iteration.case_id == "pilot-ready")

        self.assertIsInstance(cycle, ContinuousReadinessCycle)
        self.assertIsInstance(ready_iteration, ContinuousReadinessIteration)
        self.assertEqual(ready_iteration.status, ContinuousReadinessStatus.READY)
        self.assertTrue(ready_iteration.release_candidate)

    def test_kki_continuous_readiness_marks_governed_case_attention(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-governed")
        governed_iteration = next(iteration for iteration in cycle.iterations if iteration.case_id == "shadow-guarded")

        self.assertEqual(governed_iteration.status, ContinuousReadinessStatus.ATTENTION)
        self.assertEqual(governed_iteration.next_review_status, "review-required")
        self.assertIn("shadow-guarded", cycle.attention_case_ids)

    def test_kki_continuous_readiness_marks_blocked_case_not_ready(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-blocked")
        blocked_iteration = next(iteration for iteration in cycle.iterations if iteration.case_id == "pilot-containment")

        self.assertEqual(blocked_iteration.status, ContinuousReadinessStatus.BLOCKED)
        self.assertEqual(blocked_iteration.next_review_status, "not-ready")
        self.assertIn("pilot-containment", cycle.blocked_case_ids)

    def test_kki_continuous_readiness_aggregates_focus_cases(self) -> None:
        cycle = build_continuous_readiness_cycle(cycle_id="cycle-160-matrix")

        self.assertEqual(cycle.cycle_signal.status, "blocked")
        self.assertIn("pilot-ready", cycle.ready_case_ids)
        self.assertIn("shadow-guarded", cycle.next_focus_case_ids)
        self.assertIn("pilot-containment", cycle.blocked_case_ids)

    def test_kki_readiness_cadence_schedules_blocked_case_immediately(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-blocked")
        blocked_entry = next(entry for entry in cadence.entries if entry.case_id == "pilot-containment")

        self.assertIsInstance(cadence, ReadinessCadence)
        self.assertIsInstance(blocked_entry, ReadinessCadenceEntry)
        self.assertEqual(blocked_entry.trigger, ReadinessCadenceTrigger.CONTAINMENT)
        self.assertEqual(blocked_entry.window, ReadinessCadenceWindow.IMMEDIATE)
        self.assertEqual(blocked_entry.cadence_status, ReadinessCadenceStatus.ESCALATED)
        self.assertEqual(blocked_entry.due_cycle, 1)

    def test_kki_readiness_cadence_schedules_governed_case_in_current_window(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-governed")
        governed_entry = next(entry for entry in cadence.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(governed_entry.trigger, ReadinessCadenceTrigger.GOVERNANCE)
        self.assertEqual(governed_entry.window, ReadinessCadenceWindow.CURRENT)
        self.assertEqual(governed_entry.cadence_status, ReadinessCadenceStatus.REVIEW_REQUIRED)
        self.assertIn("shadow-guarded", cadence.current_window_case_ids)

    def test_kki_readiness_cadence_schedules_release_candidate_in_next_window(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-release")
        ready_entry = next(entry for entry in cadence.entries if entry.case_id == "pilot-ready")

        self.assertEqual(ready_entry.trigger, ReadinessCadenceTrigger.PROMOTION)
        self.assertEqual(ready_entry.window, ReadinessCadenceWindow.NEXT)
        self.assertEqual(ready_entry.cadence_status, ReadinessCadenceStatus.STEADY)
        self.assertTrue(ready_entry.release_candidate)
        self.assertIn("pilot-ready", cadence.next_window_case_ids)

    def test_kki_readiness_cadence_aggregates_focus_metrics(self) -> None:
        cadence = build_readiness_cadence(cadence_id="cadence-161-matrix")

        self.assertEqual(cadence.cadence_signal.status, "escalated")
        self.assertIn("pilot-containment", cadence.immediate_case_ids)
        self.assertIn("shadow-guarded", cadence.focus_case_ids)
        self.assertIn("pilot-ready", cadence.next_window_case_ids)

    def test_kki_escalation_router_routes_blocked_case_to_recovery(self) -> None:
        router = build_escalation_router(router_id="router-162-blocked")
        blocked_route = next(route for route in router.routes if route.case_id == "pilot-containment")

        self.assertIsInstance(router, EscalationRouter)
        self.assertIsInstance(blocked_route, EscalationRoute)
        self.assertEqual(blocked_route.path, EscalationRoutePath.RECOVERY_CONTAINMENT)
        self.assertEqual(blocked_route.boundary, ModuleBoundaryName.RECOVERY)
        self.assertTrue(blocked_route.release_blocked)
        self.assertIn("pilot-containment", router.recovery_case_ids)

    def test_kki_escalation_router_routes_governed_case_to_governance(self) -> None:
        router = build_escalation_router(router_id="router-162-governed")
        governed_route = next(route for route in router.routes if route.case_id == "shadow-guarded")

        self.assertEqual(governed_route.path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertEqual(governed_route.boundary, ModuleBoundaryName.GOVERNANCE)
        self.assertIn("shadow-guarded", router.governance_case_ids)

    def test_kki_escalation_router_routes_steady_case_to_telemetry(self) -> None:
        router = build_escalation_router(router_id="router-162-steady")
        steady_route = next(route for route in router.routes if route.case_id == "pilot-ready")

        self.assertEqual(steady_route.path, EscalationRoutePath.TELEMETRY_WATCH)
        self.assertEqual(steady_route.boundary, ModuleBoundaryName.TELEMETRY)
        self.assertFalse(steady_route.release_blocked)
        self.assertIn("pilot-ready", router.telemetry_case_ids)

    def test_kki_escalation_router_aggregates_focus_routes(self) -> None:
        router = build_escalation_router(router_id="router-162-matrix")

        self.assertEqual(router.router_signal.status, "critical-response")
        self.assertIn("pilot-containment", router.blocked_case_ids)
        self.assertIn("shadow-guarded", router.focus_case_ids)
        self.assertIn("pilot-ready", router.telemetry_case_ids)

    def test_kki_evidence_ledger_collects_review_evidence(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-review")
        review_entry = next(
            entry
            for entry in ledger.entries
            if entry.case_id == "shadow-guarded" and entry.source is EvidenceLedgerSource.REVIEW
        )

        self.assertIsInstance(ledger, EvidenceLedger)
        self.assertIsInstance(review_entry, EvidenceLedgerEntry)
        self.assertEqual(review_entry.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertEqual(review_entry.boundary, ModuleBoundaryName.GOVERNANCE)
        self.assertEqual(review_entry.evidence_record.evidence_type, "readiness-review-finding")

    def test_kki_evidence_ledger_collects_replay_evidence(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-replay")
        replay_entry = next(
            entry
            for entry in ledger.entries
            if entry.case_id == "pilot-containment" and entry.source is EvidenceLedgerSource.REPLAY
        )

        self.assertEqual(replay_entry.route_path, EscalationRoutePath.RECOVERY_CONTAINMENT)
        self.assertEqual(replay_entry.evidence_record.evidence_type, "scenario-replay-result")
        self.assertEqual(replay_entry.cycle_index, 1)

    def test_kki_evidence_ledger_collects_remediation_commitments(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-remediation")
        remediation_entry = next(
            entry
            for entry in ledger.entries
            if entry.case_id == "pilot-containment" and entry.source is EvidenceLedgerSource.REMEDIATION
        )

        self.assertTrue(remediation_entry.commitment_refs)
        self.assertTrue(remediation_entry.evidence_record.commitment_ref)
        self.assertIn(remediation_entry.commitment_refs[0], ledger.commitment_refs)

    def test_kki_evidence_ledger_aggregates_case_tracks(self) -> None:
        ledger = build_evidence_ledger(ledger_id="ledger-163-matrix")

        self.assertEqual(ledger.ledger_signal.status, "blocked-evidence")
        self.assertIn("pilot-containment", ledger.blocked_case_ids)
        self.assertIn("shadow-guarded", ledger.governance_case_ids)
        self.assertIn("pilot-containment", ledger.recovery_case_ids)

    def test_kki_capacity_planner_admits_blocked_case_immediately(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-blocked")
        blocked_entry = next(entry for entry in planner.entries if entry.case_id == "pilot-containment")

        self.assertIsInstance(planner, CapacityPlanner)
        self.assertIsInstance(blocked_entry, CapacityPlanEntry)
        self.assertEqual(blocked_entry.window, CapacityWindow.IMMEDIATE)
        self.assertEqual(blocked_entry.lane, CapacityLane.ADMIT)
        self.assertEqual(blocked_entry.wip_slot, 1)

    def test_kki_capacity_planner_admits_governance_case_current_window(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-governance")
        governed_entry = next(entry for entry in planner.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(governed_entry.window, CapacityWindow.CURRENT)
        self.assertEqual(governed_entry.lane, CapacityLane.ADMIT)
        self.assertIn("shadow-guarded", planner.current_window_case_ids)

    def test_kki_capacity_planner_defers_release_candidate_to_next_window(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-release")
        ready_entry = next(entry for entry in planner.entries if entry.case_id == "pilot-ready")

        self.assertEqual(ready_entry.window, CapacityWindow.NEXT)
        self.assertEqual(ready_entry.lane, CapacityLane.DEFER)
        self.assertTrue(ready_entry.release_candidate)
        self.assertIn("pilot-ready", planner.deferred_case_ids)

    def test_kki_capacity_planner_aggregates_budget_and_wip(self) -> None:
        planner = build_capacity_planner(planner_id="planner-164-matrix")

        self.assertEqual(planner.planner_signal.status, "immediate-capacity")
        self.assertEqual(planner.admitted_case_ids[:2], ("pilot-containment", "shadow-guarded"))
        self.assertLessEqual(planner.consumed_budget, planner.total_budget)
        self.assertIn("pilot-containment", planner.immediate_case_ids)

    def test_kki_governance_agenda_schedules_governance_case(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-governed")
        governed_item = next(item for item in agenda.items if item.case_id == "shadow-guarded")

        self.assertIsInstance(agenda, GovernanceAgenda)
        self.assertIsInstance(governed_item, GovernanceAgendaItem)
        self.assertEqual(governed_item.agenda_status, GovernanceAgendaStatus.SCHEDULED)
        self.assertEqual(governed_item.decision, HumanDecision.APPROVE)
        self.assertIn("shadow-guarded", agenda.scheduled_case_ids)

    def test_kki_governance_agenda_tracks_governance_evidence(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-evidence")
        governed_item = next(item for item in agenda.items if item.case_id == "shadow-guarded")

        self.assertTrue(governed_item.evidence_refs)
        self.assertEqual(governed_item.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)

    def test_kki_governance_agenda_excludes_non_governance_cases(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-scope")

        self.assertNotIn("pilot-containment", [item.case_id for item in agenda.items])
        self.assertNotIn("pilot-ready", [item.case_id for item in agenda.items])

    def test_kki_governance_agenda_aggregates_queue_state(self) -> None:
        agenda = build_governance_agenda(agenda_id="agenda-165-matrix")

        self.assertEqual(agenda.agenda_signal.status, "scheduled")
        self.assertEqual(agenda.scheduled_case_ids, ("shadow-guarded",))
        self.assertFalse(agenda.blocked_case_ids)

    def test_kki_recovery_drills_schedule_blocked_case(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-blocked")
        blocked_drill = next(drill for drill in drills.drills if drill.case_id == "pilot-containment")

        self.assertIsInstance(drills, RecoveryDrillSuite)
        self.assertIsInstance(blocked_drill, RecoveryDrill)
        self.assertEqual(blocked_drill.mode, RecoveryMode.ROLLBACK)
        self.assertEqual(blocked_drill.disposition, RecoveryDisposition.CONTAIN)

    def test_kki_recovery_drills_mark_active_blocked_case(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-active")
        blocked_drill = next(drill for drill in drills.drills if drill.case_id == "pilot-containment")

        self.assertEqual(blocked_drill.status, RecoveryDrillStatus.ACTIVE)
        self.assertIn("pilot-containment", drills.active_case_ids)

    def test_kki_recovery_drills_capture_reentry_conditions(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-conditions")
        blocked_drill = next(drill for drill in drills.drills if drill.case_id == "pilot-containment")

        self.assertIn("replay-evidence-updated", blocked_drill.reentry_conditions)
        self.assertIn("remediation-commitments-complete", blocked_drill.reentry_conditions)
        self.assertIn("readiness-review-revalidated", blocked_drill.reentry_conditions)

    def test_kki_recovery_drills_aggregate_suite_status(self) -> None:
        drills = build_recovery_drill_suite(suite_id="drills-166-matrix")

        self.assertEqual(drills.drill_signal.status, "active")
        self.assertEqual(drills.active_case_ids, ("pilot-containment",))
        self.assertFalse(drills.reentry_ready_case_ids)

    def test_kki_convergence_simulator_projects_three_cycles(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-cycles")

        self.assertIsInstance(simulator, ConvergenceSimulator)
        self.assertEqual(len(simulator.projections), 3)
        self.assertTrue(all(isinstance(projection, ConvergenceProjection) for projection in simulator.projections))
        self.assertEqual(
            tuple(projection.status for projection in simulator.projections),
            (
                ConvergenceStatus.RESIDUAL_DRIFT,
                ConvergenceStatus.STABILIZING,
                ConvergenceStatus.CONVERGED,
            ),
        )

    def test_kki_convergence_simulator_reduces_residual_drift(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-drift")
        drifts = tuple(projection.residual_drift for projection in simulator.projections)

        self.assertGreater(drifts[0], drifts[1])
        self.assertGreater(drifts[1], drifts[2])
        self.assertEqual(drifts[-1], 0.0)

    def test_kki_convergence_simulator_recovers_cases_by_final_cycle(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-ready")

        self.assertEqual(simulator.projections[0].blocked_case_ids, ("pilot-containment",))
        self.assertEqual(
            simulator.final_ready_case_ids,
            ("pilot-containment", "shadow-guarded", "recovery-resume", "pilot-ready"),
        )
        self.assertFalse(simulator.residual_case_ids)

    def test_kki_convergence_simulator_aggregates_converged_signal(self) -> None:
        simulator = build_convergence_simulator(simulator_id="convergence-167-signal")

        self.assertEqual(simulator.simulator_signal.status, "converged")
        self.assertEqual(simulator.converged_cycle_index, 3)
        self.assertEqual(simulator.projections[-1].recovery_case_ids, ("pilot-containment",))

    def test_kki_policy_tuner_tightens_recovery_paths(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-recovery")
        containment_entry = next(entry for entry in tuner.entries if entry.case_id == "pilot-containment")
        restart_entry = next(entry for entry in tuner.entries if entry.case_id == "recovery-resume")

        self.assertIsInstance(tuner, PolicyTuner)
        self.assertIsInstance(containment_entry, PolicyTuneEntry)
        self.assertEqual(containment_entry.action, PolicyTuneAction.TIGHTEN)
        self.assertEqual(containment_entry.tuned_policy_mode, GuardrailPolicyMode.CONTAIN)
        self.assertEqual(restart_entry.tuned_policy_mode, GuardrailPolicyMode.HOLD)

    def test_kki_policy_tuner_calibrates_governance_policy(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-governance")
        governed_entry = next(entry for entry in tuner.entries if entry.case_id == "shadow-guarded")

        self.assertEqual(governed_entry.action, PolicyTuneAction.CALIBRATE)
        self.assertEqual(governed_entry.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertGreater(governed_entry.tuned_threshold, governed_entry.current_threshold)

    def test_kki_policy_tuner_relaxes_stable_telemetry_case(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-telemetry")
        telemetry_entry = next(entry for entry in tuner.entries if entry.case_id == "pilot-ready")

        self.assertEqual(telemetry_entry.action, PolicyTuneAction.RELAX)
        self.assertEqual(telemetry_entry.tuned_policy_mode, GuardrailPolicyMode.MONITOR)
        self.assertLess(telemetry_entry.tuned_threshold, telemetry_entry.current_threshold)

    def test_kki_policy_tuner_aggregates_adjustment_signal(self) -> None:
        tuner = build_policy_tuner(tuner_id="policy-168-signal")

        self.assertEqual(tuner.tuner_signal.status, "policy-tightening")
        self.assertEqual(tuner.tightened_case_ids, ("recovery-resume", "pilot-containment"))
        self.assertEqual(tuner.calibrated_case_ids, ("shadow-guarded",))
        self.assertEqual(tuner.relaxed_case_ids, ("pilot-ready",))

    def test_kki_learning_register_captures_interventions(self) -> None:
        register = build_learning_register(register_id="learning-169-interventions")
        intervention = next(record for record in register.records if record.case_id == "pilot-containment")

        self.assertIsInstance(register, LearningRegister)
        self.assertIsInstance(intervention, LearningRecord)
        self.assertEqual(intervention.pattern_type, LearningPatternType.STABILIZED_INTERVENTION)
        self.assertEqual(intervention.source_action, PolicyTuneAction.TIGHTEN)
        self.assertTrue(intervention.evidence_refs)
        self.assertTrue(intervention.commitment_refs)

    def test_kki_learning_register_captures_operating_recipe(self) -> None:
        register = build_learning_register(register_id="learning-169-recipe")
        recipe = next(record for record in register.records if record.case_id == "shadow-guarded")

        self.assertEqual(recipe.pattern_type, LearningPatternType.OPERATING_RECIPE)
        self.assertEqual(recipe.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertTrue(recipe.reusable)

    def test_kki_learning_register_captures_recurring_pattern(self) -> None:
        register = build_learning_register(register_id="learning-169-pattern")
        pattern = next(record for record in register.records if record.case_id == "pilot-ready")

        self.assertEqual(pattern.pattern_type, LearningPatternType.RECURRING_PATTERN)
        self.assertEqual(pattern.source_action, PolicyTuneAction.RELAX)
        self.assertGreater(pattern.confidence_score, 0.7)

    def test_kki_learning_register_aggregates_reusable_knowledge(self) -> None:
        register = build_learning_register(register_id="learning-169-signal")

        self.assertEqual(register.register_signal.status, "reusable-learning")
        self.assertEqual(register.intervention_case_ids, ("recovery-resume", "pilot-containment"))
        self.assertEqual(register.recipe_case_ids, ("shadow-guarded",))
        self.assertEqual(register.recurring_pattern_case_ids, ("pilot-ready",))
        self.assertEqual(register.reusable_case_ids, ("shadow-guarded", "recovery-resume", "pilot-containment", "pilot-ready"))

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
