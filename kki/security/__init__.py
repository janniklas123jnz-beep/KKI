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
from kki.security.config_loader import (
    ArtifactKind,
    ArtifactScope,
    ControlArtifact,
    LoadedControlPlane,
    ValidationStep,
    authorize_artifact,
    load_control_plane,
)

BOUNDARY: ModuleBoundary = module_boundary("security")

__all__ = [
    "ActionName",
    "ArtifactKind",
    "ArtifactScope",
    "AuthorizationDecision",
    "AuthorizationIdentity",
    "BOUNDARY",
    "ControlArtifact",
    "DelegationGrant",
    "IdentityKind",
    "LoadedControlPlane",
    "OperatingMode",
    "PermissionRule",
    "RoleName",
    "TrustLevel",
    "ValidationStep",
    "authorize_action",
    "authorize_artifact",
    "load_control_plane",
    "permission_catalog",
    "role_permissions",
]
