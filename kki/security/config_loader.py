"""Config and policy loading primitives for the build-phase control plane."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.module_boundaries import ModuleBoundaryName, module_boundary
from kki.runtime_dna import RuntimeStage
from kki.security.authorization import (
    ActionName,
    AuthorizationDecision,
    AuthorizationIdentity,
    OperatingMode,
    RoleName,
    authorize_action,
)


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


def _normalize_boundary(value: ModuleBoundaryName | str | None) -> ModuleBoundaryName | None:
    if value is None:
        return None
    boundary = value if isinstance(value, ModuleBoundaryName) else ModuleBoundaryName(value)
    module_boundary(boundary)
    return boundary


def _normalize_role(value: RoleName | str | None) -> RoleName | None:
    if value is None:
        return None
    return value if isinstance(value, RoleName) else RoleName(value)


class ArtifactKind(str, Enum):
    """Canonical control artifact classes for config and policy distribution."""

    BASE_CONFIG = "base-config"
    POLICY = "policy"
    FEATURE_FLAG = "feature-flag"
    EMERGENCY_OVERRIDE = "emergency-override"


class ArtifactScope(str, Enum):
    """Distribution scopes for control-plane artifacts."""

    GLOBAL = "global"
    STAGE = "stage"
    BOUNDARY = "boundary"
    ROLE = "role"


class ValidationStep(str, Enum):
    """Validation gates for control-plane artifacts before activation."""

    STATIC = "static"
    CONSISTENCY = "consistency"
    SHADOW = "shadow"


_SCOPE_PRECEDENCE = {
    ArtifactScope.GLOBAL: 0,
    ArtifactScope.STAGE: 1,
    ArtifactScope.BOUNDARY: 2,
    ArtifactScope.ROLE: 3,
}


@dataclass(frozen=True)
class ControlArtifact:
    """Versioned control-plane artifact with explicit scope and rollback hooks."""

    artifact_id: str
    kind: ArtifactKind
    version: str
    scope: ArtifactScope
    payload: Mapping[str, object]
    validations: tuple[ValidationStep | str, ...] = (
        ValidationStep.STATIC,
        ValidationStep.CONSISTENCY,
    )
    runtime_stage: RuntimeStage | None = None
    boundary: ModuleBoundaryName | str | None = None
    role_scope: RoleName | str | None = None
    evidence_ref: str | None = None
    commitment_ref: str | None = None
    rollback_version: str | None = None
    critical: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", _non_empty(self.artifact_id, field_name="artifact_id"))
        object.__setattr__(self, "version", _non_empty(self.version, field_name="version"))
        object.__setattr__(
            self,
            "validations",
            tuple(
                step if isinstance(step, ValidationStep) else ValidationStep(step)
                for step in self.validations
            ),
        )
        object.__setattr__(self, "payload", _frozen_mapping(self.payload))
        object.__setattr__(self, "boundary", _normalize_boundary(self.boundary))
        object.__setattr__(self, "role_scope", _normalize_role(self.role_scope))
        if self.evidence_ref is not None:
            object.__setattr__(self, "evidence_ref", _non_empty(self.evidence_ref, field_name="evidence_ref"))
        if self.commitment_ref is not None:
            object.__setattr__(self, "commitment_ref", _non_empty(self.commitment_ref, field_name="commitment_ref"))
        if self.rollback_version is not None:
            object.__setattr__(
                self,
                "rollback_version",
                _non_empty(self.rollback_version, field_name="rollback_version"),
            )
        self._validate_scope()
        self._validate_requirements()

    def _validate_scope(self) -> None:
        if self.scope is ArtifactScope.GLOBAL:
            if self.runtime_stage is not None or self.boundary is not None or self.role_scope is not None:
                raise ValueError("global artifacts must not set runtime_stage, boundary, or role_scope")
        elif self.scope is ArtifactScope.STAGE:
            if self.runtime_stage is None or self.boundary is not None or self.role_scope is not None:
                raise ValueError("stage artifacts must set runtime_stage only")
        elif self.scope is ArtifactScope.BOUNDARY:
            if self.boundary is None or self.role_scope is not None:
                raise ValueError("boundary artifacts must set boundary and must not set role_scope")
        elif self.scope is ArtifactScope.ROLE:
            if self.role_scope is None:
                raise ValueError("role artifacts must set role_scope")

    def _validate_requirements(self) -> None:
        validation_set = set(self.validations)
        if ValidationStep.STATIC not in validation_set or ValidationStep.CONSISTENCY not in validation_set:
            raise ValueError("artifacts must include static and consistency validation")
        if self.kind is ArtifactKind.POLICY and self.evidence_ref is None:
            raise ValueError("policy artifacts require evidence_ref")
        if self.kind is ArtifactKind.EMERGENCY_OVERRIDE:
            if self.evidence_ref is None or self.commitment_ref is None:
                raise ValueError("emergency overrides require evidence_ref and commitment_ref")
            if self.rollback_version is None:
                raise ValueError("emergency overrides require rollback_version")
        if self.scope in {ArtifactScope.STAGE, ArtifactScope.BOUNDARY, ArtifactScope.ROLE}:
            if self.runtime_stage in {RuntimeStage.PILOT, RuntimeStage.PRODUCTION} and ValidationStep.SHADOW not in validation_set:
                raise ValueError("pilot and production scoped artifacts require shadow validation")

    @property
    def precedence(self) -> int:
        return _SCOPE_PRECEDENCE[self.scope] + (10 if self.kind is ArtifactKind.EMERGENCY_OVERRIDE else 0)

    def applies_to(
        self,
        *,
        runtime_stage: RuntimeStage,
        boundary: ModuleBoundaryName | str | None = None,
        role_scope: RoleName | str | None = None,
        include_emergency_overrides: bool = False,
    ) -> bool:
        boundary_name = _normalize_boundary(boundary)
        role_name = _normalize_role(role_scope)
        if self.kind is ArtifactKind.EMERGENCY_OVERRIDE and not include_emergency_overrides:
            return False
        if self.scope is ArtifactScope.GLOBAL:
            return True
        if self.scope is ArtifactScope.STAGE:
            return self.runtime_stage == runtime_stage
        if self.scope is ArtifactScope.BOUNDARY:
            return self.boundary == boundary_name and (
                self.runtime_stage is None or self.runtime_stage == runtime_stage
            )
        if self.scope is ArtifactScope.ROLE:
            role_matches = self.role_scope == role_name
            stage_matches = self.runtime_stage is None or self.runtime_stage == runtime_stage
            boundary_matches = self.boundary is None or self.boundary == boundary_name
            return role_matches and stage_matches and boundary_matches
        return False

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "kind": self.kind.value,
            "version": self.version,
            "scope": self.scope.value,
            "payload": dict(self.payload),
            "validations": tuple(step.value for step in self.validations),
            "runtime_stage": self.runtime_stage.value if self.runtime_stage else None,
            "boundary": self.boundary.value if self.boundary else None,
            "role_scope": self.role_scope.value if self.role_scope else None,
            "evidence_ref": self.evidence_ref,
            "commitment_ref": self.commitment_ref,
            "rollback_version": self.rollback_version,
            "critical": self.critical,
        }


@dataclass(frozen=True)
class LoadedControlPlane:
    """Resolved control-plane view for a specific runtime, boundary, and role."""

    runtime_stage: RuntimeStage
    effective_payload: Mapping[str, object]
    applied_artifacts: tuple[ControlArtifact, ...]
    rollback_chain: tuple[str, ...]
    boundary: ModuleBoundaryName | None = None
    role_scope: RoleName | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "effective_payload", _frozen_mapping(self.effective_payload))

    def to_dict(self) -> dict[str, object]:
        return {
            "runtime_stage": self.runtime_stage.value,
            "boundary": self.boundary.value if self.boundary else None,
            "role_scope": self.role_scope.value if self.role_scope else None,
            "effective_payload": dict(self.effective_payload),
            "applied_artifacts": [artifact.to_dict() for artifact in self.applied_artifacts],
            "rollback_chain": list(self.rollback_chain),
        }


def authorize_artifact(
    identity: AuthorizationIdentity,
    artifact: ControlArtifact,
    *,
    operating_mode: OperatingMode | str = OperatingMode.NORMAL,
) -> AuthorizationDecision:
    """Authorize distribution of a control artifact through the canonical role model."""

    action = {
        ArtifactKind.BASE_CONFIG: ActionName.EXECUTE,
        ArtifactKind.POLICY: ActionName.APPROVE,
        ArtifactKind.FEATURE_FLAG: ActionName.APPROVE if artifact.critical else ActionName.EXECUTE,
        ArtifactKind.EMERGENCY_OVERRIDE: ActionName.OVERRIDE,
    }[artifact.kind]
    boundary = artifact.boundary or ModuleBoundaryName.SECURITY
    return authorize_action(
        identity,
        action=action,
        boundary=boundary,
        operating_mode=operating_mode,
        evidence_ref=artifact.evidence_ref,
        commitment_ref=artifact.commitment_ref,
    )


def load_control_plane(
    artifacts: tuple[ControlArtifact, ...] | list[ControlArtifact],
    *,
    runtime_stage: RuntimeStage,
    boundary: ModuleBoundaryName | str | None = None,
    role_scope: RoleName | str | None = None,
    include_emergency_overrides: bool = False,
) -> LoadedControlPlane:
    """Resolve a consistent control-plane view for a specific runtime context."""

    boundary_name = _normalize_boundary(boundary)
    role_name = _normalize_role(role_scope)
    applicable = tuple(
        artifact
        for artifact in artifacts
        if artifact.applies_to(
            runtime_stage=runtime_stage,
            boundary=boundary_name,
            role_scope=role_name,
            include_emergency_overrides=include_emergency_overrides,
        )
    )
    seen_versions: dict[tuple[str, ArtifactScope], str] = {}
    for artifact in applicable:
        key = (artifact.artifact_id, artifact.scope)
        existing = seen_versions.get(key)
        if existing is not None and existing != artifact.version:
            raise ValueError(f"inconsistent distribution for artifact {artifact.artifact_id!r}")
        seen_versions[key] = artifact.version
    ordered = tuple(sorted(applicable, key=lambda artifact: (artifact.precedence, artifact.artifact_id, artifact.version)))
    effective_payload: dict[str, object] = {}
    rollback_chain: list[str] = []
    for artifact in ordered:
        effective_payload.update(dict(artifact.payload))
        if artifact.rollback_version is not None:
            rollback_chain.append(f"{artifact.artifact_id}:{artifact.rollback_version}")
    return LoadedControlPlane(
        runtime_stage=runtime_stage,
        boundary=boundary_name,
        role_scope=role_name,
        effective_payload=effective_payload,
        applied_artifacts=ordered,
        rollback_chain=tuple(rollback_chain),
    )
