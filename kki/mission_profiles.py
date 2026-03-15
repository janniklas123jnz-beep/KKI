"""Typed mission profiles for deterministic operational runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .governance import HumanDecision
from .module_boundaries import ModuleBoundaryName, module_boundary
from .orchestration import WorkPriority
from .runtime_dna import RuntimeStage
from .security import RoleName


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _clamp01(value: float, *, field_name: str) -> float:
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")
    return normalized


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


class MissionScenario(str, Enum):
    """Canonical operational mission scenarios."""

    ROUTINE = "routine"
    CUTOVER = "cutover"
    HARDENING = "hardening"
    RECOVERY_DRILL = "recovery-drill"


@dataclass(frozen=True)
class MissionPolicy:
    """Typed policy envelope applied to a mission profile."""

    resource_budget: float = 0.82
    recovery_reserve: float = 0.2
    drift_threshold: float = 0.05
    promotion_gate: str = "hold-until-shadow-green"

    def __post_init__(self) -> None:
        object.__setattr__(self, "resource_budget", _clamp01(self.resource_budget, field_name="resource_budget"))
        object.__setattr__(self, "recovery_reserve", _clamp01(self.recovery_reserve, field_name="recovery_reserve"))
        object.__setattr__(self, "drift_threshold", _clamp01(self.drift_threshold, field_name="drift_threshold"))
        object.__setattr__(self, "promotion_gate", _non_empty(self.promotion_gate, field_name="promotion_gate"))
        if self.recovery_reserve >= self.resource_budget:
            raise ValueError("recovery_reserve must stay below resource_budget")

    def to_dict(self) -> dict[str, object]:
        return {
            "resource_budget": self.resource_budget,
            "recovery_reserve": self.recovery_reserve,
            "drift_threshold": self.drift_threshold,
            "promotion_gate": self.promotion_gate,
        }


@dataclass(frozen=True)
class MissionProfile:
    """Reusable mission profile for deterministic integrated operations runs."""

    mission_ref: str
    title: str
    scenario: MissionScenario
    runtime_stage: RuntimeStage
    runtime_profile: str
    target_boundary: ModuleBoundaryName
    work_priority: WorkPriority = WorkPriority.HIGH
    budget_share: float = 0.12
    observed_budget: float | None = None
    governance_decision: HumanDecision = HumanDecision.APPROVE
    available_roles: tuple[RoleName, ...] = (RoleName.EXECUTOR,)
    policy: MissionPolicy = field(default_factory=MissionPolicy)
    labels: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "mission_ref", _non_empty(self.mission_ref, field_name="mission_ref"))
        object.__setattr__(self, "title", _non_empty(self.title, field_name="title"))
        object.__setattr__(self, "runtime_profile", _non_empty(self.runtime_profile, field_name="runtime_profile"))
        object.__setattr__(self, "budget_share", _clamp01(self.budget_share, field_name="budget_share"))
        if self.observed_budget is not None:
            object.__setattr__(self, "observed_budget", _clamp01(self.observed_budget, field_name="observed_budget"))
        module_boundary(self.target_boundary)
        if not self.available_roles:
            raise ValueError("available_roles must not be empty")
        object.__setattr__(
            self,
            "available_roles",
            tuple(role if isinstance(role, RoleName) else RoleName(role) for role in self.available_roles),
        )
        object.__setattr__(self, "labels", _frozen_mapping(self.labels))

    @property
    def effective_observed_budget(self) -> float:
        return self.budget_share if self.observed_budget is None else self.observed_budget

    def to_dict(self) -> dict[str, object]:
        return {
            "mission_ref": self.mission_ref,
            "title": self.title,
            "scenario": self.scenario.value,
            "runtime_stage": self.runtime_stage.value,
            "runtime_profile": self.runtime_profile,
            "target_boundary": self.target_boundary.value,
            "work_priority": self.work_priority.value,
            "budget_share": self.budget_share,
            "observed_budget": self.observed_budget,
            "effective_observed_budget": self.effective_observed_budget,
            "governance_decision": self.governance_decision.value,
            "available_roles": [role.value for role in self.available_roles],
            "policy": self.policy.to_dict(),
            "labels": dict(self.labels),
        }


def mission_profile_catalog() -> tuple[str, ...]:
    """Return the canonical mission profile preset names."""

    return ("pilot-cutover", "shadow-hardening", "recovery-drill")


def mission_profile_for_name(name: str) -> MissionProfile:
    """Resolve a named mission profile preset."""

    presets = {
        "pilot-cutover": MissionProfile(
            mission_ref="pilot-cutover",
            title="pilot cutover campaign",
            scenario=MissionScenario.CUTOVER,
            runtime_stage=RuntimeStage.PILOT,
            runtime_profile="pilot-runtime-dna",
            target_boundary=ModuleBoundaryName.ROLLOUT,
            work_priority=WorkPriority.HIGH,
            budget_share=0.12,
            observed_budget=0.12,
            available_roles=(RoleName.EXECUTOR,),
            policy=MissionPolicy(
                resource_budget=0.82,
                recovery_reserve=0.2,
                drift_threshold=0.05,
                promotion_gate="hold-until-shadow-green",
            ),
            labels={"campaign": "pilot", "mission_class": "cutover"},
        ),
        "shadow-hardening": MissionProfile(
            mission_ref="shadow-hardening",
            title="shadow hardening pass",
            scenario=MissionScenario.HARDENING,
            runtime_stage=RuntimeStage.SHADOW,
            runtime_profile="resilient-runtime-dna",
            target_boundary=ModuleBoundaryName.ROLLOUT,
            work_priority=WorkPriority.HIGH,
            budget_share=0.1,
            observed_budget=0.09,
            available_roles=(RoleName.EXECUTOR,),
            policy=MissionPolicy(
                resource_budget=0.8,
                recovery_reserve=0.22,
                drift_threshold=0.03,
                promotion_gate="guarded-shadow-promotion",
            ),
            labels={"campaign": "shadow", "mission_class": "hardening"},
        ),
        "recovery-drill": MissionProfile(
            mission_ref="recovery-drill",
            title="recovery drill run",
            scenario=MissionScenario.RECOVERY_DRILL,
            runtime_stage=RuntimeStage.PILOT,
            runtime_profile="resilient-runtime-dna",
            target_boundary=ModuleBoundaryName.ROLLOUT,
            work_priority=WorkPriority.CRITICAL,
            budget_share=0.16,
            observed_budget=0.15,
            available_roles=(RoleName.EXECUTOR,),
            policy=MissionPolicy(
                resource_budget=0.84,
                recovery_reserve=0.24,
                drift_threshold=0.04,
                promotion_gate="guarded-reentry",
            ),
            labels={"campaign": "recovery", "mission_class": "drill"},
        ),
    }
    try:
        return presets[name]
    except KeyError as exc:
        raise ValueError(f"Unknown mission profile: {name!r}") from exc
