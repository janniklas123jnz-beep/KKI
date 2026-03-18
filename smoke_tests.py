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
    ArchiveEntry,
    ArchiveRetention,
    ArchiveStatus,
    ArtifactKind,
    ArtifactScope,
    AutonomyAssignment,
    AutonomyDecision,
    AutonomyGovernor,
    AuthorizationIdentity,
    AuditTrailEntry,
    BenchmarkCase,
    BenchmarkHarness,
    BenchmarkReleaseMode,
    CabinetExecutionMode,
    CabinetOrder,
    CabinetRole,
    CabinetStatus,
    DelegationEntry,
    DelegationLane,
    DelegationMatrix,
    DelegationMode,
    DelegationStatus,
    RecallPath,
    ReleasePath,
    SluiceStatus,
    VetoChannel,
    VetoSluice,
    VetoStop,
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
    CourseCorrector,
    CourseCorrectionAction,
    CourseCorrectionDirective,
    CourseCorrectionStatus,
    ConsensusDirective,
    ConsensusDirectiveStatus,
    ConsensusDirectiveType,
    ConsensusMandate,
    ConsensusDiplomacy,
    CollegiumLane,
    CollegiumMandate,
    CollegiumSeat,
    CollegiumStatus,
    ConclaveLane,
    ConclaveMotion,
    ConclavePriority,
    ConclaveStatus,
    ContractClause,
    ContractCommitment,
    ContractParty,
    ContractStatus,
    CodexAxis,
    CodexCanon,
    CodexSection,
    CodexStatus,
    KodexRegister,
    KodexRegisterEntry,
    RatBench,
    RatInterpretation,
    RatStatus,
    SatzungsRat,
    SatzungsRatArticle,
    KonventEbene,
    KonventMandat,
    KonventStatus,
    MandatsKonvent,
    MandatsLinie,
    NormenTribunal,
    TribunalFall,
    TribunalKammer,
    TribunalUrteil,
    TribunalVerfahren,
    build_normen_tribunal,
    SenatsBeschluss,
    SenatsFraktion,
    SenatsSitzung,
    SenatsMandat,
    VerfassungsSenat,
    build_verfassungs_senat,
    ChartaArtikel,
    ChartaGeltung,
    ChartaKapitel,
    ChartaVerfahren,
    GrundrechtsCharta,
    build_grundrechts_charta,
    AktKlausel,
    AktProzedur,
    AktSektion,
    AktStatus,
    SouveraenitaetsAkt,
    build_souveraenitaets_akt,
    ManifestAbschnitt,
    ManifestGeltung,
    ManifestKapitel,
    ManifestVerfahren,
    OrdnungsManifest,
    build_ordnungs_manifest,
    Leitordnung,
    OrdnungsKraft,
    OrdnungsNorm,
    OrdnungsRang,
    OrdnungsTyp,
    build_leitordnung,
    AutoritaetsDekret,
    DekretGeltung,
    DekretKlausel,
    DekretProzedur,
    DekretSektion,
    build_autoritaets_dekret,
    FundamentKraft,
    FundamentPfeiler,
    FundamentSaeule,
    FundamentVerfahren,
    RechtsFundament,
    build_rechts_fundament,
    GrundsatzRegister,
    RegisterEintrag,
    RegisterKategorie,
    RegisterProzedur,
    RegisterStatus,
    build_grundsatz_register,
    PrinzipienKlasse,
    PrinzipienKodex,
    PrinzipienProzedur,
    PrinzipienSatz,
    PrinzipienStatus,
    build_prinzipien_kodex,
    WerteArtikel,
    WerteCharta,
    WerteProzedur,
    WerteStatus,
    WerteTyp,
    build_werte_charta,
    KonventBeschluss,
    KonventProzedur,
    LeitbildAusrichtung,
    LeitbildKonvent,
    LeitbildResolution,
    build_leitbild_konvent,
    MissionsArtikel,
    MissionsRang,
    MissionsVerfassung,
    VerfassungsProzedur,
    VerfassungsStatus,
    build_missions_verfassung,
    ManifestGeltung,
    ManifestProzedur,
    ZweckDimension,
    ZweckKlausel,
    ZweckManifest,
    build_zweck_manifest,
    KonstitutionsArtikel,
    KonstitutionsEbene,
    KonstitutionsProzedur,
    KonstitutionsRang,
    LeitsternKonstitution,
    build_leitstern_konstitution,
    GrundgesetzGeltung,
    GrundgesetzParagraph,
    GrundgesetzProzedur,
    GrundgesetzTitel,
    VerfassungsGrundgesetz,
    build_verfassungs_grundgesetz,
    StaatsEbene,
    StaatsGeltung,
    StaatsNorm,
    StaatsOrdnung,
    StaatsProzedur,
    build_staats_ordnung,
    KodexKlasse,
    KodexNorm,
    KodexProzedur,
    KodexStatus,
    RechtsKodex,
    build_rechts_kodex,
    UnionsAkt,
    UnionsGeltung,
    UnionsNorm,
    UnionsProzedur,
    UnionsTyp,
    build_unions_akt,
    FoederalGeltung,
    FoederalNorm,
    FoederalProzedur,
    FoederalTyp,
    FoederalVertrag,
    build_foederal_vertrag,
    BundesCharta,
    BundesGeltung,
    BundesNorm,
    BundesProzedur,
    BundesRang,
    build_bundes_charta,
    HoheitsGeltung,
    HoheitsGrad,
    HoheitsManifest,
    HoheitsNorm,
    HoheitsProzedur,
    build_hoheits_manifest,
    SuprematsGeltung,
    SuprematsKlasse,
    SuprematsNorm,
    SuprematsProzedur,
    SuprematsRegister,
    build_supremats_register,
    EwigkeitsEintrag,
    EwigkeitsGeltung,
    EwigkeitsNorm,
    EwigkeitsProzedur,
    EwigkeitsTyp,
    build_ewigkeits_norm,
    DoctrineClause,
    DoctrinePrinciple,
    DoctrineScope,
    DoctrineStatus,
    CompassStatus,
    CharterStatus,
    DiplomacyChannel,
    DiplomacyPath,
    DiplomacyPosture,
    DiplomacyStatus,
    ExecutionCabinet,
    LeitsternDoctrine,
    LeitsternCodex,
    MissionsCollegium,
    PriorityConclave,
    RegisterRetention,
    RegisterTier,
    CourseContract,
    VetoSluice,
    DecisionArchive,
    DelegationMatrix,
    DirectiveConsensus,
    GuidelineCompass,
    GuidelinePrinciple,
    GuidelineVector,
    InterventionCharter,
    InterventionClause,
    InterventionRight,
    MandateMemoryRecord,
    MandateMemoryStatus,
    MandateMemoryStore,
    NavigationConstraint,
    ProgramSenate,
    ReleaseThreshold,
    SenateBalanceStatus,
    SenatePriority,
    SenateResolution,
    SenateSeat,
    StopCondition,
    CockpitEntry,
    CockpitStatus,
    ConstitutionArticle,
    ConstitutionPrinciple,
    ConstitutionalAuthority,
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
    ExecutiveOrder,
    ExecutiveOrderMode,
    ExecutiveWatchStatus,
    ExecutiveWatchtower,
    ExceptionCase,
    ExceptionKind,
    ExceptionRegister,
    ExceptionSeverity,
    FederationAlignmentStatus,
    FederationCell,
    FederationCoordination,
    FederationDomain,
    FederationHandoff,
    FederationHandoffPriority,
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
    InterventionFallback,
    InterventionMode,
    InterventionSimulation,
    InterventionSimulationStatus,
    InterventionSimulator,
    LearningPatternType,
    LearningRecord,
    LearningRegister,
    LoadedControlPlane,
    MissionPolicy,
    MissionProfile,
    MissionScenario,
    MandateCard,
    MandateCardDeck,
    MandateExecutionScope,
    MandateReviewCadence,
    MessageEnvelope,
    MessageKind,
    ModuleBoundaryName,
    OperationalPressure,
    OperationsRunLedger,
    OperationsCockpit,
    OperationsSteward,
    OperationsStewardStatus,
    OutcomeLedger,
    OutcomeRecord,
    OutcomeStatus,
    OperatingConstitution,
    OperationsWave,
    OperatingMode,
    OperationsIncident,
    OrchestrationStatus,
    PlaybookCatalog,
    PlaybookEntry,
    PlaybookReadiness,
    PlaybookType,
    PortfolioAction,
    PortfolioConcentration,
    PortfolioExposure,
    PortfolioOperatingSpread,
    PortfolioOptimizer,
    PortfolioPriority,
    PortfolioRadar,
    PortfolioRadarEntry,
    PortfolioRecommendation,
    PolicyTuneAction,
    PolicyTuneEntry,
    PolicyTuner,
    ProgramController,
    ProgramControllerStatus,
    ProgramDirective,
    ProgramTrack,
    ProgramTrackType,
    PersistenceRecord,
    PreviewMode,
    ShadowCoordination,
    ShadowCoordinationMode,
    StewardDirective,
    StewardDirectiveType,
    StewardWorkboard,
    StrategyCouncil,
    StrategyCouncilStatus,
    StrategyEscalationMandate,
    StrategyLane,
    StrategyMandate,
    StrategyPriority,
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
    ScenarioChancery,
    ScenarioOfficeMode,
    ScenarioOfficeStatus,
    ScenarioOption,
    ShadowPreview,
    TelemetryAlert,
    TelemetrySignal,
    TelemetrySnapshot,
    TransferEnvelope,
    TrustLevel,
    ValidationStep,
    WaveBudgetPolicy,
    WorkboardItem,
    WorkboardLane,
    WorkboardQueue,
    WorkboardStatus,
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
    build_autonomy_governor,
    build_capacity_planner,
    build_continuous_readiness_cycle,
    build_convergence_simulator,
    build_course_corrector,
    build_decision_archive,
    build_delegation_matrix,
    build_execution_cabinet,
    build_consensus_diplomacy,
    build_leitstern_doctrine,
    build_missions_collegium,
    build_priority_conclave,
    build_course_contract,
    build_leitstern_codex,
    build_kodex_register,
    build_satzungs_rat,
    build_mandats_konvent,
    build_veto_sluice,
    build_directive_consensus,
    build_dispatch_plan,
    build_drift_monitor,
    build_escalation_router,
    build_evidence_ledger,
    build_executive_watchtower,
    build_exception_register,
    build_federation_coordination,
    build_guideline_compass,
    build_governance_agenda,
    build_guardrail_portfolio,
    build_improvement_orchestrator,
    build_intervention_charter,
    build_intervention_simulator,
    build_learning_register,
    build_mandate_card_deck,
    build_mandate_memory_store,
    build_operations_cockpit,
    build_operations_steward,
    build_operating_constitution,
    build_outcome_ledger,
    build_playbook_catalog,
    build_portfolio_optimizer,
    build_portfolio_radar,
    build_policy_tuner,
    build_program_controller,
    build_program_senate,
    build_readiness_cadence,
    build_remediation_campaign,
    build_readiness_review,
    build_recovery_drill_suite,
    build_release_campaign,
    build_review_action_plan,
    build_risk_register,
    build_scenario_replay,
    build_scenario_chancery,
    build_runtime_scorecard,
    build_steward_workboard,
    build_strategy_council,
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

    def test_kki_operations_steward_stabilizes_blocked_case(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-stabilize")
        directive = next(item for item in steward.directives if item.case_id == "pilot-containment")

        self.assertIsInstance(steward, OperationsSteward)
        self.assertIsInstance(directive, StewardDirective)
        self.assertEqual(directive.directive_type, StewardDirectiveType.STABILIZE)
        self.assertEqual(directive.policy_action, PolicyTuneAction.TIGHTEN)
        self.assertEqual(directive.learning_pattern, LearningPatternType.STABILIZED_INTERVENTION)

    def test_kki_operations_steward_governs_review_case(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-govern")
        directive = next(item for item in steward.directives if item.case_id == "shadow-guarded")

        self.assertEqual(directive.directive_type, StewardDirectiveType.GOVERN)
        self.assertEqual(directive.route_path, EscalationRoutePath.GOVERNANCE_REVIEW)
        self.assertTrue(directive.evidence_refs)

    def test_kki_operations_steward_adapts_remaining_cases(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-adapt")

        self.assertEqual(steward.adapt_case_ids, ("recovery-resume",))
        self.assertEqual(steward.monitor_case_ids, ("pilot-ready",))
        self.assertEqual(steward.govern_case_ids, ("shadow-guarded",))

    def test_kki_operations_steward_aggregates_control_signal(self) -> None:
        steward = build_operations_steward(steward_id="steward-170-signal")

        self.assertEqual(steward.steward_signal.status, OperationsStewardStatus.CRITICAL.value)
        self.assertEqual(steward.stabilize_case_ids, ("pilot-containment",))
        self.assertAlmostEqual(steward.steward_signal.metrics["directive_count"], 4.0)

    def test_kki_steward_workboard_expedites_blocked_case(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-expedite")
        item = next(item for item in workboard.items if item.case_id == "pilot-containment")

        self.assertIsInstance(workboard, StewardWorkboard)
        self.assertIsInstance(item, WorkboardItem)
        self.assertEqual(item.queue, WorkboardQueue.STABILIZATION)
        self.assertEqual(item.lane, WorkboardLane.EXPEDITE)
        self.assertEqual(item.status, WorkboardStatus.DUE_NOW)

    def test_kki_steward_workboard_tracks_governance_case(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-governance")
        item = next(item for item in workboard.items if item.case_id == "shadow-guarded")

        self.assertEqual(item.queue, WorkboardQueue.GOVERNANCE)
        self.assertEqual(item.lane, WorkboardLane.COMMITTED)
        self.assertEqual(item.sla_hours, 12)

    def test_kki_steward_workboard_places_follow_up_and_watch_items(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-lanes")

        self.assertEqual(workboard.follow_up_case_ids, ("recovery-resume",))
        self.assertEqual(workboard.watch_case_ids, ("pilot-ready",))
        self.assertEqual(workboard.committed_case_ids, ("shadow-guarded",))

    def test_kki_steward_workboard_aggregates_board_signal(self) -> None:
        workboard = build_steward_workboard(workboard_id="workboard-171-signal")

        self.assertEqual(workboard.board_signal.status, "expedite-board")
        self.assertEqual(workboard.expedite_case_ids, ("pilot-containment",))
        self.assertEqual(workboard.due_now_case_ids, ("pilot-containment",))
        self.assertAlmostEqual(workboard.board_signal.metrics["item_count"], 4.0)

    def test_kki_outcome_ledger_tracks_contained_case(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-contained")
        record = next(item for item in ledger.records if item.case_id == "pilot-containment")

        self.assertIsInstance(ledger, OutcomeLedger)
        self.assertIsInstance(record, OutcomeRecord)
        self.assertEqual(record.outcome_status, OutcomeStatus.CONTAINED)
        self.assertTrue(record.resolved_within_sla)
        self.assertTrue(record.exception_candidate)

    def test_kki_outcome_ledger_tracks_governed_case(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-governed")
        record = next(item for item in ledger.records if item.case_id == "shadow-guarded")

        self.assertEqual(record.outcome_status, OutcomeStatus.GOVERNED)
        self.assertTrue(record.outcome_ref.startswith("outcome-"))
        self.assertTrue(record.evidence_refs)

    def test_kki_outcome_ledger_tracks_tuned_and_observed_cases(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-mix")

        self.assertEqual(ledger.tuned_case_ids, ("recovery-resume",))
        self.assertEqual(ledger.observed_case_ids, ("pilot-ready",))
        self.assertEqual(ledger.exception_candidate_case_ids, ("pilot-containment", "recovery-resume"))

    def test_kki_outcome_ledger_aggregates_execution_signal(self) -> None:
        ledger = build_outcome_ledger(ledger_id="outcome-172-signal")

        self.assertEqual(ledger.ledger_signal.status, "stabilizing-outcomes")
        self.assertEqual(ledger.contained_case_ids, ("pilot-containment",))
        self.assertEqual(ledger.governed_case_ids, ("shadow-guarded",))
        self.assertAlmostEqual(ledger.ledger_signal.metrics["record_count"], 4.0)

    def test_kki_exception_register_tracks_policy_breach_case(self) -> None:
        register = build_exception_register(register_id="exception-173-breach")
        case = next(item for item in register.exceptions if item.case_id == "pilot-containment")

        self.assertIsInstance(register, ExceptionRegister)
        self.assertIsInstance(case, ExceptionCase)
        self.assertEqual(case.kind, ExceptionKind.POLICY_BREACH)
        self.assertEqual(case.severity, ExceptionSeverity.CRITICAL)

    def test_kki_exception_register_tracks_unresolved_case(self) -> None:
        register = build_exception_register(register_id="exception-173-unresolved")
        case = next(item for item in register.exceptions if item.case_id == "recovery-resume")

        self.assertEqual(case.kind, ExceptionKind.UNRESOLVED)
        self.assertEqual(case.severity, ExceptionSeverity.HIGH)
        self.assertIn("unresolved", case.escalation_reason)

    def test_kki_exception_register_excludes_routine_cases(self) -> None:
        register = build_exception_register(register_id="exception-173-scope")

        self.assertNotIn("shadow-guarded", [item.case_id for item in register.exceptions])
        self.assertNotIn("pilot-ready", [item.case_id for item in register.exceptions])

    def test_kki_exception_register_aggregates_exception_signal(self) -> None:
        register = build_exception_register(register_id="exception-173-signal")

        self.assertEqual(register.register_signal.status, "critical-exceptions")
        self.assertEqual(register.critical_case_ids, ("pilot-containment",))
        self.assertEqual(register.unresolved_case_ids, ("recovery-resume",))
        self.assertEqual(register.policy_breach_case_ids, ("pilot-containment",))

    def test_kki_playbook_catalog_compiles_steward_guided_playbooks(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-guided")
        playbook = next(item for item in catalog.playbooks if item.case_id == "pilot-containment")

        self.assertIsInstance(catalog, PlaybookCatalog)
        self.assertIsInstance(playbook, PlaybookEntry)
        self.assertEqual(playbook.playbook_type, PlaybookType.STABILIZATION)
        self.assertEqual(playbook.readiness, PlaybookReadiness.STEWARD_GUIDED)

    def test_kki_playbook_catalog_compiles_governed_standard_playbooks(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-governed")
        playbook = next(item for item in catalog.playbooks if item.case_id == "shadow-guarded")

        self.assertEqual(playbook.playbook_type, PlaybookType.GOVERNANCE)
        self.assertEqual(playbook.readiness, PlaybookReadiness.GOVERNED_STANDARD)
        self.assertFalse(playbook.automation_candidate)

    def test_kki_playbook_catalog_marks_autonomy_candidates(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-autonomy")
        playbook = next(item for item in catalog.playbooks if item.case_id == "pilot-ready")

        self.assertEqual(playbook.playbook_type, PlaybookType.MONITORING)
        self.assertEqual(playbook.readiness, PlaybookReadiness.AUTONOMY_CANDIDATE)
        self.assertIn("Eligible for controlled autonomous execution.", playbook.steps)

    def test_kki_playbook_catalog_aggregates_catalog_signal(self) -> None:
        catalog = build_playbook_catalog(catalog_id="playbook-174-signal")

        self.assertEqual(catalog.catalog_signal.status, "catalog-autonomy-ready")
        self.assertEqual(catalog.steward_guided_case_ids, ("pilot-containment", "recovery-resume"))
        self.assertEqual(catalog.governed_case_ids, ("shadow-guarded",))
        self.assertEqual(catalog.autonomy_candidate_case_ids, ("pilot-ready",))

    def test_kki_autonomy_governor_enables_bounded_autonomy(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-auto")
        assignment = next(item for item in governor.assignments if item.case_id == "pilot-ready")

        self.assertIsInstance(governor, AutonomyGovernor)
        self.assertIsInstance(assignment, AutonomyAssignment)
        self.assertEqual(assignment.decision, AutonomyDecision.AUTONOMOUS)
        self.assertTrue(assignment.automation_allowed)

    def test_kki_autonomy_governor_requires_governance_for_standard_case(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-governance")
        assignment = next(item for item in governor.assignments if item.case_id == "shadow-guarded")

        self.assertEqual(assignment.decision, AutonomyDecision.GOVERNANCE_REQUIRED)
        self.assertTrue(assignment.governance_required)
        self.assertIn("approval-gate", assignment.control_tags)

    def test_kki_autonomy_governor_keeps_exception_cases_with_steward(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-steward")

        self.assertEqual(governor.steward_required_case_ids, ("pilot-containment", "recovery-resume"))
        self.assertIn("exception-escalation", next(item for item in governor.assignments if item.case_id == "pilot-containment").control_tags)

    def test_kki_autonomy_governor_aggregates_governor_signal(self) -> None:
        governor = build_autonomy_governor(governor_id="autonomy-175-signal")

        self.assertEqual(governor.governor_signal.status, "autonomy-enabled")
        self.assertEqual(governor.autonomous_case_ids, ("pilot-ready",))
        self.assertEqual(governor.governance_required_case_ids, ("shadow-guarded",))
        self.assertAlmostEqual(governor.governor_signal.metrics["assignment_count"], 4.0)

    def test_kki_intervention_simulator_projects_ready_autonomous_case(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-ready")
        simulation = next(item for item in simulator.simulations if item.case_id == "pilot-ready")

        self.assertIsInstance(simulator, InterventionSimulator)
        self.assertIsInstance(simulation, InterventionSimulation)
        self.assertEqual(simulation.intervention_mode, InterventionMode.AUTONOMOUS)
        self.assertEqual(simulation.projected_status, InterventionSimulationStatus.READY)
        self.assertEqual(simulation.fallback_path, InterventionFallback.OBSERVE_ONLY)

    def test_kki_intervention_simulator_projects_guarded_governance_case(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-guarded")
        simulation = next(item for item in simulator.simulations if item.case_id == "shadow-guarded")

        self.assertEqual(simulation.intervention_mode, InterventionMode.GOVERNED)
        self.assertEqual(simulation.projected_status, InterventionSimulationStatus.GUARDED)
        self.assertEqual(simulation.fallback_path, InterventionFallback.APPROVAL_GATE)

    def test_kki_intervention_simulator_flags_risk_and_rollback_cases(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-risk")

        rollback_case = next(item for item in simulator.simulations if item.case_id == "pilot-containment")
        at_risk_case = next(item for item in simulator.simulations if item.case_id == "recovery-resume")
        self.assertEqual(rollback_case.projected_status, InterventionSimulationStatus.ROLLBACK_RECOMMENDED)
        self.assertEqual(rollback_case.fallback_path, InterventionFallback.ROLLBACK)
        self.assertEqual(at_risk_case.projected_status, InterventionSimulationStatus.AT_RISK)
        self.assertTrue(at_risk_case.regression_risk)

    def test_kki_intervention_simulator_aggregates_simulation_signal(self) -> None:
        simulator = build_intervention_simulator(simulator_id="intervention-176-signal")

        self.assertEqual(simulator.simulator_signal.status, "rollback-recommended")
        self.assertEqual(simulator.ready_case_ids, ("pilot-ready",))
        self.assertEqual(simulator.guarded_case_ids, ("shadow-guarded",))
        self.assertEqual(simulator.at_risk_case_ids, ("recovery-resume",))
        self.assertEqual(simulator.rollback_case_ids, ("pilot-containment",))

    def test_kki_federation_coordination_builds_resilience_cell(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-resilience")
        cell = next(item for item in coordination.cells if item.domain is FederationDomain.RESILIENCE)

        self.assertIsInstance(coordination, FederationCoordination)
        self.assertIsInstance(cell, FederationCell)
        self.assertEqual(cell.alignment_status, FederationAlignmentStatus.ESCALATED)
        self.assertEqual(cell.case_ids, ("pilot-containment", "recovery-resume"))

    def test_kki_federation_coordination_builds_governance_and_autonomy_cells(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-domains")

        governance_cell = next(item for item in coordination.cells if item.domain is FederationDomain.GOVERNANCE)
        autonomy_cell = next(item for item in coordination.cells if item.domain is FederationDomain.AUTONOMY)
        self.assertEqual(governance_cell.alignment_status, FederationAlignmentStatus.HANDOFF_REQUIRED)
        self.assertEqual(governance_cell.case_ids, ("shadow-guarded",))
        self.assertEqual(autonomy_cell.alignment_status, FederationAlignmentStatus.ALIGNED)
        self.assertEqual(autonomy_cell.case_ids, ("pilot-ready",))

    def test_kki_federation_coordination_creates_domain_handoffs(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-handoffs")

        self.assertEqual(len(coordination.handoffs), 2)
        self.assertIsInstance(coordination.handoffs[0], FederationHandoff)
        self.assertEqual(coordination.handoffs[0].priority, FederationHandoffPriority.CRITICAL)
        self.assertEqual(coordination.handoffs[1].priority, FederationHandoffPriority.PLANNED)

    def test_kki_federation_coordination_aggregates_coordination_signal(self) -> None:
        coordination = build_federation_coordination(coordination_id="federation-177-signal")

        self.assertEqual(coordination.coordination_signal.status, "federated-escalation")
        self.assertEqual(coordination.escalated_domains, (FederationDomain.RESILIENCE,))
        self.assertEqual(coordination.handoff_domains, (FederationDomain.GOVERNANCE,))
        self.assertEqual(coordination.aligned_domains, (FederationDomain.AUTONOMY,))

    def test_kki_program_controller_builds_resilience_track(self) -> None:
        controller = build_program_controller(controller_id="program-178-resilience")
        track = next(item for item in controller.tracks if item.track_type is ProgramTrackType.RESILIENCE)

        self.assertIsInstance(controller, ProgramController)
        self.assertIsInstance(track, ProgramTrack)
        self.assertEqual(track.directive, ProgramDirective.INTERVENE)
        self.assertEqual(track.status, ProgramControllerStatus.CRITICAL)

    def test_kki_program_controller_builds_governance_track(self) -> None:
        controller = build_program_controller(controller_id="program-178-governance")
        track = next(item for item in controller.tracks if item.track_type is ProgramTrackType.GOVERNANCE)

        self.assertEqual(track.case_ids, ("shadow-guarded",))
        self.assertEqual(track.directive, ProgramDirective.STEER)
        self.assertEqual(track.status, ProgramControllerStatus.CONTROLLED)

    def test_kki_program_controller_builds_routine_scaling_track(self) -> None:
        controller = build_program_controller(controller_id="program-178-routine")
        track = next(item for item in controller.tracks if item.track_type is ProgramTrackType.ROUTINE)

        self.assertEqual(track.case_ids, ("pilot-ready",))
        self.assertEqual(track.directive, ProgramDirective.SCALE)
        self.assertEqual(track.status, ProgramControllerStatus.SCALING)

    def test_kki_program_controller_aggregates_program_signal(self) -> None:
        controller = build_program_controller(controller_id="program-178-signal")

        self.assertEqual(controller.controller_signal.status, "program-critical")
        self.assertEqual(controller.critical_track_ids, ("program-178-signal-resilience",))
        self.assertEqual(controller.controlled_track_ids, ("program-178-signal-governance",))
        self.assertEqual(controller.scaling_track_ids, ("program-178-signal-autonomy",))

    def test_kki_operating_constitution_builds_steward_article(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-steward")
        article = next(item for item in constitution.articles if item.authority is ConstitutionalAuthority.STEWARD)

        self.assertIsInstance(constitution, OperatingConstitution)
        self.assertIsInstance(article, ConstitutionArticle)
        self.assertEqual(article.principle, ConstitutionPrinciple.STABILITY_FIRST)
        self.assertEqual(article.case_ids, ("pilot-containment", "recovery-resume"))

    def test_kki_operating_constitution_builds_governance_article(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-governance")
        article = next(item for item in constitution.articles if item.authority is ConstitutionalAuthority.GOVERNANCE)

        self.assertEqual(article.principle, ConstitutionPrinciple.GOVERNED_CHANGE)
        self.assertEqual(article.budget_ceiling, 0.65)
        self.assertEqual(article.escalation_limit, 2)

    def test_kki_operating_constitution_builds_bounded_autonomy_article(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-autonomy")
        article = next(item for item in constitution.articles if item.authority is ConstitutionalAuthority.AUTONOMY)

        self.assertEqual(article.principle, ConstitutionPrinciple.BOUNDED_AUTONOMY)
        self.assertIn("bounded-execution", article.execution_rights)
        self.assertEqual(article.escalation_limit, 3)

    def test_kki_operating_constitution_aggregates_constitution_signal(self) -> None:
        constitution = build_operating_constitution(constitution_id="constitution-179-signal")

        self.assertEqual(constitution.constitution_signal.status, "bounded-autonomy-chartered")
        self.assertEqual(constitution.steward_article_ids, ("constitution-179-signal-resilience-program",))
        self.assertEqual(constitution.governance_article_ids, ("constitution-179-signal-governance-program",))
        self.assertEqual(constitution.autonomy_article_ids, ("constitution-179-signal-routine-program",))

    def test_kki_executive_watchtower_builds_locked_resilience_order(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-resilience")
        order = next(item for item in watchtower.orders if item.track_type is ProgramTrackType.RESILIENCE)

        self.assertIsInstance(watchtower, ExecutiveWatchtower)
        self.assertIsInstance(order, ExecutiveOrder)
        self.assertEqual(order.mode, ExecutiveOrderMode.EXECUTIVE_OVERRIDE)
        self.assertEqual(order.watch_status, ExecutiveWatchStatus.LOCKED)

    def test_kki_executive_watchtower_builds_commanding_governance_order(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-governance")
        order = next(item for item in watchtower.orders if item.track_type is ProgramTrackType.GOVERNANCE)

        self.assertEqual(order.mode, ExecutiveOrderMode.GOVERNED_EXECUTION)
        self.assertEqual(order.watch_status, ExecutiveWatchStatus.COMMANDING)
        self.assertFalse(order.release_ready)

    def test_kki_executive_watchtower_builds_ready_autonomy_order(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-autonomy")
        order = next(item for item in watchtower.orders if item.track_type is ProgramTrackType.ROUTINE)

        self.assertEqual(order.mode, ExecutiveOrderMode.AUTONOMY_WINDOW)
        self.assertEqual(order.watch_status, ExecutiveWatchStatus.READY)
        self.assertTrue(order.release_ready)

    def test_kki_executive_watchtower_aggregates_watchtower_signal(self) -> None:
        watchtower = build_executive_watchtower(watchtower_id="executive-180-signal")

        self.assertEqual(watchtower.watchtower_signal.status, "executive-locked")
        self.assertEqual(watchtower.locked_order_ids, ("executive-180-signal-resilience-program",))
        self.assertEqual(watchtower.commanding_order_ids, ("executive-180-signal-governance-program",))
        self.assertEqual(watchtower.ready_order_ids, ("executive-180-signal-routine-program",))

    def test_kki_strategy_council_builds_escalated_stability_mandate(self) -> None:
        council = build_strategy_council(council_id="strategy-181-resilience")
        mandate = next(item for item in council.mandates if item.lane is StrategyLane.STABILITY)

        self.assertIsInstance(council, StrategyCouncil)
        self.assertIsInstance(mandate, StrategyMandate)
        self.assertEqual(mandate.priority, StrategyPriority.IMMEDIATE)
        self.assertEqual(mandate.escalation_mandate, StrategyEscalationMandate.CONTAINMENT)
        self.assertEqual(mandate.council_status, StrategyCouncilStatus.ESCALATED)

    def test_kki_strategy_council_builds_orchestrated_governance_mandate(self) -> None:
        council = build_strategy_council(council_id="strategy-181-governance")
        mandate = next(item for item in council.mandates if item.lane is StrategyLane.GOVERNANCE)

        self.assertEqual(mandate.priority, StrategyPriority.DIRECTED)
        self.assertEqual(mandate.escalation_mandate, StrategyEscalationMandate.REVIEW)
        self.assertEqual(mandate.council_status, StrategyCouncilStatus.ORCHESTRATED)
        self.assertFalse(mandate.release_ready)

    def test_kki_strategy_council_builds_primed_expansion_mandate(self) -> None:
        council = build_strategy_council(council_id="strategy-181-expansion")
        mandate = next(item for item in council.mandates if item.lane is StrategyLane.EXPANSION)

        self.assertEqual(mandate.priority, StrategyPriority.COMPOUND)
        self.assertEqual(mandate.escalation_mandate, StrategyEscalationMandate.EXPANSION)
        self.assertEqual(mandate.council_status, StrategyCouncilStatus.PRIMED)
        self.assertTrue(mandate.release_ready)

    def test_kki_strategy_council_aggregates_council_signal(self) -> None:
        council = build_strategy_council(council_id="strategy-181-signal")

        self.assertEqual(council.council_signal.status, "strategy-escalated")
        self.assertEqual(council.escalated_mandate_ids, ("strategy-181-signal-stability-lane",))
        self.assertEqual(council.orchestrated_mandate_ids, ("strategy-181-signal-governance-lane",))
        self.assertEqual(council.primed_mandate_ids, ("strategy-181-signal-expansion-lane",))

    def test_kki_mandate_card_deck_builds_steward_containment_card(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-steward")
        card = next(item for item in deck.cards if item.owner is ConstitutionalAuthority.STEWARD)

        self.assertIsInstance(deck, MandateCardDeck)
        self.assertIsInstance(card, MandateCard)
        self.assertEqual(card.execution_scope, MandateExecutionScope.CONTAINMENT)
        self.assertEqual(card.review_cadence, MandateReviewCadence.INCIDENT)

    def test_kki_mandate_card_deck_builds_governance_review_card(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-governance")
        card = next(item for item in deck.cards if item.owner is ConstitutionalAuthority.GOVERNANCE)

        self.assertEqual(card.execution_scope, MandateExecutionScope.GOVERNED_CHANGE)
        self.assertEqual(card.review_cadence, MandateReviewCadence.GOVERNANCE)
        self.assertFalse(card.release_ready)

    def test_kki_mandate_card_deck_builds_autonomy_expansion_card(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-autonomy")
        card = next(item for item in deck.cards if item.owner is ConstitutionalAuthority.AUTONOMY)

        self.assertEqual(card.execution_scope, MandateExecutionScope.BOUNDED_EXPANSION)
        self.assertEqual(card.review_cadence, MandateReviewCadence.EXPANSION)
        self.assertTrue(card.release_ready)

    def test_kki_mandate_card_deck_aggregates_deck_signal(self) -> None:
        deck = build_mandate_card_deck(deck_id="mandate-182-signal")

        self.assertEqual(deck.deck_signal.status, "mandate-containment-owned")
        self.assertEqual(deck.steward_card_ids, ("mandate-182-signal-stability-lane",))
        self.assertEqual(deck.governance_card_ids, ("mandate-182-signal-governance-lane",))
        self.assertEqual(deck.autonomy_card_ids, ("mandate-182-signal-expansion-lane",))

    def test_kki_portfolio_radar_builds_concentrated_stability_entry(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-stability")
        entry = next(item for item in radar.entries if item.exposure is PortfolioExposure.CONTAINED)

        self.assertIsInstance(radar, PortfolioRadar)
        self.assertIsInstance(entry, PortfolioRadarEntry)
        self.assertEqual(entry.concentration, PortfolioConcentration.CONCENTRATED)
        self.assertEqual(entry.operating_spread, PortfolioOperatingSpread.NARROW)

    def test_kki_portfolio_radar_builds_governed_balanced_entry(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-governance")
        entry = next(item for item in radar.entries if item.exposure is PortfolioExposure.GOVERNED)

        self.assertEqual(entry.concentration, PortfolioConcentration.BALANCED)
        self.assertEqual(entry.operating_spread, PortfolioOperatingSpread.COORDINATED)
        self.assertFalse(entry.release_ready)

    def test_kki_portfolio_radar_builds_expansive_distributed_entry(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-expansion")
        entry = next(item for item in radar.entries if item.exposure is PortfolioExposure.EXPANSIVE)

        self.assertEqual(entry.concentration, PortfolioConcentration.DISTRIBUTED)
        self.assertEqual(entry.operating_spread, PortfolioOperatingSpread.BROAD)
        self.assertTrue(entry.release_ready)

    def test_kki_portfolio_radar_aggregates_radar_signal(self) -> None:
        radar = build_portfolio_radar(radar_id="portfolio-183-signal")

        self.assertEqual(radar.radar_signal.status, "portfolio-concentrated")
        self.assertEqual(radar.concentrated_entry_ids, ("portfolio-183-signal-stability-lane",))
        self.assertEqual(radar.governed_entry_ids, ("portfolio-183-signal-governance-lane",))
        self.assertEqual(radar.expansive_entry_ids, ("portfolio-183-signal-expansion-lane",))

    def test_kki_scenario_chancery_builds_locked_stabilize_option(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-stability")
        option = next(item for item in chancery.options if item.mode is ScenarioOfficeMode.STABILIZE)

        self.assertIsInstance(chancery, ScenarioChancery)
        self.assertIsInstance(option, ScenarioOption)
        self.assertEqual(option.status, ScenarioOfficeStatus.LOCKED)
        self.assertFalse(option.release_ready)

    def test_kki_scenario_chancery_builds_review_steer_option(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-governance")
        option = next(item for item in chancery.options if item.mode is ScenarioOfficeMode.STEER)

        self.assertEqual(option.status, ScenarioOfficeStatus.REVIEW)
        self.assertGreater(option.comparison_score, 0.7)
        self.assertFalse(option.release_ready)

    def test_kki_scenario_chancery_builds_ready_expand_option(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-expansion")
        option = next(item for item in chancery.options if item.mode is ScenarioOfficeMode.EXPAND)

        self.assertEqual(option.status, ScenarioOfficeStatus.READY)
        self.assertTrue(option.release_ready)
        self.assertGreater(option.confidence_score, 0.6)

    def test_kki_scenario_chancery_aggregates_chancery_signal(self) -> None:
        chancery = build_scenario_chancery(chancery_id="scenario-184-signal")

        self.assertEqual(chancery.chancery_signal.status, "scenario-locked")
        self.assertEqual(chancery.locked_option_ids, ("scenario-184-signal-stability-lane",))
        self.assertEqual(chancery.review_option_ids, ("scenario-184-signal-governance-lane",))
        self.assertEqual(chancery.ready_option_ids, ("scenario-184-signal-expansion-lane",))

    def test_kki_course_corrector_builds_enforced_contain_directive(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-stability")
        directive = next(item for item in corrector.directives if item.action is CourseCorrectionAction.CONTAIN)

        self.assertIsInstance(corrector, CourseCorrector)
        self.assertIsInstance(directive, CourseCorrectionDirective)
        self.assertEqual(directive.status, CourseCorrectionStatus.ENFORCED)
        self.assertFalse(directive.release_ready)

    def test_kki_course_corrector_builds_directed_rebalance_directive(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-governance")
        directive = next(item for item in corrector.directives if item.action is CourseCorrectionAction.REBALANCE)

        self.assertEqual(directive.status, CourseCorrectionStatus.DIRECTED)
        self.assertGreater(directive.correction_score, 0.7)
        self.assertFalse(directive.release_ready)

    def test_kki_course_corrector_builds_cleared_accelerate_directive(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-expansion")
        directive = next(item for item in corrector.directives if item.action is CourseCorrectionAction.ACCELERATE)

        self.assertEqual(directive.status, CourseCorrectionStatus.CLEARED)
        self.assertTrue(directive.release_ready)
        self.assertGreater(directive.stress_index, 0.2)

    def test_kki_course_corrector_aggregates_corrector_signal(self) -> None:
        corrector = build_course_corrector(corrector_id="course-185-signal")

        self.assertEqual(corrector.corrector_signal.status, "course-enforced")
        self.assertEqual(corrector.enforced_directive_ids, ("course-185-signal-stability-lane",))
        self.assertEqual(corrector.directed_directive_ids, ("course-185-signal-governance-lane",))
        self.assertEqual(corrector.cleared_directive_ids, ("course-185-signal-expansion-lane",))

    def test_kki_mandate_memory_store_builds_sealed_record(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-sealed")
        record = next(item for item in store.records if item.memory_status is MandateMemoryStatus.SEALED)

        self.assertIsInstance(store, MandateMemoryStore)
        self.assertIsInstance(record, MandateMemoryRecord)
        self.assertEqual(record.source_action, CourseCorrectionAction.CONTAIN)
        self.assertFalse(record.release_ready)

    def test_kki_mandate_memory_store_builds_review_record(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-review")
        record = next(item for item in store.records if item.memory_status is MandateMemoryStatus.REVIEW)

        self.assertEqual(record.source_action, CourseCorrectionAction.REBALANCE)
        self.assertGreater(record.retention_score, 0.7)
        self.assertEqual(record.renewal_window, 4)

    def test_kki_mandate_memory_store_builds_renewable_record(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-renewable")
        record = next(item for item in store.records if item.memory_status is MandateMemoryStatus.RENEWABLE)

        self.assertEqual(record.source_action, CourseCorrectionAction.ACCELERATE)
        self.assertTrue(record.release_ready)
        self.assertEqual(record.renewal_window, 7)

    def test_kki_mandate_memory_store_aggregates_store_signal(self) -> None:
        store = build_mandate_memory_store(store_id="memory-186-signal")

        self.assertEqual(store.store_signal.status, "memory-sealed")
        self.assertEqual(store.sealed_record_ids, ("memory-186-signal-stability-lane",))
        self.assertEqual(store.review_record_ids, ("memory-186-signal-governance-lane",))
        self.assertEqual(store.renewable_record_ids, ("memory-186-signal-expansion-lane",))

    def test_kki_guideline_compass_builds_anchored_stability_vector(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-stability")
        vector = next(item for item in compass.vectors if item.compass_status is CompassStatus.ANCHORED)

        self.assertIsInstance(compass, GuidelineCompass)
        self.assertIsInstance(vector, GuidelineVector)
        self.assertEqual(vector.principle, GuidelinePrinciple.STABILITY_FIRST)
        self.assertEqual(vector.navigation_constraint, NavigationConstraint.HARD_BOUNDARY)

    def test_kki_guideline_compass_builds_guided_progress_vector(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-governance")
        vector = next(item for item in compass.vectors if item.compass_status is CompassStatus.GUIDED)

        self.assertEqual(vector.principle, GuidelinePrinciple.GOVERNED_PROGRESS)
        self.assertEqual(vector.navigation_constraint, NavigationConstraint.GOVERNED_CORRIDOR)
        self.assertGreater(vector.guidance_score, 0.7)

    def test_kki_guideline_compass_builds_open_expansion_vector(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-expansion")
        vector = next(item for item in compass.vectors if item.compass_status is CompassStatus.OPEN)

        self.assertEqual(vector.principle, GuidelinePrinciple.BOUNDED_EXPANSION)
        self.assertEqual(vector.navigation_constraint, NavigationConstraint.EXPANSION_WINDOW)
        self.assertTrue(vector.release_ready)

    def test_kki_guideline_compass_aggregates_compass_signal(self) -> None:
        compass = build_guideline_compass(compass_id="compass-187-signal")

        self.assertEqual(compass.compass_signal.status, "compass-anchored")
        self.assertEqual(compass.anchored_vector_ids, ("compass-187-signal-stability-lane",))
        self.assertEqual(compass.guided_vector_ids, ("compass-187-signal-governance-lane",))
        self.assertEqual(compass.open_vector_ids, ("compass-187-signal-expansion-lane",))

    def test_kki_intervention_charter_builds_restricted_stability_clause(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-stability")
        clause = next(item for item in charter.clauses if item.charter_status is CharterStatus.RESTRICTED)

        self.assertIsInstance(charter, InterventionCharter)
        self.assertIsInstance(clause, InterventionClause)
        self.assertEqual(clause.intervention_right, InterventionRight.STEWARD_VETO)
        self.assertEqual(clause.stop_condition, StopCondition.HARD_BOUNDARY_BREACH)
        self.assertEqual(clause.release_threshold, ReleaseThreshold.EXECUTIVE_OVERRIDE)

    def test_kki_intervention_charter_builds_guarded_governance_clause(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-governance")
        clause = next(item for item in charter.clauses if item.charter_status is CharterStatus.GUARDED)

        self.assertEqual(clause.intervention_right, InterventionRight.GOVERNANCE_REVIEW)
        self.assertEqual(clause.stop_condition, StopCondition.CORRIDOR_DEVIATION)
        self.assertEqual(clause.release_threshold, ReleaseThreshold.GOVERNANCE_CLEARANCE)
        self.assertGreater(clause.intervention_score, 0.7)

    def test_kki_intervention_charter_builds_enabled_expansion_clause(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-expansion")
        clause = next(item for item in charter.clauses if item.charter_status is CharterStatus.ENABLED)

        self.assertEqual(clause.intervention_right, InterventionRight.AUTONOMY_WINDOW)
        self.assertEqual(clause.stop_condition, StopCondition.WINDOW_EXHAUSTED)
        self.assertEqual(clause.release_threshold, ReleaseThreshold.READINESS_QUORUM)
        self.assertTrue(clause.release_ready)

    def test_kki_intervention_charter_aggregates_charter_signal(self) -> None:
        charter = build_intervention_charter(charter_id="charter-188-signal")

        self.assertEqual(charter.charter_signal.status, "charter-restricted")
        self.assertEqual(charter.restricted_clause_ids, ("charter-188-signal-stability-lane",))
        self.assertEqual(charter.guarded_clause_ids, ("charter-188-signal-governance-lane",))
        self.assertEqual(charter.enabled_clause_ids, ("charter-188-signal-expansion-lane",))

    def test_kki_program_senate_builds_contested_stability_seat(self) -> None:
        senate = build_program_senate(senate_id="senate-189-stability")
        seat = next(item for item in senate.seats if item.balance_status is SenateBalanceStatus.CONTESTED)

        self.assertIsInstance(senate, ProgramSenate)
        self.assertIsInstance(seat, SenateSeat)
        self.assertEqual(seat.priority, SenatePriority.CONSTITUTION_FIRST)
        self.assertEqual(seat.resolution, SenateResolution.VETO)

    def test_kki_program_senate_builds_balanced_governance_seat(self) -> None:
        senate = build_program_senate(senate_id="senate-189-governance")
        seat = next(item for item in senate.seats if item.balance_status is SenateBalanceStatus.BALANCED)

        self.assertEqual(seat.priority, SenatePriority.JOINT_REVIEW)
        self.assertEqual(seat.resolution, SenateResolution.NEGOTIATE)
        self.assertGreater(seat.consensus_score, 0.5)

    def test_kki_program_senate_builds_aligned_expansion_seat(self) -> None:
        senate = build_program_senate(senate_id="senate-189-expansion")
        seat = next(item for item in senate.seats if item.balance_status is SenateBalanceStatus.ALIGNED)

        self.assertEqual(seat.priority, SenatePriority.PROGRAM_ADVANCE)
        self.assertEqual(seat.resolution, SenateResolution.ENDORSE)
        self.assertTrue(seat.release_ready)

    def test_kki_program_senate_aggregates_senate_signal(self) -> None:
        senate = build_program_senate(senate_id="senate-189-signal")

        self.assertEqual(senate.senate_signal.status, "senate-contested")
        self.assertEqual(senate.contested_seat_ids, ("senate-189-signal-stability-lane",))
        self.assertEqual(senate.balanced_seat_ids, ("senate-189-signal-governance-lane",))
        self.assertEqual(senate.aligned_seat_ids, ("senate-189-signal-expansion-lane",))

    def test_kki_directive_consensus_builds_binding_stability_directive(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-stability")
        directive = next(item for item in consensus.directives if item.directive_status is ConsensusDirectiveStatus.BINDING)

        self.assertIsInstance(consensus, DirectiveConsensus)
        self.assertIsInstance(directive, ConsensusDirective)
        self.assertEqual(directive.directive_type, ConsensusDirectiveType.CONSTITUTIONAL_LOCK)
        self.assertEqual(directive.mandate, ConsensusMandate.HOLD)

    def test_kki_directive_consensus_builds_negotiated_governance_directive(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-governance")
        directive = next(item for item in consensus.directives if item.directive_status is ConsensusDirectiveStatus.NEGOTIATED)

        self.assertEqual(directive.directive_type, ConsensusDirectiveType.GOVERNED_COMPACT)
        self.assertEqual(directive.mandate, ConsensusMandate.ALIGN)
        self.assertGreater(directive.consensus_strength, 0.5)

    def test_kki_directive_consensus_builds_ratified_expansion_directive(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-expansion")
        directive = next(item for item in consensus.directives if item.directive_status is ConsensusDirectiveStatus.RATIFIED)

        self.assertEqual(directive.directive_type, ConsensusDirectiveType.EXPANSION_ACCORD)
        self.assertEqual(directive.mandate, ConsensusMandate.RELEASE)
        self.assertTrue(directive.release_ready)

    def test_kki_directive_consensus_aggregates_consensus_signal(self) -> None:
        consensus = build_directive_consensus(consensus_id="consensus-190-signal")

        self.assertEqual(consensus.consensus_signal.status, "consensus-binding")
        self.assertEqual(consensus.binding_directive_ids, ("consensus-190-signal-stability-lane",))
        self.assertEqual(consensus.negotiated_directive_ids, ("consensus-190-signal-governance-lane",))
        self.assertEqual(consensus.ratified_directive_ids, ("consensus-190-signal-expansion-lane",))

    def test_kki_decision_archive_builds_sealed_binding_entry(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-binding")
        entry = next(item for item in archive.entries if item.archive_status is ArchiveStatus.SEALED)

        self.assertIsInstance(archive, DecisionArchive)
        self.assertIsInstance(entry, ArchiveEntry)
        self.assertEqual(entry.retention, ArchiveRetention.AUDIT)
        self.assertEqual(entry.directive_status, ConsensusDirectiveStatus.BINDING)

    def test_kki_decision_archive_builds_indexed_negotiated_entry(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-negotiated")
        entry = next(item for item in archive.entries if item.archive_status is ArchiveStatus.INDEXED)

        self.assertEqual(entry.retention, ArchiveRetention.AUDIT)
        self.assertEqual(entry.directive_status, ConsensusDirectiveStatus.NEGOTIATED)
        self.assertGreater(entry.archive_weight, 0.5)

    def test_kki_decision_archive_builds_codified_ratified_entry(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-ratified")
        entry = next(item for item in archive.entries if item.archive_status is ArchiveStatus.CODIFIED)

        self.assertEqual(entry.retention, ArchiveRetention.KNOWLEDGE)
        self.assertEqual(entry.directive_status, ConsensusDirectiveStatus.RATIFIED)
        self.assertTrue(entry.release_ready)

    def test_kki_decision_archive_aggregates_archive_signal(self) -> None:
        archive = build_decision_archive(archive_id="archive-191-signal")

        self.assertEqual(archive.archive_signal.status, "archive-sealed")
        self.assertEqual(archive.sealed_entry_ids, ("archive-191-signal-stability-lane",))
        self.assertEqual(archive.indexed_entry_ids, ("archive-191-signal-governance-lane",))
        self.assertEqual(archive.codified_entry_ids, ("archive-191-signal-expansion-lane",))

    def test_kki_execution_cabinet_builds_locked_stability_order(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-stability")
        order = next(item for item in cabinet.orders if item.cabinet_status is CabinetStatus.LOCKED)

        self.assertIsInstance(cabinet, ExecutionCabinet)
        self.assertIsInstance(order, CabinetOrder)
        self.assertEqual(order.cabinet_role, CabinetRole.STEWARD_CHIEF)
        self.assertEqual(order.execution_mode, CabinetExecutionMode.ENFORCE_HOLD)

    def test_kki_execution_cabinet_builds_supervising_governance_order(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-governance")
        order = next(item for item in cabinet.orders if item.cabinet_status is CabinetStatus.SUPERVISING)

        self.assertEqual(order.cabinet_role, CabinetRole.GOVERNANCE_MINISTER)
        self.assertEqual(order.execution_mode, CabinetExecutionMode.COORDINATE_ALIGNMENT)
        self.assertGreater(order.authority_band, 0.6)

    def test_kki_execution_cabinet_builds_commissioned_expansion_order(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-expansion")
        order = next(item for item in cabinet.orders if item.cabinet_status is CabinetStatus.COMMISSIONED)

        self.assertEqual(order.cabinet_role, CabinetRole.AUTONOMY_MINISTER)
        self.assertEqual(order.execution_mode, CabinetExecutionMode.AUTHORIZE_RELEASE)
        self.assertTrue(order.release_ready)

    def test_kki_execution_cabinet_aggregates_cabinet_signal(self) -> None:
        cabinet = build_execution_cabinet(cabinet_id="cabinet-192-signal")

        self.assertEqual(cabinet.cabinet_signal.status, "cabinet-locked")
        self.assertEqual(cabinet.locked_order_ids, ("cabinet-192-signal-stability-lane",))
        self.assertEqual(cabinet.supervising_order_ids, ("cabinet-192-signal-governance-lane",))
        self.assertEqual(cabinet.commissioned_order_ids, ("cabinet-192-signal-expansion-lane",))

    def test_kki_delegation_matrix_builds_pinned_steward_entry(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-stability")
        entry = next(item for item in matrix.delegations if item.delegation_status is DelegationStatus.PINNED)

        self.assertIsInstance(matrix, DelegationMatrix)
        self.assertIsInstance(entry, DelegationEntry)
        self.assertEqual(entry.delegation_lane, DelegationLane.STEWARD_PATH)
        self.assertEqual(entry.delegation_mode, DelegationMode.HARD_HANDOFF)

    def test_kki_delegation_matrix_builds_routed_governance_entry(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-governance")
        entry = next(item for item in matrix.delegations if item.delegation_status is DelegationStatus.ROUTED)

        self.assertEqual(entry.delegation_lane, DelegationLane.GOVERNANCE_PATH)
        self.assertEqual(entry.delegation_mode, DelegationMode.GOVERNED_HANDOFF)
        self.assertGreater(entry.handoff_score, 0.6)

    def test_kki_delegation_matrix_builds_open_autonomy_entry(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-expansion")
        entry = next(item for item in matrix.delegations if item.delegation_status is DelegationStatus.OPEN)

        self.assertEqual(entry.delegation_lane, DelegationLane.AUTONOMY_PATH)
        self.assertEqual(entry.delegation_mode, DelegationMode.ENABLED_HANDOFF)
        self.assertTrue(entry.release_ready)

    def test_kki_delegation_matrix_aggregates_matrix_signal(self) -> None:
        matrix = build_delegation_matrix(matrix_id="matrix-193-signal")

        self.assertEqual(matrix.matrix_signal.status, "delegation-pinned")
        self.assertEqual(matrix.pinned_delegation_ids, ("matrix-193-signal-stability-lane",))
        self.assertEqual(matrix.routed_delegation_ids, ("matrix-193-signal-governance-lane",))
        self.assertEqual(matrix.open_delegation_ids, ("matrix-193-signal-expansion-lane",))

    def test_kki_veto_sluice_builds_blocking_stability_channel(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-stability")
        channel = next(item for item in sluice.channels if item.sluice_status is SluiceStatus.BLOCKING)

        self.assertIsInstance(sluice, VetoSluice)
        self.assertIsInstance(channel, VetoChannel)
        self.assertEqual(channel.veto_stop, VetoStop.HARD_STOP)
        self.assertEqual(channel.release_path, ReleasePath.EXECUTIVE_RELEASE)
        self.assertEqual(channel.recall_path, RecallPath.IMMEDIATE_RECALL)

    def test_kki_veto_sluice_builds_reviewing_governance_channel(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-governance")
        channel = next(item for item in sluice.channels if item.sluice_status is SluiceStatus.REVIEWING)

        self.assertEqual(channel.veto_stop, VetoStop.REVIEW_STOP)
        self.assertEqual(channel.release_path, ReleasePath.GOVERNED_RELEASE)
        self.assertEqual(channel.recall_path, RecallPath.GOVERNED_RECALL)
        self.assertGreater(channel.guard_score, 0.6)

    def test_kki_veto_sluice_builds_clearing_autonomy_channel(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-expansion")
        channel = next(item for item in sluice.channels if item.sluice_status is SluiceStatus.CLEARING)

        self.assertEqual(channel.veto_stop, VetoStop.OPEN_STOP)
        self.assertEqual(channel.release_path, ReleasePath.AUTONOMY_RELEASE)
        self.assertEqual(channel.recall_path, RecallPath.SUPERVISED_RECALL)
        self.assertTrue(channel.release_ready)

    def test_kki_veto_sluice_aggregates_sluice_signal(self) -> None:
        sluice = build_veto_sluice(sluice_id="sluice-194-signal")

        self.assertEqual(sluice.sluice_signal.status, "sluice-blocking")
        self.assertEqual(sluice.blocking_channel_ids, ("sluice-194-signal-stability-lane",))
        self.assertEqual(sluice.reviewing_channel_ids, ("sluice-194-signal-governance-lane",))
        self.assertEqual(sluice.clearing_channel_ids, ("sluice-194-signal-expansion-lane",))

    def test_kki_consensus_diplomacy_builds_deadlocked_stability_channel(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-stability")
        channel = next(item for item in diplomacy.channels if item.diplomacy_status is DiplomacyStatus.DEADLOCKED)

        self.assertIsInstance(diplomacy, ConsensusDiplomacy)
        self.assertIsInstance(channel, DiplomacyChannel)
        self.assertEqual(channel.posture, DiplomacyPosture.CONTAINMENT_TALKS)
        self.assertEqual(channel.diplomacy_path, DiplomacyPath.VETO_TABLE)

    def test_kki_consensus_diplomacy_builds_brokered_governance_channel(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-governance")
        channel = next(item for item in diplomacy.channels if item.diplomacy_status is DiplomacyStatus.BROKERED)

        self.assertEqual(channel.posture, DiplomacyPosture.REVIEW_COMPACT)
        self.assertEqual(channel.diplomacy_path, DiplomacyPath.GOVERNANCE_TABLE)
        self.assertGreater(channel.compromise_score, 0.5)

    def test_kki_consensus_diplomacy_builds_harmonized_autonomy_channel(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-expansion")
        channel = next(item for item in diplomacy.channels if item.diplomacy_status is DiplomacyStatus.HARMONIZED)

        self.assertEqual(channel.posture, DiplomacyPosture.RELEASE_ACCORD)
        self.assertEqual(channel.diplomacy_path, DiplomacyPath.AUTONOMY_TABLE)
        self.assertTrue(channel.release_ready)

    def test_kki_consensus_diplomacy_aggregates_diplomacy_signal(self) -> None:
        diplomacy = build_consensus_diplomacy(diplomacy_id="diplomacy-195-signal")

        self.assertEqual(diplomacy.diplomacy_signal.status, "diplomacy-deadlocked")
        self.assertEqual(diplomacy.deadlocked_channel_ids, ("diplomacy-195-signal-stability-lane",))
        self.assertEqual(diplomacy.brokered_channel_ids, ("diplomacy-195-signal-governance-lane",))
        self.assertEqual(diplomacy.harmonized_channel_ids, ("diplomacy-195-signal-expansion-lane",))

    def test_kki_leitstern_doctrine_builds_guarded_boundary_clause(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-stability")
        clause = next(item for item in doctrine.clauses if item.doctrine_status is DoctrineStatus.GUARDED)

        self.assertIsInstance(doctrine, LeitsternDoctrine)
        self.assertIsInstance(clause, DoctrineClause)
        self.assertEqual(clause.principle, DoctrinePrinciple.BOUNDARY_PRIMACY)
        self.assertEqual(clause.doctrine_scope, DoctrineScope.STEWARD_CANON)

    def test_kki_leitstern_doctrine_builds_adopted_governance_clause(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-governance")
        clause = next(item for item in doctrine.clauses if item.doctrine_status is DoctrineStatus.ADOPTED)

        self.assertEqual(clause.principle, DoctrinePrinciple.GOVERNED_ALIGNMENT)
        self.assertEqual(clause.doctrine_scope, DoctrineScope.GOVERNANCE_CANON)
        self.assertGreater(clause.doctrine_strength, 0.5)

    def test_kki_leitstern_doctrine_builds_enshrined_autonomy_clause(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-expansion")
        clause = next(item for item in doctrine.clauses if item.doctrine_status is DoctrineStatus.ENSHRINED)

        self.assertEqual(clause.principle, DoctrinePrinciple.EXPANSION_DISCIPLINE)
        self.assertEqual(clause.doctrine_scope, DoctrineScope.AUTONOMY_CANON)
        self.assertTrue(clause.release_ready)

    def test_kki_leitstern_doctrine_aggregates_doctrine_signal(self) -> None:
        doctrine = build_leitstern_doctrine(doctrine_id="doctrine-196-signal")

        self.assertEqual(doctrine.doctrine_signal.status, "doctrine-guarded")
        self.assertEqual(doctrine.guarded_clause_ids, ("doctrine-196-signal-stability-lane",))
        self.assertEqual(doctrine.adopted_clause_ids, ("doctrine-196-signal-governance-lane",))
        self.assertEqual(doctrine.enshrined_clause_ids, ("doctrine-196-signal-expansion-lane",))

    def test_kki_missions_collegium_builds_reserved_stability_seat(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-stability")
        seat = next(item for item in collegium.seats if item.collegium_status is CollegiumStatus.RESERVED)

        self.assertIsInstance(collegium, MissionsCollegium)
        self.assertIsInstance(seat, CollegiumSeat)
        self.assertEqual(seat.collegium_mandate, CollegiumMandate.STABILITY_CHAIR)
        self.assertEqual(seat.collegium_lane, CollegiumLane.CONTAINMENT_PORTFOLIO)
        self.assertEqual(seat.mission_ref, "recovery-drill")

    def test_kki_missions_collegium_builds_coordinating_governance_seat(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-governance")
        seat = next(item for item in collegium.seats if item.collegium_status is CollegiumStatus.COORDINATING)

        self.assertEqual(seat.collegium_mandate, CollegiumMandate.GOVERNANCE_CHAIR)
        self.assertEqual(seat.collegium_lane, CollegiumLane.GOVERNANCE_PORTFOLIO)
        self.assertEqual(seat.mission_ref, "shadow-hardening")
        self.assertGreater(seat.collegium_weight, 0.3)

    def test_kki_missions_collegium_builds_deployed_autonomy_seat(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-expansion")
        seat = next(item for item in collegium.seats if item.collegium_status is CollegiumStatus.DEPLOYED)

        self.assertEqual(seat.collegium_mandate, CollegiumMandate.EXPANSION_CHAIR)
        self.assertEqual(seat.collegium_lane, CollegiumLane.EXPANSION_PORTFOLIO)
        self.assertEqual(seat.mission_ref, "pilot-cutover")
        self.assertTrue(seat.release_ready)

    def test_kki_missions_collegium_aggregates_collegium_signal(self) -> None:
        collegium = build_missions_collegium(collegium_id="collegium-197-signal")

        self.assertEqual(collegium.collegium_signal.status, "collegium-reserved")
        self.assertEqual(collegium.reserved_seat_ids, ("collegium-197-signal-stability-lane",))
        self.assertEqual(collegium.coordinating_seat_ids, ("collegium-197-signal-governance-lane",))
        self.assertEqual(collegium.deployed_seat_ids, ("collegium-197-signal-expansion-lane",))

    def test_kki_priority_conclave_builds_guarded_stability_motion(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-stability")
        motion = next(item for item in conclave.motions if item.conclave_status is ConclaveStatus.GUARDED)

        self.assertIsInstance(conclave, PriorityConclave)
        self.assertIsInstance(motion, ConclaveMotion)
        self.assertEqual(motion.conclave_priority, ConclavePriority.STABILITY_FIRST)
        self.assertEqual(motion.conclave_lane, ConclaveLane.CONTAINMENT_SLOT)
        self.assertEqual(motion.mission_ref, "recovery-drill")

    def test_kki_priority_conclave_builds_shortlisted_governance_motion(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-governance")
        motion = next(item for item in conclave.motions if item.conclave_status is ConclaveStatus.SHORTLISTED)

        self.assertEqual(motion.conclave_priority, ConclavePriority.GOVERNANCE_FOCUS)
        self.assertEqual(motion.conclave_lane, ConclaveLane.GOVERNANCE_SLOT)
        self.assertEqual(motion.mission_ref, "shadow-hardening")
        self.assertGreater(motion.priority_score, 0.4)

    def test_kki_priority_conclave_builds_elected_autonomy_motion(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-expansion")
        motion = next(item for item in conclave.motions if item.conclave_status is ConclaveStatus.ELECTED)

        self.assertEqual(motion.conclave_priority, ConclavePriority.RELEASE_VECTOR)
        self.assertEqual(motion.conclave_lane, ConclaveLane.EXPANSION_SLOT)
        self.assertEqual(motion.mission_ref, "pilot-cutover")
        self.assertTrue(motion.release_ready)

    def test_kki_priority_conclave_aggregates_conclave_signal(self) -> None:
        conclave = build_priority_conclave(conclave_id="conclave-198-signal")

        self.assertEqual(conclave.conclave_signal.status, "conclave-guarded")
        self.assertEqual(conclave.guarded_motion_ids, ("conclave-198-signal-stability-lane",))
        self.assertEqual(conclave.shortlisted_motion_ids, ("conclave-198-signal-governance-lane",))
        self.assertEqual(conclave.elected_motion_ids, ("conclave-198-signal-expansion-lane",))

    def test_kki_course_contract_builds_protective_stability_clause(self) -> None:
        contract = build_course_contract(contract_id="contract-199-stability")
        clause = next(item for item in contract.clauses if item.contract_status is ContractStatus.PROTECTIVE)

        self.assertIsInstance(contract, CourseContract)
        self.assertIsInstance(clause, ContractClause)
        self.assertEqual(clause.contract_party, ContractParty.STEWARD_ASSEMBLY)
        self.assertEqual(clause.contract_commitment, ContractCommitment.HOLD_LINE)
        self.assertEqual(clause.mission_ref, "recovery-drill")

    def test_kki_course_contract_builds_operative_governance_clause(self) -> None:
        contract = build_course_contract(contract_id="contract-199-governance")
        clause = next(item for item in contract.clauses if item.contract_status is ContractStatus.OPERATIVE)

        self.assertEqual(clause.contract_party, ContractParty.GOVERNANCE_ASSEMBLY)
        self.assertEqual(clause.contract_commitment, ContractCommitment.ALIGN_LINE)
        self.assertEqual(clause.mission_ref, "shadow-hardening")
        self.assertGreater(clause.contract_strength, 0.4)

    def test_kki_course_contract_builds_binding_autonomy_clause(self) -> None:
        contract = build_course_contract(contract_id="contract-199-expansion")
        clause = next(item for item in contract.clauses if item.contract_status is ContractStatus.BINDING)

        self.assertEqual(clause.contract_party, ContractParty.AUTONOMY_ASSEMBLY)
        self.assertEqual(clause.contract_commitment, ContractCommitment.ADVANCE_LINE)
        self.assertEqual(clause.mission_ref, "pilot-cutover")
        self.assertTrue(clause.release_ready)

    def test_kki_course_contract_aggregates_contract_signal(self) -> None:
        contract = build_course_contract(contract_id="contract-199-signal")

        self.assertEqual(contract.contract_signal.status, "contract-protective")
        self.assertEqual(contract.protective_clause_ids, ("contract-199-signal-stability-lane",))
        self.assertEqual(contract.operative_clause_ids, ("contract-199-signal-governance-lane",))
        self.assertEqual(contract.binding_clause_ids, ("contract-199-signal-expansion-lane",))

    def test_kki_leitstern_codex_builds_guarded_decision_section(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-stability")
        section = next(item for item in codex.sections if item.codex_status is CodexStatus.GUARDED)

        self.assertIsInstance(codex, LeitsternCodex)
        self.assertIsInstance(section, CodexSection)
        self.assertEqual(section.codex_canon, CodexCanon.DECISION_CANON)
        self.assertEqual(section.codex_axis, CodexAxis.DECISION_ORDER)
        self.assertEqual(section.mission_ref, "recovery-drill")

    def test_kki_leitstern_codex_builds_governed_delegation_section(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-governance")
        section = next(item for item in codex.sections if item.codex_status is CodexStatus.GOVERNED)

        self.assertEqual(section.codex_canon, CodexCanon.GOVERNANCE_CANON)
        self.assertEqual(section.codex_axis, CodexAxis.DELEGATION_ORDER)
        self.assertEqual(section.mission_ref, "shadow-hardening")
        self.assertGreater(section.codex_strength, 0.4)

    def test_kki_leitstern_codex_builds_canonical_diplomacy_section(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-expansion")
        section = next(item for item in codex.sections if item.codex_status is CodexStatus.CANONICAL)

        self.assertEqual(section.codex_canon, CodexCanon.EXPANSION_CANON)
        self.assertEqual(section.codex_axis, CodexAxis.DIPLOMACY_ORDER)
        self.assertEqual(section.mission_ref, "pilot-cutover")
        self.assertTrue(section.release_ready)

    def test_kki_leitstern_codex_aggregates_codex_signal(self) -> None:
        codex = build_leitstern_codex(codex_id="codex-200-signal")

        self.assertEqual(codex.codex_signal.status, "codex-guarded")
        self.assertEqual(codex.guarded_section_ids, ("codex-200-signal-stability-lane",))
        self.assertEqual(codex.governed_section_ids, ("codex-200-signal-governance-lane",))
        self.assertEqual(codex.canonical_section_ids, ("codex-200-signal-expansion-lane",))

    def test_kki_kodex_register_builds_reserved_decision_entry(self) -> None:
        register = build_kodex_register(register_id="register-201-stability")
        entry = next(item for item in register.entries if item.register_tier is RegisterTier.RESERVED)

        self.assertIsInstance(register, KodexRegister)
        self.assertIsInstance(entry, KodexRegisterEntry)
        self.assertEqual(entry.codex_canon, CodexCanon.DECISION_CANON)
        self.assertEqual(entry.retention, RegisterRetention.AUDIT)
        self.assertEqual(entry.version, "v1.1")

    def test_kki_kodex_register_builds_curated_governance_entry(self) -> None:
        register = build_kodex_register(register_id="register-201-governance")
        entry = next(item for item in register.entries if item.register_tier is RegisterTier.CURATED)

        self.assertEqual(entry.codex_canon, CodexCanon.GOVERNANCE_CANON)
        self.assertEqual(entry.retention, RegisterRetention.GOVERNANCE)
        self.assertGreater(entry.register_weight, 0.4)

    def test_kki_kodex_register_builds_canonized_expansion_entry(self) -> None:
        register = build_kodex_register(register_id="register-201-expansion")
        entry = next(item for item in register.entries if item.register_tier is RegisterTier.CANONIZED)

        self.assertEqual(entry.codex_canon, CodexCanon.EXPANSION_CANON)
        self.assertEqual(entry.retention, RegisterRetention.CONSTITUTIONAL)
        self.assertTrue(entry.release_ready)

    def test_kki_kodex_register_aggregates_register_signal(self) -> None:
        register = build_kodex_register(register_id="register-201-signal")

        self.assertEqual(register.register_signal.status, "register-reserved")
        self.assertEqual(register.reserved_entry_ids, ("register-201-signal-stability-lane",))
        self.assertEqual(register.curated_entry_ids, ("register-201-signal-governance-lane",))
        self.assertEqual(register.canonized_entry_ids, ("register-201-signal-expansion-lane",))

    def test_kki_satzungs_rat_builds_provisional_steward_article(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-stability")
        article = next(item for item in rat.articles if item.rat_status is RatStatus.PROVISIONAL)

        self.assertIsInstance(rat, SatzungsRat)
        self.assertIsInstance(article, SatzungsRatArticle)
        self.assertEqual(article.bench, RatBench.STEWARD_BENCH)
        self.assertEqual(article.interpretation, RatInterpretation.PROTECTIVE_READING)
        self.assertEqual(article.precedent_window, 1)

    def test_kki_satzungs_rat_builds_ratified_governance_article(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-governance")
        article = next(item for item in rat.articles if item.rat_status is RatStatus.RATIFIED)

        self.assertEqual(article.bench, RatBench.GOVERNANCE_BENCH)
        self.assertEqual(article.interpretation, RatInterpretation.GOVERNED_READING)
        self.assertGreater(article.statute_weight, 0.45)

    def test_kki_satzungs_rat_builds_enshrined_autonomy_article(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-expansion")
        article = next(item for item in rat.articles if item.rat_status is RatStatus.ENSHRINED)

        self.assertEqual(article.bench, RatBench.AUTONOMY_BENCH)
        self.assertEqual(article.interpretation, RatInterpretation.SOVEREIGN_READING)
        self.assertTrue(article.release_ready)

    def test_kki_satzungs_rat_aggregates_rat_signal(self) -> None:
        rat = build_satzungs_rat(rat_id="rat-202-signal")

        self.assertEqual(rat.rat_signal.status, "rat-provisional")
        self.assertEqual(rat.provisional_article_ids, ("rat-202-signal-stability-lane",))
        self.assertEqual(rat.ratified_article_ids, ("rat-202-signal-governance-lane",))
        self.assertEqual(rat.enshrined_article_ids, ("rat-202-signal-expansion-lane",))

    def test_kki_mandats_konvent_builds_begrenzt_steward_line(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-stability")
        line = next(item for item in konvent.lines if item.konvent_status is KonventStatus.BEGRENZT)

        self.assertIsInstance(konvent, MandatsKonvent)
        self.assertIsInstance(line, MandatsLinie)
        self.assertEqual(line.konvent_mandat, KonventMandat.SCHUTZ_MANDAT)
        self.assertEqual(line.konvent_ebene, KonventEbene.STEWARD_EBENE)
        self.assertEqual(line.handoff_window, 1)

    def test_kki_mandats_konvent_builds_delegiert_governance_line(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-governance")
        line = next(item for item in konvent.lines if item.konvent_status is KonventStatus.DELEGIERT)

        self.assertEqual(line.konvent_mandat, KonventMandat.ORDNUNGS_MANDAT)
        self.assertEqual(line.konvent_ebene, KonventEbene.GOVERNANCE_EBENE)
        self.assertGreater(line.delegations_budget, 0.5)

    def test_kki_mandats_konvent_builds_verankert_autonomy_line(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-expansion")
        line = next(item for item in konvent.lines if item.konvent_status is KonventStatus.VERANKERT)

        self.assertEqual(line.konvent_mandat, KonventMandat.SOUVERAENITAETS_MANDAT)
        self.assertEqual(line.konvent_ebene, KonventEbene.AUTONOMIE_EBENE)
        self.assertTrue(line.release_ready)

    def test_kki_mandats_konvent_aggregates_konvent_signal(self) -> None:
        konvent = build_mandats_konvent(konvent_id="konvent-203-signal")

        self.assertEqual(konvent.konvent_signal.status, "konvent-begrenzt")
        self.assertEqual(konvent.begrenzt_line_ids, ("konvent-203-signal-stability-lane",))
        self.assertEqual(konvent.delegiert_line_ids, ("konvent-203-signal-governance-lane",))
        self.assertEqual(konvent.verankert_line_ids, ("konvent-203-signal-expansion-lane",))

    def test_kki_ewigkeits_norm_builds_gesperrt_schutz_eintrag(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-stability")
        eintrag = next(e for e in norm.eintraege if e.geltung is EwigkeitsGeltung.GESPERRT)

        self.assertIsInstance(norm, EwigkeitsNorm)
        self.assertIsInstance(eintrag, EwigkeitsEintrag)
        self.assertEqual(eintrag.ewigkeits_typ, EwigkeitsTyp.SCHUTZ_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, EwigkeitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.ewigkeits_tier, 1)

    def test_kki_ewigkeits_norm_builds_verewigt_ordnungs_eintrag(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-governance")
        eintrag = next(e for e in norm.eintraege if e.geltung is EwigkeitsGeltung.VEREWIGT)

        self.assertEqual(eintrag.ewigkeits_typ, EwigkeitsTyp.ORDNUNGS_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, EwigkeitsProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.ewigkeits_weight, 0.45)

    def test_kki_ewigkeits_norm_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-expansion")
        eintrag = next(e for e in norm.eintraege if e.geltung is EwigkeitsGeltung.GRUNDLEGEND_VEREWIGT)

        self.assertEqual(eintrag.ewigkeits_typ, EwigkeitsTyp.SOUVERAENITAETS_EWIGKEIT)
        self.assertEqual(eintrag.prozedur, EwigkeitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_ewigkeits_norm_aggregates_norm_signal(self) -> None:
        norm = build_ewigkeits_norm(norm_id="norm-228-signal")

        self.assertEqual(norm.norm_signal.status, "norm-gesperrt")
        self.assertEqual(norm.gesperrt_eintrag_ids, ("norm-228-signal-stability-lane",))
        self.assertEqual(norm.verewigt_eintrag_ids, ("norm-228-signal-governance-lane",))
        self.assertEqual(norm.grundlegend_eintrag_ids, ("norm-228-signal-expansion-lane",))

    def test_kki_supremats_register_builds_gesperrt_schutz_norm(self) -> None:
        register = build_supremats_register(register_id="register-227-stability")
        norm = next(n for n in register.normen if n.geltung is SuprematsGeltung.GESPERRT)

        self.assertIsInstance(register, SuprematsRegister)
        self.assertIsInstance(norm, SuprematsNorm)
        self.assertEqual(norm.supremats_klasse, SuprematsKlasse.SCHUTZ_SUPREMAT)
        self.assertEqual(norm.prozedur, SuprematsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.supremats_tier, 1)

    def test_kki_supremats_register_builds_supremiert_ordnungs_norm(self) -> None:
        register = build_supremats_register(register_id="register-227-governance")
        norm = next(n for n in register.normen if n.geltung is SuprematsGeltung.SUPREMIERT)

        self.assertEqual(norm.supremats_klasse, SuprematsKlasse.ORDNUNGS_SUPREMAT)
        self.assertEqual(norm.prozedur, SuprematsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.supremats_weight, 0.45)

    def test_kki_supremats_register_builds_grundlegend_souveraenitaets_norm(self) -> None:
        register = build_supremats_register(register_id="register-227-expansion")
        norm = next(n for n in register.normen if n.geltung is SuprematsGeltung.GRUNDLEGEND_SUPREMIERT)

        self.assertEqual(norm.supremats_klasse, SuprematsKlasse.SOUVERAENITAETS_SUPREMAT)
        self.assertEqual(norm.prozedur, SuprematsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_supremats_register_aggregates_register_signal(self) -> None:
        register = build_supremats_register(register_id="register-227-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_norm_ids, ("register-227-signal-stability-lane",))
        self.assertEqual(register.supremiert_norm_ids, ("register-227-signal-governance-lane",))
        self.assertEqual(register.grundlegend_norm_ids, ("register-227-signal-expansion-lane",))

    def test_kki_hoheits_manifest_builds_gesperrt_schutz_norm(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-stability")
        norm = next(n for n in manifest.normen if n.geltung is HoheitsGeltung.GESPERRT)

        self.assertIsInstance(manifest, HoheitsManifest)
        self.assertIsInstance(norm, HoheitsNorm)
        self.assertEqual(norm.hoheits_grad, HoheitsGrad.SCHUTZ_GRAD)
        self.assertEqual(norm.prozedur, HoheitsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.hoheits_tier, 1)

    def test_kki_hoheits_manifest_builds_proklamiert_ordnungs_norm(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-governance")
        norm = next(n for n in manifest.normen if n.geltung is HoheitsGeltung.PROKLAMIERT)

        self.assertEqual(norm.hoheits_grad, HoheitsGrad.ORDNUNGS_GRAD)
        self.assertEqual(norm.prozedur, HoheitsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.hoheits_weight, 0.45)

    def test_kki_hoheits_manifest_builds_grundlegend_souveraenitaets_norm(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-expansion")
        norm = next(n for n in manifest.normen if n.geltung is HoheitsGeltung.GRUNDLEGEND_PROKLAMIERT)

        self.assertEqual(norm.hoheits_grad, HoheitsGrad.SOUVERAENITAETS_GRAD)
        self.assertEqual(norm.prozedur, HoheitsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_hoheits_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_hoheits_manifest(manifest_id="manifest-226-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_norm_ids, ("manifest-226-signal-stability-lane",))
        self.assertEqual(manifest.proklamiert_norm_ids, ("manifest-226-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_norm_ids, ("manifest-226-signal-expansion-lane",))

    def test_kki_bundes_charta_builds_gesperrt_schutz_norm(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-stability")
        norm = next(n for n in charta.normen if n.geltung is BundesGeltung.GESPERRT)

        self.assertIsInstance(charta, BundesCharta)
        self.assertIsInstance(norm, BundesNorm)
        self.assertEqual(norm.bundes_rang, BundesRang.SCHUTZ_RANG)
        self.assertEqual(norm.prozedur, BundesProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.bundes_tier, 1)

    def test_kki_bundes_charta_builds_verbuergt_ordnungs_norm(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-governance")
        norm = next(n for n in charta.normen if n.geltung is BundesGeltung.VERBUERGT)

        self.assertEqual(norm.bundes_rang, BundesRang.ORDNUNGS_RANG)
        self.assertEqual(norm.prozedur, BundesProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.bundes_weight, 0.45)

    def test_kki_bundes_charta_builds_grundlegend_souveraenitaets_norm(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-expansion")
        norm = next(n for n in charta.normen if n.geltung is BundesGeltung.GRUNDLEGEND_VERBUERGT)

        self.assertEqual(norm.bundes_rang, BundesRang.SOUVERAENITAETS_RANG)
        self.assertEqual(norm.prozedur, BundesProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_bundes_charta_aggregates_charta_signal(self) -> None:
        charta = build_bundes_charta(charta_id="charta-225-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_norm_ids, ("charta-225-signal-stability-lane",))
        self.assertEqual(charta.verbuergt_norm_ids, ("charta-225-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_norm_ids, ("charta-225-signal-expansion-lane",))

    def test_kki_foederal_vertrag_builds_gesperrt_schutz_norm(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-stability")
        norm = next(n for n in vertrag.normen if n.geltung is FoederalGeltung.GESPERRT)

        self.assertIsInstance(vertrag, FoederalVertrag)
        self.assertIsInstance(norm, FoederalNorm)
        self.assertEqual(norm.foederal_typ, FoederalTyp.SCHUTZ_BUND)
        self.assertEqual(norm.prozedur, FoederalProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.foederal_tier, 1)

    def test_kki_foederal_vertrag_builds_foederiert_ordnungs_norm(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-governance")
        norm = next(n for n in vertrag.normen if n.geltung is FoederalGeltung.FOEDERIERT)

        self.assertEqual(norm.foederal_typ, FoederalTyp.ORDNUNGS_BUND)
        self.assertEqual(norm.prozedur, FoederalProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.foederal_weight, 0.45)

    def test_kki_foederal_vertrag_builds_grundlegend_souveraenitaets_norm(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-expansion")
        norm = next(n for n in vertrag.normen if n.geltung is FoederalGeltung.GRUNDLEGEND_FOEDERIERT)

        self.assertEqual(norm.foederal_typ, FoederalTyp.SOUVERAENITAETS_BUND)
        self.assertEqual(norm.prozedur, FoederalProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_foederal_vertrag_aggregates_vertrag_signal(self) -> None:
        vertrag = build_foederal_vertrag(vertrag_id="vertrag-224-signal")

        self.assertEqual(vertrag.vertrag_signal.status, "vertrag-gesperrt")
        self.assertEqual(vertrag.gesperrt_norm_ids, ("vertrag-224-signal-stability-lane",))
        self.assertEqual(vertrag.foederiert_norm_ids, ("vertrag-224-signal-governance-lane",))
        self.assertEqual(vertrag.grundlegend_norm_ids, ("vertrag-224-signal-expansion-lane",))

    def test_kki_unions_akt_builds_gesperrt_schutz_norm(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-stability")
        norm = next(n for n in akt.normen if n.geltung is UnionsGeltung.GESPERRT)

        self.assertIsInstance(akt, UnionsAkt)
        self.assertIsInstance(norm, UnionsNorm)
        self.assertEqual(norm.unions_typ, UnionsTyp.SCHUTZ_UNION)
        self.assertEqual(norm.prozedur, UnionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.unions_tier, 1)

    def test_kki_unions_akt_builds_vereint_ordnungs_norm(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-governance")
        norm = next(n for n in akt.normen if n.geltung is UnionsGeltung.VEREINT)

        self.assertEqual(norm.unions_typ, UnionsTyp.ORDNUNGS_UNION)
        self.assertEqual(norm.prozedur, UnionsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.unions_weight, 0.45)

    def test_kki_unions_akt_builds_grundlegend_souveraenitaets_norm(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-expansion")
        norm = next(n for n in akt.normen if n.geltung is UnionsGeltung.GRUNDLEGEND_VEREINT)

        self.assertEqual(norm.unions_typ, UnionsTyp.SOUVERAENITAETS_UNION)
        self.assertEqual(norm.prozedur, UnionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_unions_akt_aggregates_akt_signal(self) -> None:
        akt = build_unions_akt(akt_id="akt-223-signal")

        self.assertEqual(akt.akt_signal.status, "akt-gesperrt")
        self.assertEqual(akt.gesperrt_norm_ids, ("akt-223-signal-stability-lane",))
        self.assertEqual(akt.vereint_norm_ids, ("akt-223-signal-governance-lane",))
        self.assertEqual(akt.grundlegend_norm_ids, ("akt-223-signal-expansion-lane",))

    def test_kki_rechts_kodex_builds_gesperrt_schutz_norm(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-stability")
        norm = next(n for n in kodex.normen if n.status is KodexStatus.GESPERRT)

        self.assertIsInstance(kodex, RechtsKodex)
        self.assertIsInstance(norm, KodexNorm)
        self.assertEqual(norm.klasse, KodexKlasse.SCHUTZ_KLASSE)
        self.assertEqual(norm.prozedur, KodexProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.kodex_tier, 1)

    def test_kki_rechts_kodex_builds_kodiert_ordnungs_norm(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-governance")
        norm = next(n for n in kodex.normen if n.status is KodexStatus.KODIERT)

        self.assertEqual(norm.klasse, KodexKlasse.ORDNUNGS_KLASSE)
        self.assertEqual(norm.prozedur, KodexProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.kodex_weight, 0.45)

    def test_kki_rechts_kodex_builds_grundlegend_souveraenitaets_norm(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-expansion")
        norm = next(n for n in kodex.normen if n.status is KodexStatus.GRUNDLEGEND_KODIERT)

        self.assertEqual(norm.klasse, KodexKlasse.SOUVERAENITAETS_KLASSE)
        self.assertEqual(norm.prozedur, KodexProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_rechts_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_rechts_kodex(kodex_id="kodex-222-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_norm_ids, ("kodex-222-signal-stability-lane",))
        self.assertEqual(kodex.kodiert_norm_ids, ("kodex-222-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_norm_ids, ("kodex-222-signal-expansion-lane",))

    def test_kki_staats_ordnung_builds_gesperrt_schutz_norm(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-stability")
        norm = next(n for n in ordnung.normen if n.geltung is StaatsGeltung.GESPERRT)

        self.assertIsInstance(ordnung, StaatsOrdnung)
        self.assertIsInstance(norm, StaatsNorm)
        self.assertEqual(norm.ebene, StaatsEbene.SCHUTZ_EBENE)
        self.assertEqual(norm.prozedur, StaatsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(norm.staats_tier, 1)

    def test_kki_staats_ordnung_builds_geordnet_ordnungs_norm(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-governance")
        norm = next(n for n in ordnung.normen if n.geltung is StaatsGeltung.GEORDNET)

        self.assertEqual(norm.ebene, StaatsEbene.ORDNUNGS_EBENE)
        self.assertEqual(norm.prozedur, StaatsProzedur.REGELPROTOKOLL)
        self.assertGreater(norm.staats_weight, 0.45)

    def test_kki_staats_ordnung_builds_grundlegend_souveraenitaets_norm(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-expansion")
        norm = next(n for n in ordnung.normen if n.geltung is StaatsGeltung.GRUNDLEGEND_GEORDNET)

        self.assertEqual(norm.ebene, StaatsEbene.SOUVERAENITAETS_EBENE)
        self.assertEqual(norm.prozedur, StaatsProzedur.PLENARPROTOKOLL)
        self.assertTrue(norm.canonical)

    def test_kki_staats_ordnung_aggregates_staats_signal(self) -> None:
        ordnung = build_staats_ordnung(ordnung_id="ordnung-221-signal")

        self.assertEqual(ordnung.staats_signal.status, "ordnung-gesperrt")
        self.assertEqual(ordnung.gesperrt_norm_ids, ("ordnung-221-signal-stability-lane",))
        self.assertEqual(ordnung.geordnet_norm_ids, ("ordnung-221-signal-governance-lane",))
        self.assertEqual(ordnung.grundlegend_norm_ids, ("ordnung-221-signal-expansion-lane",))

    def test_kki_verfassungs_grundgesetz_builds_gesperrt_schutz_paragraph(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-stability")
        paragraph = next(p for p in grundgesetz.paragraphen if p.geltung is GrundgesetzGeltung.GESPERRT)

        self.assertIsInstance(grundgesetz, VerfassungsGrundgesetz)
        self.assertIsInstance(paragraph, GrundgesetzParagraph)
        self.assertEqual(paragraph.titel, GrundgesetzTitel.SCHUTZ_TITEL)
        self.assertEqual(paragraph.prozedur, GrundgesetzProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(paragraph.grundgesetz_tier, 1)

    def test_kki_verfassungs_grundgesetz_builds_verbindlich_ordnungs_paragraph(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-governance")
        paragraph = next(p for p in grundgesetz.paragraphen if p.geltung is GrundgesetzGeltung.VERBINDLICH)

        self.assertEqual(paragraph.titel, GrundgesetzTitel.ORDNUNGS_TITEL)
        self.assertEqual(paragraph.prozedur, GrundgesetzProzedur.REGELPROTOKOLL)
        self.assertGreater(paragraph.grundgesetz_weight, 0.45)

    def test_kki_verfassungs_grundgesetz_builds_grundgesetzlich_souveraenitaets_paragraph(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-expansion")
        paragraph = next(p for p in grundgesetz.paragraphen if p.geltung is GrundgesetzGeltung.GRUNDGESETZLICH)

        self.assertEqual(paragraph.titel, GrundgesetzTitel.SOUVERAENITAETS_TITEL)
        self.assertEqual(paragraph.prozedur, GrundgesetzProzedur.PLENARPROTOKOLL)
        self.assertTrue(paragraph.canonical)

    def test_kki_verfassungs_grundgesetz_aggregates_grundgesetz_signal(self) -> None:
        grundgesetz = build_verfassungs_grundgesetz(grundgesetz_id="grundgesetz-220-signal")

        self.assertEqual(grundgesetz.grundgesetz_signal.status, "grundgesetz-gesperrt")
        self.assertEqual(grundgesetz.gesperrt_paragraph_ids, ("grundgesetz-220-signal-stability-lane",))
        self.assertEqual(grundgesetz.verbindlich_paragraph_ids, ("grundgesetz-220-signal-governance-lane",))
        self.assertEqual(grundgesetz.grundgesetzlich_paragraph_ids, ("grundgesetz-220-signal-expansion-lane",))

    def test_kki_leitstern_konstitution_builds_gesperrt_schutz_artikel(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-stability")
        artikel = next(a for a in konstitution.artikel if a.rang is KonstitutionsRang.GESPERRT)

        self.assertIsInstance(konstitution, LeitsternKonstitution)
        self.assertIsInstance(artikel, KonstitutionsArtikel)
        self.assertEqual(artikel.ebene, KonstitutionsEbene.SCHUTZ_EBENE)
        self.assertEqual(artikel.prozedur, KonstitutionsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(artikel.konstitutions_tier, 1)

    def test_kki_leitstern_konstitution_builds_konstituiert_ordnungs_artikel(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-governance")
        artikel = next(a for a in konstitution.artikel if a.rang is KonstitutionsRang.KONSTITUIERT)

        self.assertEqual(artikel.ebene, KonstitutionsEbene.ORDNUNGS_EBENE)
        self.assertEqual(artikel.prozedur, KonstitutionsProzedur.REGELPROTOKOLL)
        self.assertGreater(artikel.konstitutions_weight, 0.45)

    def test_kki_leitstern_konstitution_builds_grundlegend_souveraenitaets_artikel(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-expansion")
        artikel = next(a for a in konstitution.artikel if a.rang is KonstitutionsRang.GRUNDLEGEND_KONSTITUIERT)

        self.assertEqual(artikel.ebene, KonstitutionsEbene.SOUVERAENITAETS_EBENE)
        self.assertEqual(artikel.prozedur, KonstitutionsProzedur.PLENARPROTOKOLL)
        self.assertTrue(artikel.canonical)

    def test_kki_leitstern_konstitution_aggregates_konstitutions_signal(self) -> None:
        konstitution = build_leitstern_konstitution(konstitutions_id="konstitution-219-signal")

        self.assertEqual(konstitution.konstitutions_signal.status, "konstitution-gesperrt")
        self.assertEqual(konstitution.gesperrt_artikel_ids, ("konstitution-219-signal-stability-lane",))
        self.assertEqual(konstitution.konstituiert_artikel_ids, ("konstitution-219-signal-governance-lane",))
        self.assertEqual(konstitution.grundlegend_artikel_ids, ("konstitution-219-signal-expansion-lane",))

    def test_kki_zweck_manifest_builds_gesperrt_schutz_klausel(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-stability")
        klausel = next(k for k in manifest.klauseln if k.geltung is ManifestGeltung.GESPERRT)

        self.assertIsInstance(manifest, ZweckManifest)
        self.assertIsInstance(klausel, ZweckKlausel)
        self.assertEqual(klausel.dimension, ZweckDimension.SCHUTZ_DIMENSION)
        self.assertEqual(klausel.prozedur, ManifestProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(klausel.manifest_tier, 1)

    def test_kki_zweck_manifest_builds_proklamiert_ordnungs_klausel(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-governance")
        klausel = next(k for k in manifest.klauseln if k.geltung is ManifestGeltung.PROKLAMIERT)

        self.assertEqual(klausel.dimension, ZweckDimension.ORDNUNGS_DIMENSION)
        self.assertEqual(klausel.prozedur, ManifestProzedur.REGELPROTOKOLL)
        self.assertGreater(klausel.manifest_weight, 0.45)

    def test_kki_zweck_manifest_builds_grundlegend_souveraenitaets_klausel(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-expansion")
        klausel = next(k for k in manifest.klauseln if k.geltung is ManifestGeltung.GRUNDLEGEND_PROKLAMIERT)

        self.assertEqual(klausel.dimension, ZweckDimension.SOUVERAENITAETS_DIMENSION)
        self.assertEqual(klausel.prozedur, ManifestProzedur.PLENARPROTOKOLL)
        self.assertTrue(klausel.canonical)

    def test_kki_zweck_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_zweck_manifest(manifest_id="manifest-218-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_klausel_ids, ("manifest-218-signal-stability-lane",))
        self.assertEqual(manifest.proklamiert_klausel_ids, ("manifest-218-signal-governance-lane",))
        self.assertEqual(manifest.grundlegend_klausel_ids, ("manifest-218-signal-expansion-lane",))

    def test_kki_missions_verfassung_builds_gesperrt_schutz_artikel(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-stability")
        artikel = next(a for a in verfassung.artikel if a.status is VerfassungsStatus.GESPERRT)

        self.assertIsInstance(verfassung, MissionsVerfassung)
        self.assertIsInstance(artikel, MissionsArtikel)
        self.assertEqual(artikel.rang, MissionsRang.SCHUTZ_RANG)
        self.assertEqual(artikel.prozedur, VerfassungsProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(artikel.verfassungs_tier, 1)

    def test_kki_missions_verfassung_builds_ratifiziert_ordnungs_artikel(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-governance")
        artikel = next(a for a in verfassung.artikel if a.status is VerfassungsStatus.RATIFIZIERT)

        self.assertEqual(artikel.rang, MissionsRang.ORDNUNGS_RANG)
        self.assertEqual(artikel.prozedur, VerfassungsProzedur.REGELPROTOKOLL)
        self.assertGreater(artikel.verfassungs_weight, 0.45)

    def test_kki_missions_verfassung_builds_grundlegend_souveraenitaets_artikel(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-expansion")
        artikel = next(a for a in verfassung.artikel if a.status is VerfassungsStatus.GRUNDLEGEND_RATIFIZIERT)

        self.assertEqual(artikel.rang, MissionsRang.SOUVERAENITAETS_RANG)
        self.assertEqual(artikel.prozedur, VerfassungsProzedur.PLENARPROTOKOLL)
        self.assertTrue(artikel.canonical)

    def test_kki_missions_verfassung_aggregates_verfassungs_signal(self) -> None:
        verfassung = build_missions_verfassung(verfassungs_id="verfassung-217-signal")

        self.assertEqual(verfassung.verfassungs_signal.status, "verfassung-gesperrt")
        self.assertEqual(verfassung.gesperrt_artikel_ids, ("verfassung-217-signal-stability-lane",))
        self.assertEqual(verfassung.ratifiziert_artikel_ids, ("verfassung-217-signal-governance-lane",))
        self.assertEqual(verfassung.grundlegend_artikel_ids, ("verfassung-217-signal-expansion-lane",))

    def test_kki_leitbild_konvent_builds_gesperrt_schutz_resolution(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-stability")
        resolution = next(r for r in konvent.resolutionen if r.beschluss is KonventBeschluss.GESPERRT)

        self.assertIsInstance(konvent, LeitbildKonvent)
        self.assertIsInstance(resolution, LeitbildResolution)
        self.assertEqual(resolution.ausrichtung, LeitbildAusrichtung.SCHUTZ_AUSRICHTUNG)
        self.assertEqual(resolution.prozedur, KonventProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(resolution.konvent_tier, 1)

    def test_kki_leitbild_konvent_builds_beschlossen_ordnungs_resolution(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-governance")
        resolution = next(r for r in konvent.resolutionen if r.beschluss is KonventBeschluss.BESCHLOSSEN)

        self.assertEqual(resolution.ausrichtung, LeitbildAusrichtung.ORDNUNGS_AUSRICHTUNG)
        self.assertEqual(resolution.prozedur, KonventProzedur.REGELPROTOKOLL)
        self.assertGreater(resolution.konvent_weight, 0.45)

    def test_kki_leitbild_konvent_builds_grundlegend_souveraenitaets_resolution(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-expansion")
        resolution = next(r for r in konvent.resolutionen if r.beschluss is KonventBeschluss.GRUNDLEGEND_BESCHLOSSEN)

        self.assertEqual(resolution.ausrichtung, LeitbildAusrichtung.SOUVERAENITAETS_AUSRICHTUNG)
        self.assertEqual(resolution.prozedur, KonventProzedur.PLENARPROTOKOLL)
        self.assertTrue(resolution.canonical)

    def test_kki_leitbild_konvent_aggregates_konvent_signal(self) -> None:
        konvent = build_leitbild_konvent(konvent_id="konvent-216-signal")

        self.assertEqual(konvent.konvent_signal.status, "konvent-gesperrt")
        self.assertEqual(konvent.gesperrt_resolution_ids, ("konvent-216-signal-stability-lane",))
        self.assertEqual(konvent.beschlossen_resolution_ids, ("konvent-216-signal-governance-lane",))
        self.assertEqual(konvent.grundlegend_resolution_ids, ("konvent-216-signal-expansion-lane",))

    def test_kki_werte_charta_builds_gesperrt_schutz_artikel(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-stability")
        artikel = next(a for a in charta.artikel if a.status is WerteStatus.GESPERRT)

        self.assertIsInstance(charta, WerteCharta)
        self.assertIsInstance(artikel, WerteArtikel)
        self.assertEqual(artikel.typ, WerteTyp.SCHUTZ_WERT)
        self.assertEqual(artikel.prozedur, WerteProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(artikel.charta_tier, 1)

    def test_kki_werte_charta_builds_verankert_ordnungs_artikel(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-governance")
        artikel = next(a for a in charta.artikel if a.status is WerteStatus.VERANKERT)

        self.assertEqual(artikel.typ, WerteTyp.ORDNUNGS_WERT)
        self.assertEqual(artikel.prozedur, WerteProzedur.REGELPROTOKOLL)
        self.assertGreater(artikel.charta_weight, 0.45)

    def test_kki_werte_charta_builds_grundlegend_souveraenitaets_artikel(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-expansion")
        artikel = next(a for a in charta.artikel if a.status is WerteStatus.GRUNDLEGEND_VERANKERT)

        self.assertEqual(artikel.typ, WerteTyp.SOUVERAENITAETS_WERT)
        self.assertEqual(artikel.prozedur, WerteProzedur.PLENARPROTOKOLL)
        self.assertTrue(artikel.canonical)

    def test_kki_werte_charta_aggregates_charta_signal(self) -> None:
        charta = build_werte_charta(charta_id="charta-215-signal")

        self.assertEqual(charta.charta_signal.status, "charta-gesperrt")
        self.assertEqual(charta.gesperrt_artikel_ids, ("charta-215-signal-stability-lane",))
        self.assertEqual(charta.verankert_artikel_ids, ("charta-215-signal-governance-lane",))
        self.assertEqual(charta.grundlegend_artikel_ids, ("charta-215-signal-expansion-lane",))

    def test_kki_prinzipien_kodex_builds_gesperrt_schutz_satz(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-stability")
        satz = next(s for s in kodex.saetze if s.status is PrinzipienStatus.GESPERRT)

        self.assertIsInstance(kodex, PrinzipienKodex)
        self.assertIsInstance(satz, PrinzipienSatz)
        self.assertEqual(satz.klasse, PrinzipienKlasse.SCHUTZ_KLASSE)
        self.assertEqual(satz.prozedur, PrinzipienProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(satz.kodex_tier, 1)

    def test_kki_prinzipien_kodex_builds_kodifiziert_ordnungs_satz(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-governance")
        satz = next(s for s in kodex.saetze if s.status is PrinzipienStatus.KODIFIZIERT)

        self.assertEqual(satz.klasse, PrinzipienKlasse.ORDNUNGS_KLASSE)
        self.assertEqual(satz.prozedur, PrinzipienProzedur.REGELPROTOKOLL)
        self.assertGreater(satz.kodex_weight, 0.45)

    def test_kki_prinzipien_kodex_builds_grundlegend_souveraenitaets_satz(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-expansion")
        satz = next(s for s in kodex.saetze if s.status is PrinzipienStatus.GRUNDLEGEND_KODIFIZIERT)

        self.assertEqual(satz.klasse, PrinzipienKlasse.SOUVERAENITAETS_KLASSE)
        self.assertEqual(satz.prozedur, PrinzipienProzedur.PLENARPROTOKOLL)
        self.assertTrue(satz.canonical)

    def test_kki_prinzipien_kodex_aggregates_kodex_signal(self) -> None:
        kodex = build_prinzipien_kodex(kodex_id="kodex-214-signal")

        self.assertEqual(kodex.kodex_signal.status, "kodex-gesperrt")
        self.assertEqual(kodex.gesperrt_satz_ids, ("kodex-214-signal-stability-lane",))
        self.assertEqual(kodex.kodifiziert_satz_ids, ("kodex-214-signal-governance-lane",))
        self.assertEqual(kodex.grundlegend_satz_ids, ("kodex-214-signal-expansion-lane",))

    def test_kki_grundsatz_register_builds_gesperrt_schutz_eintrag(self) -> None:
        register = build_grundsatz_register(register_id="register-213-stability")
        eintrag = next(e for e in register.eintraege if e.status is RegisterStatus.GESPERRT)

        self.assertIsInstance(register, GrundsatzRegister)
        self.assertIsInstance(eintrag, RegisterEintrag)
        self.assertEqual(eintrag.kategorie, RegisterKategorie.SCHUTZ_KATEGORIE)
        self.assertEqual(eintrag.prozedur, RegisterProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(eintrag.registry_tier, 1)

    def test_kki_grundsatz_register_builds_eingetragen_ordnungs_eintrag(self) -> None:
        register = build_grundsatz_register(register_id="register-213-governance")
        eintrag = next(e for e in register.eintraege if e.status is RegisterStatus.EINGETRAGEN)

        self.assertEqual(eintrag.kategorie, RegisterKategorie.ORDNUNGS_KATEGORIE)
        self.assertEqual(eintrag.prozedur, RegisterProzedur.REGELPROTOKOLL)
        self.assertGreater(eintrag.register_weight, 0.45)

    def test_kki_grundsatz_register_builds_grundlegend_souveraenitaets_eintrag(self) -> None:
        register = build_grundsatz_register(register_id="register-213-expansion")
        eintrag = next(e for e in register.eintraege if e.status is RegisterStatus.GRUNDLEGEND_EINGETRAGEN)

        self.assertEqual(eintrag.kategorie, RegisterKategorie.SOUVERAENITAETS_KATEGORIE)
        self.assertEqual(eintrag.prozedur, RegisterProzedur.PLENARPROTOKOLL)
        self.assertTrue(eintrag.canonical)

    def test_kki_grundsatz_register_aggregates_register_signal(self) -> None:
        register = build_grundsatz_register(register_id="register-213-signal")

        self.assertEqual(register.register_signal.status, "register-gesperrt")
        self.assertEqual(register.gesperrt_eintrag_ids, ("register-213-signal-stability-lane",))
        self.assertEqual(register.eingetragen_eintrag_ids, ("register-213-signal-governance-lane",))
        self.assertEqual(register.grundlegend_eintrag_ids, ("register-213-signal-expansion-lane",))

    def test_kki_rechts_fundament_builds_gesperrt_schutz_pfeiler(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-stability")
        pfeiler = next(p for p in fundament.pfeiler if p.kraft is FundamentKraft.GESPERRT)

        self.assertIsInstance(fundament, RechtsFundament)
        self.assertIsInstance(pfeiler, FundamentPfeiler)
        self.assertEqual(pfeiler.saeule, FundamentSaeule.SCHUTZ_SAEULE)
        self.assertEqual(pfeiler.verfahren, FundamentVerfahren.NOTVERFAHREN)
        self.assertGreaterEqual(pfeiler.foundation_depth, 1)

    def test_kki_rechts_fundament_builds_fundiert_ordnungs_pfeiler(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-governance")
        pfeiler = next(p for p in fundament.pfeiler if p.kraft is FundamentKraft.FUNDIERT)

        self.assertEqual(pfeiler.saeule, FundamentSaeule.ORDNUNGS_SAEULE)
        self.assertEqual(pfeiler.verfahren, FundamentVerfahren.REGELVERFAHREN)
        self.assertGreater(pfeiler.fundament_weight, 0.45)

    def test_kki_rechts_fundament_builds_tragendes_recht_souveraenitaets_pfeiler(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-expansion")
        pfeiler = next(p for p in fundament.pfeiler if p.kraft is FundamentKraft.TRAGENDES_RECHT)

        self.assertEqual(pfeiler.saeule, FundamentSaeule.SOUVERAENITAETS_SAEULE)
        self.assertEqual(pfeiler.verfahren, FundamentVerfahren.PLENARVERFAHREN)
        self.assertTrue(pfeiler.load_bearing)

    def test_kki_rechts_fundament_aggregates_fundament_signal(self) -> None:
        fundament = build_rechts_fundament(fundament_id="fundament-212-signal")

        self.assertEqual(fundament.fundament_signal.status, "fundament-gesperrt")
        self.assertEqual(fundament.gesperrt_pfeiler_ids, ("fundament-212-signal-stability-lane",))
        self.assertEqual(fundament.fundiert_pfeiler_ids, ("fundament-212-signal-governance-lane",))
        self.assertEqual(fundament.tragendes_recht_pfeiler_ids, ("fundament-212-signal-expansion-lane",))

    def test_kki_autoritaets_dekret_builds_gesperrt_schutz_klausel(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-stability")
        klausel = next(k for k in dekret.klauseln if k.geltung is DekretGeltung.GESPERRT)

        self.assertIsInstance(dekret, AutoritaetsDekret)
        self.assertIsInstance(klausel, DekretKlausel)
        self.assertEqual(klausel.sektion, DekretSektion.SCHUTZ_SEKTION)
        self.assertEqual(klausel.prozedur, DekretProzedur.NOTPROZEDUR)
        self.assertGreaterEqual(klausel.decree_order, 1)

    def test_kki_autoritaets_dekret_builds_verordnet_ordnungs_klausel(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-governance")
        klausel = next(k for k in dekret.klauseln if k.geltung is DekretGeltung.VERORDNET)

        self.assertEqual(klausel.sektion, DekretSektion.ORDNUNGS_SEKTION)
        self.assertEqual(klausel.prozedur, DekretProzedur.REGELPROZEDUR)
        self.assertGreater(klausel.dekret_weight, 0.45)

    def test_kki_autoritaets_dekret_builds_autoritaetsrecht_souveraenitaets_klausel(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-expansion")
        klausel = next(k for k in dekret.klauseln if k.geltung is DekretGeltung.AUTORITAETSRECHT)

        self.assertEqual(klausel.sektion, DekretSektion.SOUVERAENITAETS_SEKTION)
        self.assertEqual(klausel.prozedur, DekretProzedur.PLENARPROZEDUR)
        self.assertTrue(klausel.decreed)

    def test_kki_autoritaets_dekret_aggregates_dekret_signal(self) -> None:
        dekret = build_autoritaets_dekret(dekret_id="dekret-211-signal")

        self.assertEqual(dekret.dekret_signal.status, "dekret-gesperrt")
        self.assertEqual(dekret.gesperrt_klausel_ids, ("dekret-211-signal-stability-lane",))
        self.assertEqual(dekret.verordnet_klausel_ids, ("dekret-211-signal-governance-lane",))
        self.assertEqual(dekret.autoritaetsrecht_klausel_ids, ("dekret-211-signal-expansion-lane",))

    def test_kki_leitordnung_builds_blockiert_schutz_norm(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-stability")
        norm = next(n for n in ordnung.normen if n.kraft is OrdnungsKraft.BLOCKIERT)

        self.assertIsInstance(ordnung, Leitordnung)
        self.assertIsInstance(norm, OrdnungsNorm)
        self.assertEqual(norm.rang, OrdnungsRang.SCHUTZ_RANG)
        self.assertEqual(norm.typ, OrdnungsTyp.NOTORDNUNG)
        self.assertGreaterEqual(norm.authority_level, 1)

    def test_kki_leitordnung_builds_wirksam_ordnungs_norm(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-governance")
        norm = next(n for n in ordnung.normen if n.kraft is OrdnungsKraft.WIRKSAM)

        self.assertEqual(norm.rang, OrdnungsRang.ORDNUNGS_RANG)
        self.assertEqual(norm.typ, OrdnungsTyp.REGELORDNUNG)
        self.assertGreater(norm.ordnungs_weight, 0.45)

    def test_kki_leitordnung_builds_leitend_souveraenitaets_norm(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-expansion")
        norm = next(n for n in ordnung.normen if n.kraft is OrdnungsKraft.LEITEND)

        self.assertEqual(norm.rang, OrdnungsRang.SOUVERAENITAETS_RANG)
        self.assertEqual(norm.typ, OrdnungsTyp.PLENARORDNUNG)
        self.assertTrue(norm.supreme)

    def test_kki_leitordnung_aggregates_ordnungs_signal(self) -> None:
        ordnung = build_leitordnung(ordnung_id="ordnung-210-signal")

        self.assertEqual(ordnung.ordnungs_signal.status, "ordnung-blockiert")
        self.assertEqual(ordnung.blockiert_norm_ids, ("ordnung-210-signal-stability-lane",))
        self.assertEqual(ordnung.wirksam_norm_ids, ("ordnung-210-signal-governance-lane",))
        self.assertEqual(ordnung.leitend_norm_ids, ("ordnung-210-signal-expansion-lane",))

    def test_kki_ordnungs_manifest_builds_gesperrt_schutz_abschnitt(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-stability")
        abschnitt = next(a for a in manifest.abschnitte if a.geltung is ManifestGeltung.GESPERRT)

        self.assertIsInstance(manifest, OrdnungsManifest)
        self.assertIsInstance(abschnitt, ManifestAbschnitt)
        self.assertEqual(abschnitt.kapitel, ManifestKapitel.SCHUTZ_KAPITEL)
        self.assertEqual(abschnitt.verfahren, ManifestVerfahren.NOTVERFAHREN)
        self.assertGreaterEqual(abschnitt.proclamation_rank, 1)

    def test_kki_ordnungs_manifest_builds_proklamiert_ordnungs_abschnitt(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-governance")
        abschnitt = next(a for a in manifest.abschnitte if a.geltung is ManifestGeltung.PROKLAMIERT)

        self.assertEqual(abschnitt.kapitel, ManifestKapitel.ORDNUNGS_KAPITEL)
        self.assertEqual(abschnitt.verfahren, ManifestVerfahren.REGELVERFAHREN)
        self.assertGreater(abschnitt.manifest_weight, 0.45)

    def test_kki_ordnungs_manifest_builds_hoheitsrecht_souveraenitaets_abschnitt(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-expansion")
        abschnitt = next(a for a in manifest.abschnitte if a.geltung is ManifestGeltung.HOHEITSRECHT)

        self.assertEqual(abschnitt.kapitel, ManifestKapitel.SOUVERAENITAETS_KAPITEL)
        self.assertEqual(abschnitt.verfahren, ManifestVerfahren.PLENARVERFAHREN)
        self.assertTrue(abschnitt.promulgated)

    def test_kki_ordnungs_manifest_aggregates_manifest_signal(self) -> None:
        manifest = build_ordnungs_manifest(manifest_id="manifest-209-signal")

        self.assertEqual(manifest.manifest_signal.status, "manifest-gesperrt")
        self.assertEqual(manifest.gesperrt_abschnitt_ids, ("manifest-209-signal-stability-lane",))
        self.assertEqual(manifest.proklamiert_abschnitt_ids, ("manifest-209-signal-governance-lane",))
        self.assertEqual(manifest.hoheitsrecht_abschnitt_ids, ("manifest-209-signal-expansion-lane",))

    def test_kki_souveraenitaets_akt_builds_suspendiert_schutz_klausel(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-stability")
        klausel = next(k for k in akt.klauseln if k.akt_status is AktStatus.SUSPENDIERT)

        self.assertIsInstance(akt, SouveraenitaetsAkt)
        self.assertIsInstance(klausel, AktKlausel)
        self.assertEqual(klausel.sektion, AktSektion.SCHUTZ_SEKTION)
        self.assertEqual(klausel.prozedur, AktProzedur.EILVERFAHREN)
        self.assertGreaterEqual(klausel.enactment_tier, 1)

    def test_kki_souveraenitaets_akt_builds_ratifiziert_ordnungs_klausel(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-governance")
        klausel = next(k for k in akt.klauseln if k.akt_status is AktStatus.RATIFIZIERT)

        self.assertEqual(klausel.sektion, AktSektion.ORDNUNGS_SEKTION)
        self.assertEqual(klausel.prozedur, AktProzedur.STANDARDVERFAHREN)
        self.assertGreater(klausel.sovereignty_weight, 0.45)

    def test_kki_souveraenitaets_akt_builds_souveraen_souveraenitaets_klausel(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-expansion")
        klausel = next(k for k in akt.klauseln if k.akt_status is AktStatus.SOUVERAEN)

        self.assertEqual(klausel.sektion, AktSektion.SOUVERAENITAETS_SEKTION)
        self.assertEqual(klausel.prozedur, AktProzedur.VOLLVERFAHREN)
        self.assertTrue(klausel.operative)

    def test_kki_souveraenitaets_akt_aggregates_akt_signal(self) -> None:
        akt = build_souveraenitaets_akt(akt_id="akt-208-signal")

        self.assertEqual(akt.akt_signal.status, "akt-suspendiert")
        self.assertEqual(akt.suspendiert_klausel_ids, ("akt-208-signal-stability-lane",))
        self.assertEqual(akt.ratifiziert_klausel_ids, ("akt-208-signal-governance-lane",))
        self.assertEqual(akt.souveraen_klausel_ids, ("akt-208-signal-expansion-lane",))

    def test_kki_grundrechts_charta_builds_ausgesetzt_schutz_artikel(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-stability")
        artikel = next(a for a in charta.artikel if a.geltung is ChartaGeltung.AUSGESETZT)

        self.assertIsInstance(charta, GrundrechtsCharta)
        self.assertIsInstance(artikel, ChartaArtikel)
        self.assertEqual(artikel.kapitel, ChartaKapitel.SCHUTZ_KAPITEL)
        self.assertEqual(artikel.verfahren, ChartaVerfahren.DRINGLICHE_EINTRAGUNG)
        self.assertGreaterEqual(artikel.ratification_depth, 1)

    def test_kki_grundrechts_charta_builds_geltend_ordnungs_artikel(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-governance")
        artikel = next(a for a in charta.artikel if a.geltung is ChartaGeltung.GELTEND)

        self.assertEqual(artikel.kapitel, ChartaKapitel.ORDNUNGS_KAPITEL)
        self.assertEqual(artikel.verfahren, ChartaVerfahren.ORDENTLICHE_EINTRAGUNG)
        self.assertGreater(artikel.codex_weight, 0.45)

    def test_kki_grundrechts_charta_builds_grundrecht_souveraenitaets_artikel(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-expansion")
        artikel = next(a for a in charta.artikel if a.geltung is ChartaGeltung.GRUNDRECHT)

        self.assertEqual(artikel.kapitel, ChartaKapitel.SOUVERAENITAETS_KAPITEL)
        self.assertEqual(artikel.verfahren, ChartaVerfahren.PLENARE_EINTRAGUNG)
        self.assertTrue(artikel.enforceable)

    def test_kki_grundrechts_charta_aggregates_charta_signal(self) -> None:
        charta = build_grundrechts_charta(charta_id="charta-207-signal")

        self.assertEqual(charta.charta_signal.status, "charta-ausgesetzt")
        self.assertEqual(charta.ausgesetzt_artikel_ids, ("charta-207-signal-stability-lane",))
        self.assertEqual(charta.geltend_artikel_ids, ("charta-207-signal-governance-lane",))
        self.assertEqual(charta.grundrecht_artikel_ids, ("charta-207-signal-expansion-lane",))

    def test_kki_verfassungs_senat_builds_ungueltig_schutz_mandat(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-stability")
        mandat = next(m for m in senat.mandate if m.beschluss is SenatsBeschluss.UNGUELTIG)

        self.assertIsInstance(senat, VerfassungsSenat)
        self.assertIsInstance(mandat, SenatsMandat)
        self.assertEqual(mandat.fraktion, SenatsFraktion.SCHUTZ_FRAKTION)
        self.assertEqual(mandat.sitzung, SenatsSitzung.DRINGLICH_SITZUNG)
        self.assertGreaterEqual(mandat.deliberation_quorum, 1)

    def test_kki_verfassungs_senat_builds_wirksam_ordnungs_mandat(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-governance")
        mandat = next(m for m in senat.mandate if m.beschluss is SenatsBeschluss.WIRKSAM)

        self.assertEqual(mandat.fraktion, SenatsFraktion.ORDNUNGS_FRAKTION)
        self.assertEqual(mandat.sitzung, SenatsSitzung.ORDENTLICHE_SITZUNG)
        self.assertGreater(mandat.resolution_weight, 0.45)

    def test_kki_verfassungs_senat_builds_grundlegend_souveraenitaets_mandat(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-expansion")
        mandat = next(m for m in senat.mandate if m.beschluss is SenatsBeschluss.GRUNDLEGEND)

        self.assertEqual(mandat.fraktion, SenatsFraktion.SOUVERAENITAETS_FRAKTION)
        self.assertEqual(mandat.sitzung, SenatsSitzung.PLENARSITZUNG)
        self.assertTrue(mandat.binding)

    def test_kki_verfassungs_senat_aggregates_senat_signal(self) -> None:
        senat = build_verfassungs_senat(senat_id="senat-206-signal")

        self.assertEqual(senat.senat_signal.status, "senat-ungueltig")
        self.assertEqual(senat.ungueltig_mandat_ids, ("senat-206-signal-stability-lane",))
        self.assertEqual(senat.wirksam_mandat_ids, ("senat-206-signal-governance-lane",))
        self.assertEqual(senat.grundlegend_mandat_ids, ("senat-206-signal-expansion-lane",))

    def test_kki_normen_tribunal_builds_abgewiesen_schutz_fall(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-stability")
        fall = next(f for f in tribunal.faelle if f.urteil is TribunalUrteil.ABGEWIESEN)

        self.assertIsInstance(tribunal, NormenTribunal)
        self.assertIsInstance(fall, TribunalFall)
        self.assertEqual(fall.kammer, TribunalKammer.SCHUTZ_KAMMER)
        self.assertEqual(fall.verfahren, TribunalVerfahren.SUMMARISCHES_VERFAHREN)
        self.assertGreaterEqual(fall.deliberation_rounds, 1)

    def test_kki_normen_tribunal_builds_bestaetigt_ordnungs_fall(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-governance")
        fall = next(f for f in tribunal.faelle if f.urteil is TribunalUrteil.BESTAETIGT)

        self.assertEqual(fall.kammer, TribunalKammer.ORDNUNGS_KAMMER)
        self.assertEqual(fall.verfahren, TribunalVerfahren.ORDENTLICHES_VERFAHREN)
        self.assertGreater(fall.verdict_weight, 0.45)

    def test_kki_normen_tribunal_builds_verfassungsgebunden_souveraenitaets_fall(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-expansion")
        fall = next(f for f in tribunal.faelle if f.urteil is TribunalUrteil.VERFASSUNGSGEBUNDEN)

        self.assertEqual(fall.kammer, TribunalKammer.SOUVERAENITAETS_KAMMER)
        self.assertEqual(fall.verfahren, TribunalVerfahren.VERFASSUNGSVERFAHREN)
        self.assertTrue(fall.release_ready)

    def test_kki_normen_tribunal_aggregates_tribunal_signal(self) -> None:
        tribunal = build_normen_tribunal(tribunal_id="tribunal-205-signal")

        self.assertEqual(tribunal.tribunal_signal.status, "tribunal-abgewiesen")
        self.assertEqual(tribunal.abgewiesen_fall_ids, ("tribunal-205-signal-stability-lane",))
        self.assertEqual(tribunal.bestaetigt_fall_ids, ("tribunal-205-signal-governance-lane",))
        self.assertEqual(tribunal.verfassungsgebunden_fall_ids, ("tribunal-205-signal-expansion-lane",))

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
