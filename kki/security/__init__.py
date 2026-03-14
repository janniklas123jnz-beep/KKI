"""Security boundary for gates, policies, and quarantine decisions."""

from kki.module_boundaries import ModuleBoundary, module_boundary
from kki.security.authorization import (
    ActionName,
    AuthorizationDecision,
    AuthorizationIdentity,
    DelegationGrant,
    IdentityKind,
    OperatingMode,
    PermissionRule,
    RoleName,
    TrustLevel,
    authorize_action,
    permission_catalog,
    role_permissions,
)

BOUNDARY: ModuleBoundary = module_boundary("security")

__all__ = [
    "ActionName",
    "AuthorizationDecision",
    "AuthorizationIdentity",
    "BOUNDARY",
    "DelegationGrant",
    "IdentityKind",
    "OperatingMode",
    "PermissionRule",
    "RoleName",
    "TrustLevel",
    "authorize_action",
    "permission_catalog",
    "role_permissions",
]
