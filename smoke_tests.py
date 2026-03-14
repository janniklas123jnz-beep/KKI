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
    ControlArtifact,
    CoreState,
    DelegationGrant,
    DeliveryGuarantee,
    DeliveryMode,
    EvidenceRecord,
    EventEnvelope,
    IdentityKind,
    LoadedControlPlane,
    MessageEnvelope,
    MessageKind,
    ModuleBoundaryName,
    OperatingMode,
    PersistenceRecord,
    ProtocolContext,
    RoleName,
    RuntimeStage,
    RuntimeThresholds,
    TransferEnvelope,
    TrustLevel,
    ValidationStep,
    authorize_action,
    authorize_artifact,
    command_message,
    core_state_for_runtime,
    event_message,
    evidence_message,
    load_control_plane,
    module_boundaries,
    module_dependency_graph,
    protocol_context,
    runtime_dna_for_profile,
    runtime_dna_from_env,
    transfer_message,
    transfer_envelope_for_state,
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
