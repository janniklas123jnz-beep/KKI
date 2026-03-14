"""Leichte Smoke-Tests fuer zentrale KKI-Skripte."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
