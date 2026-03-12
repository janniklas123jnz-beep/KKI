"""Gemeinsame Runtime-Helfer fuer KKI-Simulationen."""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any, Mapping

DEFAULT_SEED = 42


def _env_flag(name: str) -> bool:
    value = os.getenv(name, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def is_test_mode() -> bool:
    return _env_flag("KKI_TEST_MODE")


def initialize_runtime(np_module: Any | None = None) -> int:
    """Initialisiere Seed fuer `random` und optional `numpy.random`."""
    raw_seed = os.getenv("KKI_SEED")
    if raw_seed is None:
        seed = DEFAULT_SEED
        source = "default"
    else:
        seed = int(raw_seed)
        source = "KKI_SEED"

    random.seed(seed)
    if np_module is not None:
        np_module.random.seed(seed)

    print(f"Seed: {seed} ({source})")
    return seed


def configure_simulation(
    config: Mapping[str, int],
    *,
    np_module: Any | None = None,
    plt_module: Any | None = None,
) -> tuple[dict[str, int], int]:
    """Initialisiere eine Simulation mit gemeinsamen Runtime-Konventionen."""
    if plt_module is not None:
        configure_matplotlib(plt_module)

    updated_config = apply_test_overrides(config)
    seed = initialize_runtime(np_module)
    return updated_config, seed


def apply_test_overrides(values: Mapping[str, int]) -> dict[str, int]:
    """Verkuerze Laufzeiten im Testmodus, ohne die Logik komplett zu veraendern."""
    updated = dict(values)
    if not is_test_mode():
        return updated

    round_cap = int(os.getenv("KKI_TEST_ROUNDS", "6"))
    interaction_cap = int(os.getenv("KKI_TEST_INTERACTIONS", "8"))
    invasion_round_cap = int(os.getenv("KKI_TEST_INVASION_ROUND", "3"))

    for key, value in values.items():
        if key == "INVASION_RUNDE":
            updated[key] = min(value, invasion_round_cap)
        elif "RUNDEN" in key:
            updated[key] = min(value, round_cap)
        elif "INTERAKTIONEN_PRO_RUNDE" in key:
            updated[key] = min(value, interaction_cap)

    return updated


def configure_matplotlib(plt_module: Any) -> None:
    """Aktiviere im Testmodus ein headless Backend."""
    if is_test_mode():
        plt_module.switch_backend("Agg")


def save_and_maybe_show(plt_module: Any, filename: str, **savefig_kwargs: Any) -> Path:
    """Speichere einen Plot und zeige ihn ausserhalb des Testmodus an."""
    output_dir = os.getenv("KKI_OUTPUT_DIR")
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        target = output_path / filename
    else:
        target = Path(filename)

    plt_module.savefig(target, **savefig_kwargs)
    print(f"\nGraph gespeichert: {target}")

    backend = str(plt_module.get_backend()).lower()
    if not is_test_mode() and "agg" not in backend:
        plt_module.show()

    plt_module.close()
    return target
