"""Module boundary map for the build-phase package structure."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModuleBoundaryName(str, Enum):
    """Canonical module boundary names for the build-phase package."""

    ORCHESTRATION = "orchestration"
    TELEMETRY = "telemetry"
    SECURITY = "security"
    SHADOW = "shadow"
    ROLLOUT = "rollout"
    RECOVERY = "recovery"
    GOVERNANCE = "governance"


@dataclass(frozen=True)
class ModuleBoundary:
    """Repository-facing description of a build-phase module boundary."""

    name: ModuleBoundaryName
    package: str
    summary: str
    depends_on: tuple[ModuleBoundaryName, ...]
    runtime_hooks: tuple[str, ...]
    extension_contracts: tuple[str, ...]


_BOUNDARIES: dict[ModuleBoundaryName, ModuleBoundary] = {
    ModuleBoundaryName.ORCHESTRATION: ModuleBoundary(
        name=ModuleBoundaryName.ORCHESTRATION,
        package="kki.orchestration",
        summary="Budget-, Zustands- und Triage-Kern fuer Build- und Laufzeitkoordination.",
        depends_on=(),
        runtime_hooks=("messaging", "recovery"),
        extension_contracts=("identity", "recovery"),
    ),
    ModuleBoundaryName.TELEMETRY: ModuleBoundary(
        name=ModuleBoundaryName.TELEMETRY,
        package="kki.telemetry",
        summary="Audit-, Diagnose- und Evidenzgrenzen fuer Beobachtung und Nachweis.",
        depends_on=(ModuleBoundaryName.ORCHESTRATION,),
        runtime_hooks=("telemetry",),
        extension_contracts=("telemetry",),
    ),
    ModuleBoundaryName.SECURITY: ModuleBoundary(
        name=ModuleBoundaryName.SECURITY,
        package="kki.security",
        summary="Policy-, Gate- und Quarantaeneschicht fuer kontrollierte Freigaben.",
        depends_on=(ModuleBoundaryName.TELEMETRY,),
        runtime_hooks=("approvals", "telemetry"),
        extension_contracts=("security",),
    ),
    ModuleBoundaryName.SHADOW: ModuleBoundary(
        name=ModuleBoundaryName.SHADOW,
        package="kki.shadow",
        summary="Preview-, Replay- und Parallelvalidierungsgrenze vor realer Wirkung.",
        depends_on=(ModuleBoundaryName.TELEMETRY, ModuleBoundaryName.SECURITY),
        runtime_hooks=("shadow", "telemetry"),
        extension_contracts=("shadow",),
    ),
    ModuleBoundaryName.ROLLOUT: ModuleBoundary(
        name=ModuleBoundaryName.ROLLOUT,
        package="kki.rollout",
        summary="Einfuehrungs- und Promotionspfad mit Gates fuer produktionsnahe Aktivierung.",
        depends_on=(
            ModuleBoundaryName.ORCHESTRATION,
            ModuleBoundaryName.SECURITY,
            ModuleBoundaryName.SHADOW,
        ),
        runtime_hooks=("approvals", "shadow", "telemetry"),
        extension_contracts=("rollout", "telemetry"),
    ),
    ModuleBoundaryName.RECOVERY: ModuleBoundary(
        name=ModuleBoundaryName.RECOVERY,
        package="kki.recovery",
        summary="Restart-, Ruecksprung- und Wiedereintrittspfad fuer Störungen und Migration.",
        depends_on=(ModuleBoundaryName.ORCHESTRATION, ModuleBoundaryName.ROLLOUT),
        runtime_hooks=("recovery", "telemetry"),
        extension_contracts=("recovery", "rollback"),
    ),
    ModuleBoundaryName.GOVERNANCE: ModuleBoundary(
        name=ModuleBoundaryName.GOVERNANCE,
        package="kki.governance",
        summary="Commitment-, Freigabe- und Human-in-the-loop-Grenze fuer kritische Entscheidungen.",
        depends_on=(
            ModuleBoundaryName.SECURITY,
            ModuleBoundaryName.ROLLOUT,
            ModuleBoundaryName.RECOVERY,
        ),
        runtime_hooks=("approvals", "telemetry", "recovery"),
        extension_contracts=("identity", "security", "telemetry"),
    ),
}


def module_boundaries() -> tuple[ModuleBoundary, ...]:
    """Return the canonical build-phase boundary definitions in dependency order."""

    return tuple(_BOUNDARIES[name] for name in ModuleBoundaryName)


def module_boundary(name: ModuleBoundaryName | str) -> ModuleBoundary:
    """Return a single boundary definition by enum or string name."""

    boundary_name = name if isinstance(name, ModuleBoundaryName) else ModuleBoundaryName(name)
    return _BOUNDARIES[boundary_name]


def module_dependency_graph() -> dict[str, tuple[str, ...]]:
    """Expose boundary dependencies in a serialization-friendly form."""

    return {
        boundary.name.value: tuple(dependency.value for dependency in boundary.depends_on)
        for boundary in module_boundaries()
    }
