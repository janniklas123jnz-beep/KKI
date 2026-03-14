"""KKI build-phase foundation package."""

from .module_boundaries import (
    ModuleBoundary,
    ModuleBoundaryName,
    module_boundaries,
    module_boundary,
    module_dependency_graph,
)
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
    "ModuleBoundary",
    "ModuleBoundaryName",
    "RuntimeDNA",
    "RuntimeHooks",
    "RuntimeIdentity",
    "RuntimeStage",
    "RuntimeThresholds",
    "module_boundaries",
    "module_boundary",
    "module_dependency_graph",
    "runtime_dna_for_profile",
    "runtime_dna_from_env",
]
