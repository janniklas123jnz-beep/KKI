"""KKI build-phase foundation package."""

from .runtime_dna import (
    RuntimeDNA,
    RuntimeHooks,
    RuntimeIdentity,
    RuntimeStage,
    RuntimeThresholds,
    runtime_dna_for_profile,
    runtime_dna_from_env,
)

__all__ = [
    "RuntimeDNA",
    "RuntimeHooks",
    "RuntimeIdentity",
    "RuntimeStage",
    "RuntimeThresholds",
    "runtime_dna_for_profile",
    "runtime_dna_from_env",
]
