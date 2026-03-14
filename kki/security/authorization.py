"""Authorization primitives for identities, roles, and bounded delegation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from kki.message_protocols import MessageEnvelope, MessageKind
from kki.module_boundaries import ModuleBoundaryName, module_boundary


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _frozen_mapping(data: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(data or {}))


def _normalize_boundary(name: ModuleBoundaryName | str) -> ModuleBoundaryName:
    boundary_name = name if isinstance(name, ModuleBoundaryName) else ModuleBoundaryName(name)
    module_boundary(boundary_name)
    return boundary_name


def _normalize_boundaries(
    boundaries: tuple[ModuleBoundaryName | str, ...] | tuple[()] | None,
) -> tuple[ModuleBoundaryName, ...]:
    if not boundaries:
        return ()
    return tuple(_normalize_boundary(boundary) for boundary in boundaries)


def _normalize_message_kind(name: str) -> str:
    if name not in {
        MessageKind.COMMAND,
        MessageKind.EVENT,
        MessageKind.TRANSFER,
        MessageKind.EVIDENCE,
    }:
        raise ValueError("Unsupported message kind")
    return name


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class IdentityKind(str, Enum):
    """Canonical identity classes for the build-phase authorization layer."""

    MODULE = "module"
    RUNTIME = "runtime"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    TOOL = "tool"


class RoleName(str, Enum):
    """Canonical authorization roles for the build-phase package."""

    OBSERVER = "observer"
    EXECUTOR = "executor"
    GATEKEEPER = "gatekeeper"
    SUPERVISOR = "supervisor"


class TrustLevel(str, Enum):
    """Trust level assigned to an authorization identity."""

    RESTRICTED = "restricted"
    VERIFIED = "verified"
    PRIVILEGED = "privileged"
    EMERGENCY = "emergency"


class OperatingMode(str, Enum):
    """Runtime mode used when evaluating authorization rules."""

    NORMAL = "normal"
    QUARANTINE = "quarantine"
    RECOVERY = "recovery"
    EMERGENCY = "emergency"


class ActionName(str, Enum):
    """Canonical actions protected by the build-phase authorization layer."""

    OBSERVE = "observe"
    EXECUTE = "execute"
    APPROVE = "approve"
    QUARANTINE = "quarantine"
    RECOVER = "recover"
    OVERRIDE = "override"


_TRUST_ORDER = {
    TrustLevel.RESTRICTED: 0,
    TrustLevel.VERIFIED: 1,
    TrustLevel.PRIVILEGED: 2,
    TrustLevel.EMERGENCY: 3,
}


@dataclass(frozen=True)
class AuthorizationIdentity:
    """A bounded identity used for policy and gate decisions."""

    slug: str
    kind: IdentityKind
    role: RoleName
    trust_level: TrustLevel
    boundary_scope: tuple[ModuleBoundaryName | str, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "slug", _non_empty(self.slug, field_name="slug"))
        object.__setattr__(self, "boundary_scope", _normalize_boundaries(self.boundary_scope))
        object.__setattr__(self, "metadata", _frozen_mapping(self.metadata))

    def can_reach(self, boundary: ModuleBoundaryName | str) -> bool:
        boundary_name = _normalize_boundary(boundary)
        return not self.boundary_scope or boundary_name in self.boundary_scope

    def to_dict(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "kind": self.kind.value,
            "role": self.role.value,
            "trust_level": self.trust_level.value,
            "boundary_scope": tuple(boundary.value for boundary in self.boundary_scope),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PermissionRule:
    """Canonical permission rule for a role, boundary set, and operating modes."""

    action: ActionName
    role: RoleName
    boundaries: tuple[ModuleBoundaryName | str, ...]
    message_kinds: tuple[str, ...]
    operating_modes: tuple[OperatingMode, ...]
    minimum_trust: TrustLevel
    requires_evidence: bool = False
    requires_commitment: bool = False
    delegable: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "boundaries", _normalize_boundaries(self.boundaries))
        object.__setattr__(
            self,
            "message_kinds",
            tuple(_normalize_message_kind(kind) for kind in self.message_kinds),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "role": self.role.value,
            "boundaries": tuple(boundary.value for boundary in self.boundaries),
            "message_kinds": self.message_kinds,
            "operating_modes": tuple(mode.value for mode in self.operating_modes),
            "minimum_trust": self.minimum_trust.value,
            "requires_evidence": self.requires_evidence,
            "requires_commitment": self.requires_commitment,
            "delegable": self.delegable,
        }


@dataclass(frozen=True)
class DelegationGrant:
    """Bounded delegation that never upgrades into open-ended superuser power."""

    grantor_slug: str
    delegate_slug: str
    action: ActionName
    boundaries: tuple[ModuleBoundaryName | str, ...]
    operating_modes: tuple[OperatingMode, ...]
    expires_at: str
    justification: str
    message_kinds: tuple[str, ...] = (MessageKind.COMMAND,)

    def __post_init__(self) -> None:
        object.__setattr__(self, "grantor_slug", _non_empty(self.grantor_slug, field_name="grantor_slug"))
        object.__setattr__(self, "delegate_slug", _non_empty(self.delegate_slug, field_name="delegate_slug"))
        object.__setattr__(self, "boundaries", _normalize_boundaries(self.boundaries))
        object.__setattr__(
            self,
            "message_kinds",
            tuple(_normalize_message_kind(kind) for kind in self.message_kinds),
        )
        object.__setattr__(self, "expires_at", _non_empty(self.expires_at, field_name="expires_at"))
        _parse_timestamp(self.expires_at)
        object.__setattr__(self, "justification", _non_empty(self.justification, field_name="justification"))

    def is_active(
        self,
        *,
        delegate_slug: str,
        action: ActionName,
        boundary: ModuleBoundaryName,
        operating_mode: OperatingMode,
        message_kind: str,
        now: datetime | None = None,
    ) -> bool:
        if delegate_slug != self.delegate_slug or action != self.action:
            return False
        if boundary not in self.boundaries:
            return False
        if operating_mode not in self.operating_modes:
            return False
        if message_kind not in self.message_kinds:
            return False
        current_time = now or datetime.now(timezone.utc)
        return current_time <= _parse_timestamp(self.expires_at)

    def to_dict(self) -> dict[str, object]:
        return {
            "grantor_slug": self.grantor_slug,
            "delegate_slug": self.delegate_slug,
            "action": self.action.value,
            "boundaries": tuple(boundary.value for boundary in self.boundaries),
            "operating_modes": tuple(mode.value for mode in self.operating_modes),
            "message_kinds": self.message_kinds,
            "expires_at": self.expires_at,
            "justification": self.justification,
        }


@dataclass(frozen=True)
class AuthorizationDecision:
    """Explicit authorization result for a requested action."""

    allowed: bool
    reason: str
    action: ActionName
    boundary: ModuleBoundaryName
    operating_mode: OperatingMode
    principal_role: RoleName
    permission_source: str
    requires_evidence: bool
    requires_commitment: bool
    escalation_required: bool
    message_kind: str

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "action": self.action.value,
            "boundary": self.boundary.value,
            "operating_mode": self.operating_mode.value,
            "principal_role": self.principal_role.value,
            "permission_source": self.permission_source,
            "requires_evidence": self.requires_evidence,
            "requires_commitment": self.requires_commitment,
            "escalation_required": self.escalation_required,
            "message_kind": self.message_kind,
        }


_ALL_BOUNDARIES = tuple(ModuleBoundaryName)
_ALL_OPERATING_MODES = tuple(OperatingMode)

_PERMISSION_RULES: tuple[PermissionRule, ...] = (
    PermissionRule(
        action=ActionName.OBSERVE,
        role=RoleName.OBSERVER,
        boundaries=_ALL_BOUNDARIES,
        message_kinds=(MessageKind.EVENT, MessageKind.EVIDENCE),
        operating_modes=_ALL_OPERATING_MODES,
        minimum_trust=TrustLevel.RESTRICTED,
        delegable=True,
    ),
    PermissionRule(
        action=ActionName.EXECUTE,
        role=RoleName.EXECUTOR,
        boundaries=(
            ModuleBoundaryName.ORCHESTRATION,
            ModuleBoundaryName.TELEMETRY,
            ModuleBoundaryName.SHADOW,
            ModuleBoundaryName.ROLLOUT,
        ),
        message_kinds=(MessageKind.COMMAND, MessageKind.EVENT, MessageKind.TRANSFER),
        operating_modes=(OperatingMode.NORMAL, OperatingMode.QUARANTINE),
        minimum_trust=TrustLevel.VERIFIED,
        delegable=True,
    ),
    PermissionRule(
        action=ActionName.APPROVE,
        role=RoleName.GATEKEEPER,
        boundaries=(
            ModuleBoundaryName.SECURITY,
            ModuleBoundaryName.ROLLOUT,
            ModuleBoundaryName.GOVERNANCE,
        ),
        message_kinds=(MessageKind.COMMAND, MessageKind.EVIDENCE),
        operating_modes=(OperatingMode.NORMAL, OperatingMode.QUARANTINE, OperatingMode.RECOVERY),
        minimum_trust=TrustLevel.VERIFIED,
        requires_evidence=True,
    ),
    PermissionRule(
        action=ActionName.QUARANTINE,
        role=RoleName.GATEKEEPER,
        boundaries=(
            ModuleBoundaryName.SECURITY,
            ModuleBoundaryName.SHADOW,
            ModuleBoundaryName.ROLLOUT,
        ),
        message_kinds=(MessageKind.COMMAND, MessageKind.EVIDENCE),
        operating_modes=(OperatingMode.NORMAL, OperatingMode.QUARANTINE, OperatingMode.RECOVERY),
        minimum_trust=TrustLevel.PRIVILEGED,
        requires_evidence=True,
    ),
    PermissionRule(
        action=ActionName.RECOVER,
        role=RoleName.SUPERVISOR,
        boundaries=(ModuleBoundaryName.RECOVERY, ModuleBoundaryName.ROLLOUT),
        message_kinds=(MessageKind.COMMAND, MessageKind.TRANSFER, MessageKind.EVIDENCE),
        operating_modes=(OperatingMode.RECOVERY, OperatingMode.EMERGENCY),
        minimum_trust=TrustLevel.PRIVILEGED,
        requires_evidence=True,
    ),
    PermissionRule(
        action=ActionName.OVERRIDE,
        role=RoleName.SUPERVISOR,
        boundaries=(
            ModuleBoundaryName.SECURITY,
            ModuleBoundaryName.GOVERNANCE,
            ModuleBoundaryName.RECOVERY,
        ),
        message_kinds=(MessageKind.COMMAND, MessageKind.EVIDENCE),
        operating_modes=(OperatingMode.EMERGENCY,),
        minimum_trust=TrustLevel.EMERGENCY,
        requires_evidence=True,
        requires_commitment=True,
    ),
)


def permission_catalog() -> tuple[PermissionRule, ...]:
    """Return the canonical permission rules for the build-phase package."""

    return _PERMISSION_RULES


def role_permissions(role: RoleName | str) -> tuple[PermissionRule, ...]:
    """Return the rule set available to a single canonical role."""

    role_name = role if isinstance(role, RoleName) else RoleName(role)
    rules = [rule for rule in _PERMISSION_RULES if rule.role == role_name]
    if role_name is not RoleName.OBSERVER:
        rules.append(_PERMISSION_RULES[0])
    return tuple(rules)


def _default_message_kind(action: ActionName) -> str:
    if action is ActionName.OBSERVE:
        return MessageKind.EVENT
    return MessageKind.COMMAND


def _identity_matches_rule(identity: AuthorizationIdentity, rule: PermissionRule) -> bool:
    if rule.role == RoleName.OBSERVER:
        return identity.role in tuple(RoleName)
    return identity.role == rule.role


def _trust_satisfies(current: TrustLevel, minimum: TrustLevel) -> bool:
    return _TRUST_ORDER[current] >= _TRUST_ORDER[minimum]


def authorize_action(
    identity: AuthorizationIdentity,
    *,
    action: ActionName | str,
    boundary: ModuleBoundaryName | str,
    operating_mode: OperatingMode | str = OperatingMode.NORMAL,
    message: MessageEnvelope | None = None,
    message_kind: str | None = None,
    evidence_ref: str | None = None,
    commitment_ref: str | None = None,
    delegation: DelegationGrant | None = None,
) -> AuthorizationDecision:
    """Evaluate whether an identity may execute an action in a given context."""

    requested_action = action if isinstance(action, ActionName) else ActionName(action)
    boundary_name = _normalize_boundary(boundary)
    mode = operating_mode if isinstance(operating_mode, OperatingMode) else OperatingMode(operating_mode)
    effective_message_kind = _normalize_message_kind(
        message.kind if message is not None else (message_kind or _default_message_kind(requested_action))
    )

    if not identity.can_reach(boundary_name):
        return AuthorizationDecision(
            allowed=False,
            reason="identity scope does not cover the requested boundary",
            action=requested_action,
            boundary=boundary_name,
            operating_mode=mode,
            principal_role=identity.role,
            permission_source="scope",
            requires_evidence=False,
            requires_commitment=False,
            escalation_required=False,
            message_kind=effective_message_kind,
        )

    for rule in role_permissions(identity.role):
        if rule.action != requested_action:
            continue
        if not _identity_matches_rule(identity, rule):
            continue
        if boundary_name not in rule.boundaries:
            continue
        if mode not in rule.operating_modes:
            continue
        if effective_message_kind not in rule.message_kinds:
            continue
        if not _trust_satisfies(identity.trust_level, rule.minimum_trust):
            return AuthorizationDecision(
                allowed=False,
                reason="identity trust level is too low for the requested action",
                action=requested_action,
                boundary=boundary_name,
                operating_mode=mode,
                principal_role=identity.role,
                permission_source="trust",
                requires_evidence=rule.requires_evidence,
                requires_commitment=rule.requires_commitment,
                escalation_required=rule.requires_commitment or mode is OperatingMode.EMERGENCY,
                message_kind=effective_message_kind,
            )
        if rule.requires_evidence and not evidence_ref:
            return AuthorizationDecision(
                allowed=False,
                reason="action requires evidence binding",
                action=requested_action,
                boundary=boundary_name,
                operating_mode=mode,
                principal_role=identity.role,
                permission_source="evidence",
                requires_evidence=True,
                requires_commitment=rule.requires_commitment,
                escalation_required=rule.requires_commitment or mode is OperatingMode.EMERGENCY,
                message_kind=effective_message_kind,
            )
        if rule.requires_commitment and not commitment_ref:
            return AuthorizationDecision(
                allowed=False,
                reason="action requires commitment binding",
                action=requested_action,
                boundary=boundary_name,
                operating_mode=mode,
                principal_role=identity.role,
                permission_source="commitment",
                requires_evidence=rule.requires_evidence,
                requires_commitment=True,
                escalation_required=True,
                message_kind=effective_message_kind,
            )
        return AuthorizationDecision(
            allowed=True,
            reason="action is allowed by canonical role policy",
            action=requested_action,
            boundary=boundary_name,
            operating_mode=mode,
            principal_role=identity.role,
            permission_source="role-policy",
            requires_evidence=rule.requires_evidence,
            requires_commitment=rule.requires_commitment,
            escalation_required=rule.requires_commitment or mode is OperatingMode.EMERGENCY,
            message_kind=effective_message_kind,
        )

    if delegation is not None:
        delegable_rules = tuple(
            rule
            for rule in _PERMISSION_RULES
            if rule.action == requested_action and rule.delegable and boundary_name in rule.boundaries
        )
        for rule in delegable_rules:
            if not delegation.is_active(
                delegate_slug=identity.slug,
                action=requested_action,
                boundary=boundary_name,
                operating_mode=mode,
                message_kind=effective_message_kind,
            ):
                continue
            return AuthorizationDecision(
                allowed=True,
                reason="action is allowed by bounded delegation",
                action=requested_action,
                boundary=boundary_name,
                operating_mode=mode,
                principal_role=identity.role,
                permission_source="delegation",
                requires_evidence=rule.requires_evidence,
                requires_commitment=rule.requires_commitment,
                escalation_required=False,
                message_kind=effective_message_kind,
            )

    return AuthorizationDecision(
        allowed=False,
        reason="no canonical permission rule matches the requested action",
        action=requested_action,
        boundary=boundary_name,
        operating_mode=mode,
        principal_role=identity.role,
        permission_source="role-policy",
        requires_evidence=False,
        requires_commitment=False,
        escalation_required=mode is OperatingMode.EMERGENCY,
        message_kind=effective_message_kind,
    )
