"""KKI build-phase foundation package."""

from .data_models import (
    CoreState,
    EvidenceRecord,
    PersistenceRecord,
    TransferEnvelope,
    core_state_for_runtime,
    transfer_envelope_for_state,
)
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
    "CoreState",
    "EvidenceRecord",
    "ModuleBoundary",
    "ModuleBoundaryName",
    "PersistenceRecord",
    "RuntimeDNA",
    "RuntimeHooks",
    "RuntimeIdentity",
    "RuntimeStage",
    "RuntimeThresholds",
    "TransferEnvelope",
    "core_state_for_runtime",
    "module_boundaries",
    "module_boundary",
    "module_dependency_graph",
    "runtime_dna_for_profile",
    "runtime_dna_from_env",
    "transfer_envelope_for_state",
]
