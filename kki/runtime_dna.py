"""Runtime-DNA foundation primitives for the build phase."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping


def _env_flag(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return float(raw_value)


def _env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _clamp01(value: float, *, field_name: str) -> float:
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {normalized!r}")
    return normalized


class RuntimeStage(str, Enum):
    """Deployment stage for the first build-phase runtime foundation."""

    LAB = "lab"
    SHADOW = "shadow"
    PILOT = "pilot"
    PRODUCTION = "production"

    @classmethod
    def parse(cls, raw_value: str) -> "RuntimeStage":
        normalized = raw_value.strip().lower()
        for stage in cls:
            if stage.value == normalized:
                return stage
        raise ValueError(f"Unsupported runtime stage: {raw_value!r}")


@dataclass(frozen=True)
class RuntimeIdentity:
    """Stable identity anchors for a concrete runtime DNA profile."""

    system: str
    profile: str
    version: str
    stage: RuntimeStage

    def __post_init__(self) -> None:
        if not self.system.strip():
            raise ValueError("system must not be empty")
        if not self.profile.strip():
            raise ValueError("profile must not be empty")
        if not self.version.strip():
            raise ValueError("version must not be empty")

    @property
    def slug(self) -> str:
        return f"{self.system}-{self.profile}-{self.stage.value}"


@dataclass(frozen=True)
class RuntimeHooks:
    """Feature hooks that later build-phase modules can attach to."""

    telemetry: bool = True
    approvals: bool = True
    messaging: bool = True
    recovery: bool = True
    shadow: bool = True

    def enabled(self) -> tuple[str, ...]:
        return tuple(name for name, active in asdict(self).items() if active)


@dataclass(frozen=True)
class RuntimeThresholds:
    """Foundational limits and pacing knobs for the build-phase runtime."""

    resource_budget: float = 0.78
    resource_share_factor: float = 0.26
    recovery_reserve: float = 0.18
    approval_window: int = 2
    meta_update_interval: int = 5

    def __post_init__(self) -> None:
        budget = _clamp01(self.resource_budget, field_name="resource_budget")
        share_factor = _clamp01(self.resource_share_factor, field_name="resource_share_factor")
        reserve = _clamp01(self.recovery_reserve, field_name="recovery_reserve")
        if reserve >= budget:
            raise ValueError("recovery_reserve must stay below resource_budget")
        if self.approval_window < 1:
            raise ValueError("approval_window must be >= 1")
        if self.meta_update_interval < 1:
            raise ValueError("meta_update_interval must be >= 1")

        object.__setattr__(self, "resource_budget", budget)
        object.__setattr__(self, "resource_share_factor", share_factor)
        object.__setattr__(self, "recovery_reserve", reserve)


@dataclass(frozen=True)
class RuntimeDNA:
    """Validated runtime DNA contract for the first build-phase foundation."""

    identity: RuntimeIdentity
    hooks: RuntimeHooks = field(default_factory=RuntimeHooks)
    thresholds: RuntimeThresholds = field(default_factory=RuntimeThresholds)
    extension_contracts: tuple[str, ...] = (
        "identity",
        "telemetry",
        "security",
        "shadow",
        "recovery",
    )
    invariants: tuple[str, ...] = (
        "no-unguarded-external-coupling",
        "audit-before-cutover",
        "recovery-before-live",
    )
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        cleaned_contracts = tuple(contract.strip() for contract in self.extension_contracts if contract.strip())
        cleaned_invariants = tuple(invariant.strip() for invariant in self.invariants if invariant.strip())
        if not cleaned_contracts:
            raise ValueError("extension_contracts must not be empty")
        if not cleaned_invariants:
            raise ValueError("invariants must not be empty")

        frozen_metadata = MappingProxyType(dict(self.metadata))
        object.__setattr__(self, "extension_contracts", cleaned_contracts)
        object.__setattr__(self, "invariants", cleaned_invariants)
        object.__setattr__(self, "metadata", frozen_metadata)

    def has_hook(self, name: str) -> bool:
        return name in self.hooks.enabled()

    def to_dict(self) -> dict[str, object]:
        return {
            "identity": {
                "system": self.identity.system,
                "profile": self.identity.profile,
                "version": self.identity.version,
                "stage": self.identity.stage.value,
                "slug": self.identity.slug,
            },
            "enabled_hooks": list(self.hooks.enabled()),
            "thresholds": asdict(self.thresholds),
            "extension_contracts": list(self.extension_contracts),
            "invariants": list(self.invariants),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RuntimePreset:
    """Typed preset container for named runtime DNA profiles."""

    hooks: RuntimeHooks
    thresholds: RuntimeThresholds
    extension_contracts: tuple[str, ...]


def runtime_dna_for_profile(
    profile: str = "balanced-runtime-dna",
    *,
    stage: RuntimeStage = RuntimeStage.LAB,
    version: str = "0.1.0",
) -> RuntimeDNA:
    """Build a validated runtime DNA object from a named preset."""

    presets: dict[str, RuntimePreset] = {
        "balanced-runtime-dna": RuntimePreset(
            hooks=RuntimeHooks(),
            thresholds=RuntimeThresholds(),
            extension_contracts=(
                "identity",
                "telemetry",
                "security",
                "shadow",
                "recovery",
            ),
        ),
        "pilot-runtime-dna": RuntimePreset(
            hooks=RuntimeHooks(),
            thresholds=RuntimeThresholds(
                resource_budget=0.8,
                resource_share_factor=0.28,
                recovery_reserve=0.2,
                approval_window=2,
                meta_update_interval=4,
            ),
            extension_contracts=(
                "identity",
                "telemetry",
                "security",
                "shadow",
                "recovery",
                "rollout",
            ),
        ),
        "resilient-runtime-dna": RuntimePreset(
            hooks=RuntimeHooks(),
            thresholds=RuntimeThresholds(
                resource_budget=0.82,
                resource_share_factor=0.3,
                recovery_reserve=0.24,
                approval_window=3,
                meta_update_interval=4,
            ),
            extension_contracts=(
                "identity",
                "telemetry",
                "security",
                "shadow",
                "recovery",
                "rollback",
            ),
        ),
    }
    try:
        preset = presets[profile]
    except KeyError as exc:
        raise ValueError(f"Unknown runtime DNA profile: {profile!r}") from exc

    return RuntimeDNA(
        identity=RuntimeIdentity(system="kki", profile=profile, version=version, stage=stage),
        hooks=preset.hooks,
        thresholds=preset.thresholds,
        extension_contracts=preset.extension_contracts,
        metadata={"foundation_issue": "121"},
    )


def runtime_dna_from_env() -> RuntimeDNA:
    """Load the initial build-phase runtime DNA from environment overrides."""

    profile = os.getenv("KKI_RUNTIME_PROFILE", "balanced-runtime-dna")
    stage = RuntimeStage.parse(os.getenv("KKI_RUNTIME_STAGE", RuntimeStage.LAB.value))
    version = os.getenv("KKI_RUNTIME_VERSION", "0.1.0")

    base = runtime_dna_for_profile(profile, stage=stage, version=version)
    thresholds = RuntimeThresholds(
        resource_budget=_env_float("KKI_RUNTIME_RESOURCE_BUDGET", base.thresholds.resource_budget),
        resource_share_factor=_env_float(
            "KKI_RUNTIME_RESOURCE_SHARE_FACTOR", base.thresholds.resource_share_factor
        ),
        recovery_reserve=_env_float("KKI_RUNTIME_RECOVERY_RESERVE", base.thresholds.recovery_reserve),
        approval_window=_env_int("KKI_RUNTIME_APPROVAL_WINDOW", base.thresholds.approval_window),
        meta_update_interval=_env_int(
            "KKI_RUNTIME_META_UPDATE_INTERVAL", base.thresholds.meta_update_interval
        ),
    )
    hooks = RuntimeHooks(
        telemetry=_env_flag("KKI_RUNTIME_ENABLE_TELEMETRY", base.hooks.telemetry),
        approvals=_env_flag("KKI_RUNTIME_ENABLE_APPROVALS", base.hooks.approvals),
        messaging=_env_flag("KKI_RUNTIME_ENABLE_MESSAGING", base.hooks.messaging),
        recovery=_env_flag("KKI_RUNTIME_ENABLE_RECOVERY", base.hooks.recovery),
        shadow=_env_flag("KKI_RUNTIME_ENABLE_SHADOW", base.hooks.shadow),
    )

    metadata = dict(base.metadata)
    owner = os.getenv("KKI_RUNTIME_OWNER")
    if owner:
        metadata["owner"] = owner

    return RuntimeDNA(
        identity=base.identity,
        hooks=hooks,
        thresholds=thresholds,
        extension_contracts=base.extension_contracts,
        invariants=base.invariants,
        metadata=metadata,
    )
